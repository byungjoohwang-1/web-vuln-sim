/**
 * 금융 서버 진단 실습 엔진 — 모의 리눅스 호스트 (SRV-*)
 *
 * 왜 만들었나
 * -----------
 * 전자금융 서버 점검 항목은 지금까지 "읽고 양호/취약을 고르는" 체크리스트였다.
 * 실무에서 하는 일은 그게 아니라 **서버에 붙어 설정 파일을 열어 보고, 그 내용으로 판정하고,
 * 고친 뒤 다시 확인하는 것**이다. 그래서 명령을 실제로 치는 형태로 만든다.
 *
 * 설계 원칙
 * ---------
 * 1. 판정 근거는 화면에 다 있다. 문제를 외우는 게 아니라 파일을 읽어서 답이 나와야 한다.
 * 2. 정답은 "양호/취약" 한 글자가 아니라 **어느 줄을 보고 그렇게 판단했는가**까지다.
 * 3. 고치면 같은 명령의 출력이 실제로 바뀌고, 재점검하면 양호로 바뀐다.
 *    (설정을 바꿨다고 말만 하고 넘어가면 배우는 게 없다)
 * 4. 실제 시스템에 접속하지 않는다. 전부 이 페이지 안의 가상 파일시스템이다.
 *
 * 파일시스템 표현
 *   FS[path] = { body:'파일 내용', mode:'0644', owner:'root', group:'root', dir:false }
 */
