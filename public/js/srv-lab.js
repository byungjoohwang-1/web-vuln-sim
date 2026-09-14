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
  function modeToRwx(mode, isDir) {
    var m = String(mode).slice(-3);
    var map = ['---', '--x', '-w-', '-wx', 'r--', 'r-x', 'rw-', 'rwx'];
    var out = '';
    for (var i = 0; i < 3; i++) out += map[parseInt(m[i], 10) || 0];
    return (isDir ? 'd' : '-') + out;
  }

  /* ── 가상 파일시스템 ────────────────────────────────── */
  function FileSystem(spec) {
    this.files = {};
    for (var p in spec) {
      var f = spec[p];
      this.files[p] = {
        body: f.body != null ? f.body : '',
        mode: f.mode || (f.dir ? '0755' : '0644'),
        owner: f.owner || 'root',
        group: f.group || 'root',
        dir: !!f.dir,
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
    this.host = host || { name: 'fin-app-01', procs: [], ports: [], pkgs: {}, users: [] };
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

  Shell.prototype._one = function (cmd) {
    var fs = this.fs, host = this.host;
    var m;

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
    if (/^help$|^\?$/.test(cmd)) return this.helpText();
    return cmd.split(/\s+/)[0] + ': 이 실습에서는 지원하지 않는 명령입니다. help 를 입력해 보세요.';
  };

  Shell.prototype._ls = function (path, long) {
    var fs = this.fs;
    var f = fs.files[path];
    if (f && !f.missing && !f.dir) {
      if (!long) return path;
      return modeToRwx(f.mode, false) + ' 1 ' + f.owner + ' ' + f.group + '  ' +
        String(f.body.length).padStart(6) + ' Sep 14 09:12 ' + path;
    }
    var items = fs.list(path);
    if (!items.length && !(f && f.dir)) return 'ls: cannot access ' + path + ': No such file or directory';
    if (!long) return items.map(function (i) { return i.name; }).join('  ');
    return items.map(function (i) {
      return modeToRwx(i.f.mode, i.f.dir) + ' 1 ' + i.f.owner + ' ' + i.f.group + '  ' +
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
