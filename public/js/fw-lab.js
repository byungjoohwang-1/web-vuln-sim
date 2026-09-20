/**
 * 펌웨어·IoT 임베디드 진단 실습 엔진 — 모의 펌웨어 분석 워크벤치 (FW-*)
 *
 * 왜 만들었나
 * -----------
 * 임베디드/IoT 보안 학습은 대개 "펌웨어를 추출해서 취약점을 찾는다"고 설명만 하고 끝난다.
 * 실무에서 하는 일은 **배포 이미지를 binwalk 로 열어 파일시스템을 꺼내고, 그 안의 설정·바이너리·키를
 * 읽어 판정하고, 재빌드된 이미지에서 그 결함이 사라졌는지 다시 확인하는 것**이다.
 * 그래서 명령을 실제로 치는 형태로 만든다. 07_srv 엔진과 같은 판정 설계를 따른다.
 *
 * 설계 원칙 (srv-lab 과 동일)
 * ---------
 * 1. 판정 근거는 화면에 다 있다. 외우는 게 아니라 이미지를 열어 읽어서 답이 나와야 한다.
 * 2. 정답은 "양호/취약" 한 글자가 아니라 **어느 줄을 보고 그렇게 판단했는가**까지다.
 * 3. 고치면(재빌드) 같은 명령의 출력이 실제로 바뀌고, 재점검하면 양호로 바뀐다.
 * 4. 실제 기기에 접속하지 않는다. 전부 이 페이지 안의 가상 펌웨어 이미지·파일시스템이다.
 *
 * 상태 표현
 *   FS[path] = { body, mode, owner, group, dir, dev, ftype, bin, strings, missing }
 *   host.image   = { file, binwalk:[...], encrypted, signed }  (binwalk/update 상태)
 *   host.nvram   = { key: value }                              (nvram show/get)
 *   판정 함수는 fs / fs.host 를 읽는다(전역을 직접 읽으면 미션 격리가 깨진다).
 */