(function () {
  'use strict';

  /* ── 유틸 ───────────────────────────────────────────── */
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  /* dev 는 'c'(문자 장치)·'b'(블록 장치). 장치 경로 점검에서 "장치 파일이 아닌 항목"을
     가려내려면 일반 파일과 장치 노드를 화면에서 구분할 수 있어야 한다. */
  function modeToRwx(mode, isDir, dev) {
    var m = String(mode).slice(-3);
    var map = ['---', '--x', '-w-', '-wx', 'r--', 'r-x', 'rw-', 'rwx'];
    var out = '';
    for (var i = 0; i < 3; i++) out += map[parseInt(m[i], 10) || 0];
    return (dev ? dev : (isDir ? 'd' : '-')) + out;
  }

  /* ── 가상 파일시스템 ──────────────────────────────────
     host 를 같이 들고 있는 이유: Windows 랩은 판정 근거가 파일이 아니라
     레지스트리·서비스·공유·로컬 정책이다. 판정 함수 시그니처는 verdict(fs) 하나뿐이므로
     fs.host 로 닿게 해 둔다. 전역(window.SRV_LAB_DATA)을 직접 읽게 하면
     미션마다 상태를 격리할 수 없어서 앞 미션의 조치가 뒤 미션 판정을 바꾼다. */
  function FileSystem(spec, host) {
    this.host = host || {};
    this.files = {};
    for (var p in spec) {
      var f = spec[p];
      this.files[p] = {
        body: f.body != null ? f.body : '',
        mode: f.mode || (f.dir ? '0755' : '0644'),
        owner: f.owner || 'root',
        group: f.group || 'root',
        dir: !!f.dir,
        dev: f.dev || false,        // 'c' | 'b' 면 장치 노드
        missing: !!f.missing,       // "이 경로에 파일이 없다"를 표현(점검 항목이 됨)
      };
    }
  }
  FileSystem.prototype.exists = function (p) {
    return !!this.files[p] && !this.files[p].missing;
  };
  FileSystem.prototype.read = function (p) {
    return this.exists(p) ? this.files[p].body : null;
  };
  FileSystem.prototype.write = function (p, body) {
    if (!this.files[p]) this.files[p] = { mode: '0644', owner: 'root', group: 'root', dir: false };
    this.files[p].body = body;
    this.files[p].missing = false;
  };
  /* 파일을 지운다. 목록·읽기에서 사라지되 "원래 있었다"는 사실은 남긴다
     (재점검에서 같은 명령을 다시 돌려 없어진 것을 확인할 수 있어야 한다). */
  FileSystem.prototype.remove = function (p) {
    if (this.files[p]) this.files[p].missing = true;
  };
  FileSystem.prototype.chmod = function (p, mode) {
    if (this.files[p]) this.files[p].mode = mode;
  };
  FileSystem.prototype.chown = function (p, owner, group) {
    if (!this.files[p]) return;
    this.files[p].owner = owner;
    if (group) this.files[p].group = group;
  };
  FileSystem.prototype.list = function (dir) {
    var out = [];
    var base = dir.replace(/\/+$/, '');
    for (var p in this.files) {
      if (this.files[p].missing) continue;
      if (p.indexOf(base + '/') !== 0) continue;
      var rest = p.slice(base.length + 1);
      if (rest.indexOf('/') >= 0) continue;         // 한 단계만
      out.push({ path: p, name: rest, f: this.files[p] });
    }
    return out.sort(function (a, b) { return a.name < b.name ? -1 : 1; });
  };

  /* ── 아주 작은 셸 ───────────────────────────────────────
     지원 범위를 일부러 좁게 뒀다. 점검에 실제로 쓰는 명령만 되고,
     안 되는 명령은 "이 실습에서는 지원하지 않습니다"라고 분명히 말한다.
     되는 척하면서 빈 출력을 주면 학습자가 "취약이 없구나"로 오해한다. */
  function Shell(fs, host) {
    this.fs = fs;
    /* host 를 따로 주지 않으면 파일시스템이 들고 있는 것을 쓴다.
       같은 객체를 공유해야 "조치 → 같은 명령의 출력이 바뀐다"가 성립한다. */
    this.host = host || fs.host ||
      { name: 'fin-app-01', procs: [], ports: [], pkgs: {}, users: [] };
  }

  Shell.prototype.run = function (line) {
    var raw = String(line || '').trim();
    if (!raw) return '';
    /* 파이프는 grep 한 단계만 지원한다(점검에서 제일 자주 쓰는 형태) */
    var parts = raw.split('|').map(function (s) { return s.trim(); });
    var out = this._one(parts[0]);
    for (var i = 1; i < parts.length; i++) {
      var pg = parts[i].match(/^(grep|egrep)\s+(-[a-zA-Z]+\s+)?(.+)$/);
      if (!pg) return out + '\n(이 실습의 셸은 파이프 뒤에 grep 만 지원합니다)';
      out = this._grep(out, pg[3], (pg[2] || '').trim());
    }
    return out;
  };

  Shell.prototype._grep = function (text, pattern, flags) {
    var pat = pattern.replace(/^['"]|['"]$/g, '');
    var inv = /v/.test(flags), ic = /i/.test(flags), cnt = /c/.test(flags);
    var re;
    try { re = new RegExp(pat, ic ? 'i' : ''); } catch (e) { return 'grep: 잘못된 패턴'; }
    var hits = String(text).split('\n').filter(function (l) {
      var m = re.test(l);
      return inv ? !m : m;
    });
    if (cnt) return String(hits.length);
    return hits.join('\n');
  };

  /* ── Windows 호스트 ────────────────────────────────────
     리눅스와 같은 "설정을 읽어 판정한다"는 흐름을 그대로 쓰되, 확인 수단이 다르다.
     Windows 는 파일이 아니라 **레지스트리·서비스·공유·로컬 정책**을 본다.
     host.reg / host.services / host.shares / host.policy 에 상태를 담고,
     판정 함수는 그 값을 읽는다(그래서 조치를 적용하면 같은 함수가 양호를 돌려준다). */
  Shell.prototype._win = function (cmd) {
    var h = this.host, m;

    if ((m = cmd.match(/^reg\s+query\s+"?([^"]+?)"?\s+\/v\s+(\S+)\s*$/i))) {
      var key = m[1].replace(/\//g, '\\'), name = m[2];
      var full = (key + '\\' + name).toLowerCase();
      var hit = null;
      for (var k in h.reg) { if (k.toLowerCase() === full) { hit = h.reg[k]; break; } }
      if (hit === null || hit === undefined) {
        return 'ERROR: 시스템이 지정된 레지스트리 키 또는 값을 찾을 수 없습니다.';
      }
      var type = typeof hit === 'number' ? 'REG_DWORD' : 'REG_SZ';
      var val = typeof hit === 'number' ? '0x' + hit.toString(16) : hit;
      return key + '\n    ' + name + '    ' + type + '    ' + val;
    }
    if ((m = cmd.match(/^reg\s+query\s+"?([^"]+?)"?\s*$/i))) {
      var base = m[1].replace(/\//g, '\\').toLowerCase();
      var rows = [];
      for (var k2 in h.reg) {
        var i2 = k2.lastIndexOf('\\');
        if (k2.slice(0, i2).toLowerCase() !== base) continue;
        var v2 = h.reg[k2];
        rows.push('    ' + k2.slice(i2 + 1) + '    ' +
          (typeof v2 === 'number' ? 'REG_DWORD    0x' + v2.toString(16) : 'REG_SZ    ' + v2));
      }
      return rows.length ? m[1] + '\n' + rows.join('\n')
        : 'ERROR: 시스템이 지정된 레지스트리 키 또는 값을 찾을 수 없습니다.';
    }
    if ((m = cmd.match(/^sc\s+query\s+(\S+)\s*$/i))) {
      var svc = (h.services || {})[m[1]];
      if (!svc) return '[SC] EnumQueryServicesStatus:OpenService 실패 1060:\n\n지정된 서비스가 설치된 서비스가 아닙니다.';
      return 'SERVICE_NAME: ' + m[1] + '\n        TYPE               : 10  WIN32_OWN_PROCESS\n' +
        '        STATE              : ' + (svc === 'running' ? '4  RUNNING' : '1  STOPPED');
    }
    if (/^net\s+share\s*$/i.test(cmd)) {
      var sh = h.shares || {};
      var out = ['공유 이름   리소스                        설명',
        '-------------------------------------------------------------------------------'];
      for (var s2 in sh) out.push(s2.padEnd(12) + String(sh[s2].path).padEnd(30) + (sh[s2].note || ''));
      return out.join('\n') + '\n명령을 잘 실행했습니다.';
    }
    if ((m = cmd.match(/^net\s+share\s+(\S+)\s*$/i))) {
      var one = (h.shares || {})[m[1]];
      if (!one) return '이 공유 이름을 찾을 수 없습니다.';
      return '공유 이름        ' + m[1] + '\n경로             ' + one.path +
        '\n사용 권한        ' + (one.perm || '(설정 없음)');
    }
    if ((m = cmd.match(/^net\s+user\s+(\S+)\s*$/i))) {
      var u = (h.users || {})[m[1]];
      if (!u) return '사용자 이름을 찾을 수 없습니다.';
      return '사용자 이름                  ' + m[1] +
        '\n계정 사용                    ' + (u.enabled ? 'Yes' : 'No') +
        '\n마지막으로 암호 설정         ' + (u.pwSet || '-') +
        '\n로컬 그룹 멤버쉽             ' + (u.groups || []).join(', ');
    }
    if (/^net\s+user\s*$/i.test(cmd)) {
      return '\\\\' + h.name + '에 대한 사용자 계정\n\n-------------------------------------------------------------------------------\n' +
        Object.keys(h.users || {}).join('    ');
    }
    if ((m = cmd.match(/^net\s+localgroup\s+(\S+)\s*$/i))) {
      var g = (h.groups || {})[m[1]];
      if (!g) return '그룹 이름을 찾을 수 없습니다.';
      return '별칭 이름     ' + m[1] + '\n\n구성원\n\n-------------------------------------------------------------------------------\n' +
        g.join('\n') + '\n명령을 잘 실행했습니다.';
    }
    if ((m = cmd.match(/^(?:secedit\s+\/export\s+\/cfg\s+\S+|secpol)/i))) {
      var p = h.policy || {};
      var lines = ['[System Access]'];
      for (var pk in p) lines.push(pk + ' = ' + p[pk]);
      return lines.join('\n');
    }
    if (/^schtasks\s*$/i.test(cmd) || /^schtasks\s+\/query/i.test(cmd)) {
      var t2 = h.tasks || [];
      return '작업 이름                      다음 실행 시간         실행할 작업\n' +
        '============================== ====================== ==========================\n' +
        t2.map(function (x) {
          return String(x.name).padEnd(30) + ' ' + String(x.next || '-').padEnd(22) + ' ' +
            (x.cmd || '(확인 불가)') + (x.user ? '   [실행 계정 ' + x.user + ']' : '');
        }).join('\n');
    }
    if ((m = cmd.match(/^(?:cacls|icacls)\s+(\S+)\s*$/i))) {
      var acl = (h.acl || {})[m[1].replace(/\//g, '\\')];
      if (!acl) return '지정된 경로를 찾을 수 없습니다.';
      return m[1] + ' ' + acl.join('\n' + ' '.repeat(m[1].length + 1));
    }
    if (/^wmic\s+logicaldisk/i.test(cmd)) {
      return 'DeviceID  FileSystem  Size\n' +
        (h.disks || []).map(function (d) { return String(d.id).padEnd(10) + String(d.fs).padEnd(12) + (d.size || ''); }).join('\n');
    }
    if (/^wmic\s+os\s+get/i.test(cmd) || /^systeminfo/i.test(cmd)) {
      var dep = h.dep == null ? 3 : h.dep;
      var depName = ['모든 프로그램 제외(꺼짐)', '필수 프로그램만', '기본 구성(OS 구성 요소)',
        '모든 프로그램'][dep] || String(dep);
      return 'OS 이름:                          ' + h.os +
        '\n시스템 종류:                      x64-based PC' +
        (h.today ? '\n현재 시스템 날짜:                 ' + h.today : '') +
        '\nDataExecutionPrevention_SupportPolicy : ' + dep + '  (' + depName + ')';
    }
    if (/^manage-bde(\s|$)/i.test(cmd)) {
      var ds = h.disks || [];
      if (!ds.length) return '암호화 대상 볼륨 정보를 가져올 수 없습니다.';
      return ds.map(function (d) {
        return '볼륨 ' + d.id + '\n    파일 시스템     ' + d.fs +
          '\n    변환 상태       ' + (d.enc ? '암호화됨' : '암호화되지 않음') +
          '\n    키 보호기       ' + (d.enc ? (d.keyProt || 'TPM') : '키 보호기를 찾을 수 없습니다');
      }).join('\n\n');
    }
    if (/^tasklist/i.test(cmd)) {
      return '이미지 이름                     PID 세션 이름\n' +
        '========================= ======== ================\n' +
        (h.procs || []).map(function (p) { return String(p.cmd).padEnd(25) + ' ' + String(p.pid).padStart(8) + ' Services'; }).join('\n');
    }
    if ((m = cmd.match(/^dir\s+\/a:h\s+(\S+)/i))) {
      return (h.hidden || []).join('\n') || '파일을 찾을 수 없습니다.';
    }
    return null;   // Windows 명령이 아니면 리눅스 처리로 넘긴다
  };

  Shell.prototype._one = function (cmd) {
    var fs = this.fs, host = this.host;
    var m;

    if (host.platform === 'windows') {
      var w = this._win(cmd);
      if (w !== null) return w;
      if (/^help$|^\?$/.test(cmd)) return this.helpText();
      return cmd.split(/\s+/)[0] + ': 이 실습에서는 지원하지 않는 명령입니다. help 를 입력해 보세요.';
    }

    if ((m = cmd.match(/^cat\s+(\S+)$/))) {
      var b = fs.read(m[1]);
      if (b === null) return 'cat: ' + m[1] + ': No such file or directory';
      return b;
    }
    if ((m = cmd.match(/^(?:ls\s+-(?:al?L?d?|la|ld|l)\s+|ls\s+-l\s+)(\S+)$/))) {
      return this._ls(m[1], true);
    }
    if ((m = cmd.match(/^ls\s+(\S+)$/))) return this._ls(m[1], false);
    if ((m = cmd.match(/^stat\s+(\S+)$/))) {
      var f = fs.files[m[1]];
      if (!f || f.missing) return 'stat: cannot stat ' + m[1] + ': No such file or directory';
      return '  File: ' + m[1] + '\nAccess: (' + f.mode.slice(-4) + '/' + modeToRwx(f.mode, f.dir) +
        ')  Uid: ( ' + f.owner + ' )   Gid: ( ' + f.group + ' )';
    }
    if ((m = cmd.match(/^(?:grep|egrep)\s+(?:-([a-zA-Z]+)\s+)?(?:'([^']*)'|"([^"]*)"|(\S+))\s+(\S+)$/))) {
      var flags = m[1] || '', pat = m[2] || m[3] || m[4], file = m[5];
      var body = fs.read(file);
      if (body === null) return 'grep: ' + file + ': No such file or directory';
      return this._grep(body, pat, flags);
    }
    if (/^ps\s+-ef$/.test(cmd) || /^ps\s+aux$/.test(cmd)) {
      return 'UID        PID  PPID  C STIME TTY          TIME CMD\n' +
        host.procs.map(function (p) {
          return (p.user || 'root').padEnd(10) + String(p.pid).padStart(5) + '     1  0 09:12 ?        00:00:00 ' + p.cmd;
        }).join('\n');
    }
    if (/^(netstat\s+-(an|tulpn|nlp)|ss\s+-(lntu|tulpn))/.test(cmd)) {
      return 'Proto Recv-Q Send-Q Local Address           Foreign Address         State\n' +
        host.ports.map(function (p) {
          return 'tcp        0      0 ' + (p.bind || '0.0.0.0') + ':' + String(p.port).padEnd(6) +
            '      0.0.0.0:*               LISTEN      ' + (p.svc || '');
        }).join('\n');
    }
    if ((m = cmd.match(/^(?:rpm\s+-q|dpkg\s+-l)\s+(\S+)$/))) {
      var v = host.pkgs[m[1]];
      return v ? m[1] + '-' + v : 'package ' + m[1] + ' is not installed';
    }
    if (/^(id|whoami)$/.test(cmd)) return 'uid=0(root) gid=0(root) groups=0(root)';
    if (/^hostname$/.test(cmd)) return host.name;
    if ((m = cmd.match(/^find\s+(\S+)\s+.*-perm\s+-(\d+)/))) {
      return this._findPerm(m[1], m[2]);
    }
    if ((m = cmd.match(/^find\s+(\S+)\s+.*-(nouser|nogroup)/))) {
      return this._findNoUser(m[1], m[2]);
    }
    if ((m = cmd.match(/^find\s+(\S+)\s+.*-type\s+f/))) {
      return this._findType(m[1]);
    }
    if (/^help$|^\?$/.test(cmd)) return this.helpText();
    return cmd.split(/\s+/)[0] + ': 이 실습에서는 지원하지 않는 명령입니다. help 를 입력해 보세요.';
  };

  Shell.prototype._ls = function (path, long) {
    var fs = this.fs;
    var f = fs.files[path];
    if (f && !f.missing && !f.dir) {
      if (!long) return path;
      return modeToRwx(f.mode, false, f.dev) + ' 1 ' + f.owner + ' ' + f.group + '  ' +
        String(f.body.length).padStart(6) + ' Sep 14 09:12 ' + path;
    }
    var items = fs.list(path);
    if (!items.length && !(f && f.dir)) return 'ls: cannot access ' + path + ': No such file or directory';
    if (!long) return items.map(function (i) { return i.name; }).join('  ');
    return items.map(function (i) {
      return modeToRwx(i.f.mode, i.f.dir, i.f.dev) + ' 1 ' + i.f.owner + ' ' + i.f.group + '  ' +
        String(i.f.body.length).padStart(6) + ' Sep 14 09:12 ' + i.name;
    }).join('\n');
  };

  Shell.prototype._findPerm = function (base, perm) {
    var fs = this.fs, out = [];
    var want = parseInt(perm, 8);
    for (var p in fs.files) {
      var f = fs.files[p];
      if (f.missing || f.dir) continue;
      if (p.indexOf(base === '/' ? '/' : base) !== 0) continue;
      var mode = parseInt(f.mode, 8);
      if ((mode & want) === want) {
        out.push(modeToRwx(f.mode, false) + ' 1 ' + f.owner + ' ' + f.group + '  ' + p);
      }
    }
    return out.join('\n');
  };

  /* find <경로> -type f — 장치 노드와 디렉터리를 뺀 "보통 파일"만 돌려준다.
     장치 경로에 장치가 아닌 것이 섞여 있는지 보는 점검에 쓴다. */
  Shell.prototype._findType = function (base) {
    var fs = this.fs, out = [];
    for (var p in fs.files) {
      var f = fs.files[p];
      if (f.missing || f.dir || f.dev) continue;
      if (p.indexOf(base === '/' ? '/' : base) !== 0) continue;
      out.push(p);
    }
    return out.sort().join('\n');
  };

  Shell.prototype._findNoUser = function (base, kind) {
    var fs = this.fs, out = [];
    for (var p in fs.files) {
      var f = fs.files[p];
      if (f.missing) continue;
      if (p.indexOf(base === '/' ? '/' : base) !== 0) continue;
      var who = kind === 'nouser' ? f.owner : f.group;
      if (/^\d+$/.test(who)) out.push(modeToRwx(f.mode, f.dir) + ' 1 ' + f.owner + ' ' + f.group + '  ' + p);
    }
    return out.join('\n');
  };

  Shell.prototype.helpText = function () {
    if (this.host.platform === 'windows') {
      return [
        '이 실습에서 쓸 수 있는 명령 (Windows)',
        '  reg query <키> /v <값>       레지스트리 값 확인',
        '  reg query <키>               키 아래 값 목록',
        '  sc query <서비스>            서비스 실행 상태',
        '  net share                    공유 목록',
        '  net share <이름>             공유 권한',
        '  net user [계정]              계정 목록·상세',
        '  net localgroup <그룹>        그룹 구성원',
        '  secedit /export /cfg out.txt 로컬 보안 정책',
        '  schtasks                     예약 작업 목록',
        '  cacls <경로>                 파일·폴더 권한',
        '  wmic logicaldisk             디스크 파일 시스템',
        '  wmic os get                  OS 정보·메모리 실행 방지 수준',
        '  manage-bde -status           볼륨 암호화 상태',
        '  tasklist                     실행 중인 프로세스',
        '  dir /a:h <경로>              숨김 항목',
      ].join('\n');
    }
    return [
      '이 실습에서 쓸 수 있는 명령',
      '  cat <파일>                 파일 내용 보기',
      '  ls -al <경로>              권한·소유자 보기',
      '  stat <파일>                권한 상세',
      '  grep [-i|-v|-c] <패턴> <파일>',
      '  ps -ef                     실행 중인 프로세스',
      '  netstat -an                열린 포트',
      '  rpm -q <패키지>            설치 버전',
      '  find <경로> -perm -4000    특정 권한 파일 찾기',
      '  find <경로> -nouser        소유자 없는 파일 찾기',
      '  find <경로> -type f        장치·디렉터리를 뺀 보통 파일 찾기',
      '  <명령> | grep <패턴>       파이프는 grep 한 단계까지',
    ].join('\n');
  };

  /* ── 미션 채점 ──────────────────────────────────────────
     정답은 두 부분이다: (1) 양호/취약 판정 (2) 그렇게 본 근거.
     근거를 고르지 않으면 찍어서 맞힐 수 있으므로 둘 다 요구한다. */
  function grade(mission, fs, chosenVerdict, chosenEvidence) {
    var actual = mission.verdict(fs);          // 현재 파일시스템 기준의 진짜 상태
    var verdictOk = chosenVerdict === actual;
    var need = mission.evidence || [];
    var evidenceOk = need.length === 0 ||
      need.some(function (e) { return chosenEvidence === e; });
    return {
      actual: actual,
      verdictOk: verdictOk,
      evidenceOk: evidenceOk,
      pass: verdictOk && evidenceOk,
    };
  }

  window.WVS_SRV_LAB = {
    FileSystem: FileSystem,
    Shell: Shell,
    grade: grade,
    esc: esc,
    modeToRwx: modeToRwx,
  };
})();