(function () {
  'use strict';

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function modeToRwx(mode, isDir, dev) {
    var m = String(mode).slice(-3);
    var map = ['---', '--x', '-w-', '-wx', 'r--', 'r-x', 'rw-', 'rwx'];
    var out = '';
    for (var i = 0; i < 3; i++) out += map[parseInt(m[i], 10) || 0];
    return (dev ? dev : (isDir ? 'd' : '-')) + out;
  }

  /* ── 가상 파일시스템 (추출된 rootfs) ────────────────────
     host 를 같이 들고 있는 이유: 판정 근거가 파일이 아니라 이미지 상태(binwalk·서명)나
     nvram 인 미션이 있다. 판정 함수 시그니처는 verdict(fs) 하나뿐이므로 fs.host 로 닿게 둔다. */
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
        dev: f.dev || false,          // 'c' | 'b'
        ftype: f.ftype || null,       // file(1) 이 돌려줄 형식 문자열
        bin: !!f.bin,                 // 바이너리(그냥 cat 하면 의미 없음)
        strings: f.strings || null,   // bin 파일에서 strings 가 뽑아낼 문자열 배열
        missing: !!f.missing,
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
  FileSystem.prototype.remove = function (p) {
    if (this.files[p]) this.files[p].missing = true;
  };
  FileSystem.prototype.chmod = function (p, mode) {
    if (this.files[p]) this.files[p].mode = mode;
  };
  FileSystem.prototype.list = function (dir) {
    var out = [];
    var base = dir.replace(/\/+$/, '');
    for (var p in this.files) {
      if (this.files[p].missing) continue;
      if (p.indexOf(base + '/') !== 0) continue;
      var rest = p.slice(base.length + 1);
      if (rest.indexOf('/') >= 0) continue;
      out.push({ path: p, name: rest, f: this.files[p] });
    }
    return out.sort(function (a, b) { return a.name < b.name ? -1 : 1; });
  };

  /* ── 셸 ─────────────────────────────────────────────────
     펌웨어 분석에 실제로 쓰는 명령만. 안 되는 명령은 빈 출력 대신 분명히 안내한다
     (빈 출력을 "취약 없음"으로 오해하는 것을 막는다). */
  function Shell(fs, host) {
    this.fs = fs;
    this.host = host || fs.host || { name: 'workbench', image: {}, nvram: {} };
  }

  Shell.prototype.run = function (line) {
    var raw = String(line || '').trim();
    if (!raw) return '';
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

  /* strings: 텍스트 파일은 내용 줄을, 바이너리는 미리 뽑아 둔 strings 배열을 돌려준다.
     실제 strings(1) 은 4바이트 이상 출력 가능 문자열을 뽑는데, 교육용으로는 "그 안에서
     의미 있는 문자열"만 있으면 되므로 스펙에 담아 둔 배열을 쓴다. */
  Shell.prototype._strings = function (path) {
    var f = this.fs.files[path];
    if (!f || f.missing) return 'strings: ' + path + ': No such file';
    if (f.bin) return (f.strings || []).join('\n');
    // 텍스트 파일이면 출력 가능한 줄만(공백 아닌 것)
    return String(f.body).split('\n').filter(function (l) { return l.trim().length >= 4; }).join('\n');
  };

  Shell.prototype._file = function (path) {
    var f = this.fs.files[path];
    if (!f || f.missing) return path + ': cannot open (No such file or directory)';
    if (f.ftype) return path + ': ' + f.ftype;
    if (f.dir) return path + ': directory';
    if (f.dev) return path + ': ' + (f.dev === 'b' ? 'block' : 'character') + ' special';
    if (f.bin) return path + ': data';
    return path + ': ASCII text';
  };

  Shell.prototype._binwalk = function (path) {
    var img = this.host.image || {};
    if (path !== img.file) return 'binwalk: ' + path + ': 이 이미지를 찾을 수 없습니다.';
    var rows = ['DECIMAL       HEXADECIMAL     DESCRIPTION',
      '--------------------------------------------------------------------------------'];
    /* 이미지가 암호화·서명되면 시그니처가 안 잡힌다 → 조치(재빌드) 후 이 출력이 바뀐다.
       host 는 JSON 으로 직렬화되므로 binwalk 결과는 함수가 아니라 encrypted 플래그로 가른다. */
    if (img.encrypted) {
      return rows.join('\n') +
        '\n(식별된 시그니처 없음 — 이미지가 암호화되어 고엔트로피 데이터로 보입니다)';
    }
    var sigs = img.binwalk || [];
    if (!sigs.length) return rows.join('\n') + '\n(식별된 시그니처 없음)';
    sigs.forEach(function (s) {
      rows.push(String(s.dec).padEnd(14) + ('0x' + s.hex).padEnd(16) + s.desc);
    });
    return rows.join('\n');
  };

  Shell.prototype._nvram = function (rest) {
    var nv = this.host.nvram || {};
    var m;
    if (/^show\s*$/.test(rest) || /^getall\s*$/.test(rest)) {
      var lines = [];
      for (var k in nv) lines.push(k + '=' + nv[k]);
      return lines.join('\n');
    }
    if ((m = rest.match(/^get\s+(\S+)\s*$/))) {
      return nv[m[1]] != null ? String(nv[m[1]]) : '';
    }
    return 'nvram: 사용법 — nvram show | nvram get <이름>';
  };

  Shell.prototype._one = function (cmd) {
    var fs = this.fs, m;

    if ((m = cmd.match(/^binwalk\s+(?:-\w+\s+)*(\S+)$/))) return this._binwalk(m[1]);
    if ((m = cmd.match(/^strings\s+(?:-\w+\s+)*(\S+)$/))) return this._strings(m[1]);
    if ((m = cmd.match(/^file\s+(\S+)$/))) return this._file(m[1]);
    if ((m = cmd.match(/^nvram\s+(.+)$/))) return this._nvram(m[1].trim());

    if ((m = cmd.match(/^cat\s+(\S+)$/))) {
      var f = fs.files[m[1]];
      if (!f || f.missing) return 'cat: ' + m[1] + ': No such file or directory';
      if (f.bin) return 'cat: ' + m[1] + ': 바이너리 파일입니다. strings 또는 file 로 살펴보세요.';
      return f.body;
    }
    if ((m = cmd.match(/^(?:ls\s+-(?:al?L?d?|la|ld|l)\s+|ls\s+-l\s+)(\S+)$/))) return this._ls(m[1], true);
    if ((m = cmd.match(/^ls\s+(\S+)$/))) return this._ls(m[1], false);
    if ((m = cmd.match(/^stat\s+(\S+)$/))) {
      var sf = fs.files[m[1]];
      if (!sf || sf.missing) return 'stat: cannot stat ' + m[1] + ': No such file or directory';
      return '  File: ' + m[1] + '\nAccess: (' + sf.mode.slice(-4) + '/' + modeToRwx(sf.mode, sf.dir, sf.dev) +
        ')  Uid: ( ' + sf.owner + ' )   Gid: ( ' + sf.group + ' )';
    }
    if ((m = cmd.match(/^(?:grep|egrep)\s+(?:-([a-zA-Z]+)\s+)?(?:'([^']*)'|"([^"]*)"|(\S+))\s+(\S+)$/))) {
      var flags = m[1] || '', pat = m[2] || m[3] || m[4], file = m[5];
      var body = fs.read(file);
      if (body === null) return 'grep: ' + file + ': No such file or directory';
      return this._grep(body, pat, flags);
    }
    if ((m = cmd.match(/^find\s+(\S+)\s+.*-name\s+(?:'([^']*)'|"([^"]*)"|(\S+))/))) {
      return this._findName(m[1], m[2] || m[3] || m[4]);
    }
    if ((m = cmd.match(/^find\s+(\S+)\s+.*-perm\s+-(\d+)/))) return this._findPerm(m[1], m[2]);
    if ((m = cmd.match(/^find\s+(\S+)\s+.*-type\s+f/))) return this._findType(m[1]);
    if (/^(id|whoami)$/.test(cmd)) return 'uid=0(root) gid=0(root)  # 추출된 rootfs 를 로컬에서 분석 중';
    if (/^help$|^\?$/.test(cmd)) return this.helpText();
    return cmd.split(/\s+/)[0] + ': 이 실습에서는 지원하지 않는 명령입니다. help 를 입력해 보세요.';
  };

  Shell.prototype._ls = function (path, long) {
    var fs = this.fs;
    var f = fs.files[path];
    if (f && !f.missing && !f.dir) {
      if (!long) return path;
      return modeToRwx(f.mode, false, f.dev) + ' 1 ' + f.owner + ' ' + f.group + '  ' +
        String(f.body.length).padStart(6) + ' Jan  1  1970 ' + path;
    }
    var items = fs.list(path);
    if (!items.length && !(f && f.dir)) return 'ls: cannot access ' + path + ': No such file or directory';
    if (!long) return items.map(function (i) { return i.name; }).join('  ');
    return items.map(function (i) {
      return modeToRwx(i.f.mode, i.f.dir, i.f.dev) + ' 1 ' + i.f.owner + ' ' + i.f.group + '  ' +
        String(i.f.body.length).padStart(6) + ' Jan  1  1970 ' + i.name;
    }).join('\n');
  };

  Shell.prototype._findName = function (base, pattern) {
    var fs = this.fs, out = [];
    var pat = pattern.replace(/^['"]|['"]$/g, '');
    // 셸 글로브(* ?)를 정규식으로
    var re = new RegExp('^' + pat.replace(/[.+^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*').replace(/\?/g, '.') + '$');
    for (var p in fs.files) {
      var f = fs.files[p];
      if (f.missing) continue;
      if (p.indexOf(base === '/' ? '/' : base) !== 0) continue;
      var name = p.slice(p.lastIndexOf('/') + 1);
      if (re.test(name)) out.push(p);
    }
    return out.sort().join('\n');
  };

  Shell.prototype._findPerm = function (base, perm) {
    var fs = this.fs, out = [];
    var want = parseInt(perm, 8);
    for (var p in fs.files) {
      var f = fs.files[p];
      if (f.missing || f.dir) continue;
      if (p.indexOf(base === '/' ? '/' : base) !== 0) continue;
      if ((parseInt(f.mode, 8) & want) === want) {
        out.push(modeToRwx(f.mode, false, f.dev) + ' 1 ' + f.owner + ' ' + f.group + '  ' + p);
      }
    }
    return out.join('\n');
  };

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

  Shell.prototype.helpText = function () {
    return [
      '이 실습에서 쓸 수 있는 명령 (펌웨어 분석 워크벤치)',
      '  binwalk <이미지>           펌웨어 이미지의 내장 시그니처·파일시스템 스캔',
      '  strings <파일>             바이너리에서 사람이 읽을 수 있는 문자열 추출',
      '  file <경로>                파일 형식 판별(ELF 아키텍처 등)',
      '  nvram show                 기기 설정값(nvram) 전체',
      '  nvram get <이름>           설정값 하나',
      '  cat <파일>                 텍스트 파일 내용',
      '  ls -al <경로>              권한·소유자',
      '  stat <파일>                권한 상세',
      '  grep [-i|-v|-c] <패턴> <파일>',
      '  find <경로> -name "*.key"  이름으로 파일 찾기',
      '  find <경로> -perm -0002    쓰기 가능(world-writable) 파일 찾기',
      '  find <경로> -type f        보통 파일 찾기',
      '  <명령> | grep <패턴>       파이프는 grep 한 단계까지',
    ].join('\n');
  };

  /* ── 미션 채점 (srv-lab 과 동일) ── */
  function grade(mission, fs, chosenVerdict, chosenEvidence) {
    var actual = mission.verdict(fs);
    var verdictOk = chosenVerdict === actual;
    var need = mission.evidence || [];
    var evidenceOk = need.length === 0 ||
      need.some(function (e) { return chosenEvidence === e; });
    return { actual: actual, verdictOk: verdictOk, evidenceOk: evidenceOk, pass: verdictOk && evidenceOk };
  }

  window.WVS_FW_LAB = {
    FileSystem: FileSystem,
    Shell: Shell,
    grade: grade,
    esc: esc,
    modeToRwx: modeToRwx,
  };
})();
