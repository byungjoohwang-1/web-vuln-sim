/**
 * 펌웨어·IoT 임베디드 진단 실습 엔진 — 모의 펌웨어 분석 워크벤치 (FW-*)
 *
 * 왜 만들었나
 * -----------
 * 임베디드/IoT 보안 학습은 대개 "펌웨어를 추출해서 취약점을 찾는다"고 설명만 하고 끝난다.
 * 실무는 배포 이미지를 열어 파일시스템을 꺼내고, 설정·바이너리·키를 읽어 판정하고,
 * 재빌드된 이미지에서 그 결함이 사라졌는지 다시 확인하는 것이다. 07_srv 판정 설계를 따른다.
 *
 * 고도화 (2026-09): 캔드 출력 대신 **실제 바이트를 스캔**한다.
 *   - binwalk/strings/hexdump/entropy 는 host.image.layout 으로 생성한 진짜 Uint8Array 를 읽는다.
 *     시그니처(uImage 0x27051956, SquashFS 'hsqs' …)를 오프셋마다 실제로 찾고, 엔트로피를 실제 계산한다.
 *     암호화 조치를 하면 이미지가 고엔트로피로 바뀌어 시그니처가 사라진다(진짜로).
 *   - boot <img> 로 정적→동적 전환: rootfs 에서 실행 서비스를 도출해 netstat/ps 로 보여준다.
 *     inittab 등을 고치면 재부팅 시 그 포트/프로세스가 실제로 사라진다.
 *   - U-Boot 콘솔(printenv/setenv), cve-check(버전→자체작성 CVE DB) 추가.
 *
 * 상태 표현
 *   FS[path] = { body, mode, owner, group, dir, dev, ftype, bin, strings, missing }
 *   host.image = { file, layout:[{kind,size,text,name}], encrypted }  host.uboot, host.cvedb, host.dyn
 *   판정 함수는 fs / fs.host 를 읽는다(전역 직접 읽기 금지 → 미션 격리).
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

  /* ── 결정적 바이트 생성 (Math.random 안 씀 → 로드·테스트마다 동일) ── */
  function lcg(seed) {
    var s = seed >>> 0;
    return function () { s = (s * 1664525 + 1013904223) >>> 0; return (s >>> 24) & 0xff; };
  }
  function u32be(a, o, v) { a[o] = (v >>> 24) & 255; a[o + 1] = (v >>> 16) & 255; a[o + 2] = (v >>> 8) & 255; a[o + 3] = v & 255; }
  /* 필러 바이트가 시그니처 매직의 선두 바이트가 되지 않게 뒤집는다.
     안 그러면 랜덤 구간이 가짜 SquashFS/JFFS2 를 만들어 binwalk 출력이 지저분해진다. */
  function sb(v) { return (v === 0x27 || v === 0x68 || v === 0x73 || v === 0x85 || v === 0x5D || v === 0x1f) ? (v ^ 1) : v; }

  /* 펌웨어 이미지 바이트를 layout 스펙에서 실제로 조립한다.
     encrypted 면 전체를 고엔트로피로 채워 어떤 시그니처도 안 잡히게 한다(암호화된 배포본). */
  function buildImage(image) {
    if (!image) return new Uint8Array(0);
    if (image.encrypted) {
      var elen = image.len || 8192, eb = new Uint8Array(elen), er = lcg(0xC0FFEE);
      for (var i = 0; i < elen; i++) eb[i] = sb(er());
      return eb;
    }
    var parts = [];
    (image.layout || []).forEach(function (reg, idx) {
      var seed = 0x1000 + idx * 0x777, r = lcg(seed), b, i, sz = reg.size || 512;
      if (reg.kind === 'uimage') {
        b = new Uint8Array(reg.size || 64); u32be(b, 0, 0x27051956);
        var nm = reg.name || 'Linux Kernel Image';
        for (i = 0; i < nm.length && i < 32; i++) b[32 + i] = nm.charCodeAt(i) & 0xff;
      } else if (reg.kind === 'lzma') {
        b = new Uint8Array(sz); b[0] = 0x5D; b[1] = 0x00; b[2] = 0x00; b[3] = 0x01;
        for (i = 4; i < sz; i++) b[i] = sb((r() & 0x7f) | 0x40);   // 중간 엔트로피
      } else if (reg.kind === 'squashfs') {
        b = new Uint8Array(sz); b[0] = 0x68; b[1] = 0x73; b[2] = 0x71; b[3] = 0x73; // 'hsqs'
        b[28] = 0x04; b[29] = 0x00;                              // version 4.0 (LE)
        for (i = 96; i < sz; i++) b[i] = sb(r());                 // 압축 데이터 = 고엔트로피
      } else if (reg.kind === 'jffs2') {
        b = new Uint8Array(sz); b[0] = 0x85; b[1] = 0x19;        // JFFS2 LE
        for (i = 12; i < sz; i++) b[i] = sb(r());
      } else if (reg.kind === 'gzip') {
        b = new Uint8Array(sz); b[0] = 0x1f; b[1] = 0x8b; b[2] = 0x08;
        for (i = 10; i < sz; i++) b[i] = sb(r());
      } else if (reg.kind === 'text') {
        var t = reg.text || ''; b = new Uint8Array(t.length);
        for (i = 0; i < t.length; i++) b[i] = t.charCodeAt(i) & 0xff;
      } else { // 'random'
        b = new Uint8Array(sz); for (i = 0; i < sz; i++) b[i] = sb(r());
      }
      parts.push(b);
    });
    var total = parts.reduce(function (a, p) { return a + p.length; }, 0);
    var out = new Uint8Array(total), off = 0;
    parts.forEach(function (p) { out.set(p, off); off += p.length; });
    return out;
  }

  var SIGS = [
    { b: [0x27, 0x05, 0x19, 0x56], d: 'uImage header, header size: 64 bytes, OS: Linux, image type: OS Kernel Image' },
    { b: [0x68, 0x73, 0x71, 0x73], d: 'Squashfs filesystem, little endian, version 4.0' },
    { b: [0x73, 0x71, 0x73, 0x68], d: 'Squashfs filesystem, big endian' },
    { b: [0x85, 0x19], d: 'JFFS2 filesystem, little endian' },
    { b: [0x5D, 0x00, 0x00], d: 'LZMA compressed data' },
    { b: [0x1f, 0x8b, 0x08], d: 'gzip compressed data' },
  ];
  function matchAt(bytes, off, sig) {
    for (var i = 0; i < sig.length; i++) if (bytes[off + i] !== sig[i]) return false;
    return true;
  }
  function shannon(bytes, start, len) {
    var freq = {}, end = Math.min(bytes.length, start + len), n = end - start, i;
    if (n <= 0) return 0;
    for (i = start; i < end; i++) freq[bytes[i]] = (freq[bytes[i]] || 0) + 1;
    var h = 0;
    for (var k in freq) { var p = freq[k] / n; h -= p * (Math.log(p) / Math.log(2)); }
    return h; // bits/byte, 0..8
  }

  /* ── 가상 파일시스템 (추출된 rootfs) ── */
  function FileSystem(spec, host) {
    this.host = host || {};
    this.files = {};
    for (var p in spec) {
      var f = spec[p];
      this.files[p] = {
        body: f.body != null ? f.body : '', mode: f.mode || (f.dir ? '0755' : '0644'),
        owner: f.owner || 'root', group: f.group || 'root', dir: !!f.dir,
        dev: f.dev || false, ftype: f.ftype || null, bin: !!f.bin,
        strings: f.strings || null, missing: !!f.missing,
      };
    }
  }
  FileSystem.prototype.exists = function (p) { return !!this.files[p] && !this.files[p].missing; };
  FileSystem.prototype.read = function (p) { return this.exists(p) ? this.files[p].body : null; };
  FileSystem.prototype.write = function (p, body) {
    if (!this.files[p]) this.files[p] = { mode: '0644', owner: 'root', group: 'root', dir: false };
    this.files[p].body = body; this.files[p].missing = false;
  };
  FileSystem.prototype.remove = function (p) { if (this.files[p]) this.files[p].missing = true; };
  FileSystem.prototype.chmod = function (p, mode) { if (this.files[p]) this.files[p].mode = mode; };
  FileSystem.prototype.list = function (dir) {
    var out = [], base = dir.replace(/\/+$/, '');
    for (var p in this.files) {
      if (this.files[p].missing) continue;
      if (p.indexOf(base + '/') !== 0) continue;
      var rest = p.slice(base.length + 1);
      if (rest.indexOf('/') >= 0) continue;
      out.push({ path: p, name: rest, f: this.files[p] });
    }
    return out.sort(function (a, b) { return a.name < b.name ? -1 : 1; });
  };

  /* ── 셸 ── */
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
    var inv = /v/.test(flags), ic = /i/.test(flags), cnt = /c/.test(flags), re;
    try { re = new RegExp(pat, ic ? 'i' : ''); } catch (e) { return 'grep: 잘못된 패턴'; }
    var hits = String(text).split('\n').filter(function (l) { var m = re.test(l); return inv ? !m : m; });
    return cnt ? String(hits.length) : hits.join('\n');
  };

  /* 이미지 바이트 — 현재 encrypted 상태에 맞춰 생성(조치로 encrypted 가 바뀌면 다시 만든다) */
  Shell.prototype._imgBytes = function () {
    var img = this.host.image || {};
    if (!this._imgCache || this._imgCache.enc !== !!img.encrypted) {
      this._imgCache = { enc: !!img.encrypted, bytes: buildImage(img) };
    }
    return this._imgCache.bytes;
  };

  Shell.prototype._binwalk = function (path, extract) {
    var img = this.host.image || {};
    if (path !== img.file) return 'binwalk: ' + path + ': 이 이미지를 찾을 수 없습니다.';
    var bytes = this._imgBytes();
    var rows = ['DECIMAL       HEXADECIMAL     DESCRIPTION',
      '--------------------------------------------------------------------------------'];
    var found = [];
    for (var off = 0; off < bytes.length; off++) {
      for (var s = 0; s < SIGS.length; s++) {
        if (matchAt(bytes, off, SIGS[s].b)) {
          found.push({ off: off, d: SIGS[s].d });
          off += SIGS[s].b.length - 1; break;
        }
      }
    }
    found.forEach(function (f) {
      rows.push(String(f.off).padEnd(14) + ('0x' + f.off.toString(16).toUpperCase()).padEnd(16) + f.d);
    });
    if (!found.length) {
      // 시그니처 없음 + 고엔트로피 → 암호화 추정 (실제 계산)
      var h = shannon(bytes, 0, bytes.length);
      rows.push('(식별된 시그니처 없음 — 전체 엔트로피 ' + h.toFixed(2) +
        '/8.00, 고엔트로피 데이터로 암호화·서명 배포본으로 보입니다)');
      return rows.join('\n');
    }
    if (extract) {
      rows.push('', '[binwalk -e] 추출 완료 → _' + path + '.extracted/squashfs-root/ 에 rootfs 를 카빙했습니다.',
        '  이제 cat / ls -al / find 로 추출된 파일시스템을 탐색하세요.');
    }
    return rows.join('\n');
  };

  Shell.prototype._entropy = function (path) {
    var img = this.host.image || {};
    if (path !== img.file) return 'entropy: ' + path + ': 이 이미지를 찾을 수 없습니다.';
    var bytes = this._imgBytes(), win = 512, rows = ['오프셋        엔트로피(bits/byte)  판정'];
    for (var off = 0; off < bytes.length; off += win) {
      var h = shannon(bytes, off, win);
      var tag = h >= 7.5 ? '높음(압축/암호화)' : (h >= 5 ? '보통' : '낮음(헤더/텍스트)');
      rows.push(('0x' + off.toString(16).toUpperCase()).padEnd(12) + h.toFixed(2).padEnd(20) + tag);
    }
    var all = shannon(bytes, 0, bytes.length);
    rows.push('평균 ' + all.toFixed(2) + '/8.00');
    return rows.join('\n');
  };

  Shell.prototype._hexdump = function (path, len) {
    var bytes;
    var img = this.host.image || {};
    if (path === img.file) bytes = this._imgBytes();
    else {
      var f = this.fs.files[path];
      if (!f || f.missing) return 'hexdump: ' + path + ': No such file';
      var body = String(f.body); bytes = new Uint8Array(body.length);
      for (var i = 0; i < body.length; i++) bytes[i] = body.charCodeAt(i) & 0xff;
    }
    var n = Math.min(bytes.length, len || 128), rows = [];
    for (var o = 0; o < n; o += 16) {
      var hex = '', asc = '';
      for (var j = 0; j < 16; j++) {
        if (o + j < n) {
          var v = bytes[o + j]; hex += (v < 16 ? '0' : '') + v.toString(16) + ' ';
          asc += (v >= 32 && v < 127) ? String.fromCharCode(v) : '.';
        } else hex += '   ';
      }
      rows.push(('0000000' + o.toString(16)).slice(-8) + '  ' + hex + ' |' + asc + '|');
    }
    return rows.join('\n');
  };

  Shell.prototype._strings = function (path) {
    var img = this.host.image || {};
    if (path === img.file) {
      // 이미지 바이트에서 출력 가능한 ASCII 런(≥4)을 실제로 추출
      var bytes = this._imgBytes(), runs = [], cur = '';
      for (var i = 0; i < bytes.length; i++) {
        var v = bytes[i];
        if (v >= 32 && v < 127) cur += String.fromCharCode(v);
        else { if (cur.length >= 4) runs.push(cur); cur = ''; }
      }
      if (cur.length >= 4) runs.push(cur);
      return runs.join('\n') || '(추출된 문자열 없음)';
    }
    var f = this.fs.files[path];
    if (!f || f.missing) return 'strings: ' + path + ': No such file';
    if (f.bin) return (f.strings || []).join('\n');
    return String(f.body).split('\n').filter(function (l) { return l.trim().length >= 4; }).join('\n');
  };

  Shell.prototype._file = function (path) {
    var img = this.host.image || {};
    if (path === img.file) {
      var bytes = this._imgBytes();
      if (bytes[0] === 0x27 && bytes[1] === 0x05) return path + ': u-boot legacy uImage, Linux kernel';
      return path + ': data';
    }
    var f = this.fs.files[path];
    if (!f || f.missing) return path + ': cannot open (No such file or directory)';
    if (f.ftype) return path + ': ' + f.ftype;
    if (f.dir) return path + ': directory';
    if (f.dev) return path + ': ' + (f.dev === 'b' ? 'block' : 'character') + ' special';
    if (f.bin) return path + ': data';
    return path + ': ASCII text';
  };

  Shell.prototype._nvram = function (rest) {
    var nv = this.host.nvram || {}, m;
    if (/^show\s*$/.test(rest) || /^getall\s*$/.test(rest)) {
      var lines = []; for (var k in nv) lines.push(k + '=' + nv[k]); return lines.join('\n');
    }
    if ((m = rest.match(/^get\s+(\S+)\s*$/))) return nv[m[1]] != null ? String(nv[m[1]]) : '';
    return 'nvram: 사용법 — nvram show | nvram get <이름>';
  };

  /* U-Boot 부트로더 환경변수 콘솔 */
  Shell.prototype._uboot = function (cmd) {
    var env = this.host.uboot || {}, m;
    if (/^(printenv|fw_printenv)\s*$/i.test(cmd)) {
      var lines = []; for (var k in env) lines.push(k + '=' + env[k]);
      return lines.length ? lines.join('\n') : '(U-Boot 환경변수 없음)';
    }
    if ((m = cmd.match(/^(?:printenv|fw_printenv)\s+(\S+)\s*$/i))) {
      return env[m[1]] != null ? m[1] + '=' + env[m[1]] : '## Error: "' + m[1] + '" not defined';
    }
    if ((m = cmd.match(/^(?:setenv|fw_setenv)\s+(\S+)\s+(.+)$/i))) { env[m[1]] = m[2]; return ''; }
    if ((m = cmd.match(/^(?:setenv|fw_setenv)\s+(\S+)\s*$/i))) { delete env[m[1]]; return ''; }
    return null;
  };

  /* boot: rootfs 에서 실행 서비스를 도출해 동적 상태를 만든다.
     정적 설정을 고치면(예: inittab 에서 telnetd 제거) 재부팅 시 그 포트가 실제로 사라진다. */
  Shell.prototype._deriveDyn = function () {
    var fs = this.fs, ports = [], procs = [];
    var inittab = fs.read('/etc/inittab') || '';
    var rcS = fs.read('/etc/init.d/rcS') || '';
    var rclocal = fs.read('/etc/rc.local') || '';
    if (/telnetd/.test(inittab)) { ports.push({ p: 23, svc: 'telnetd' }); procs.push('/usr/sbin/telnetd'); }
    if (fs.exists('/usr/sbin/dropbear') || /dropbear/.test(rcS + rclocal)) { ports.push({ p: 22, svc: 'dropbear' }); procs.push('/usr/sbin/dropbear'); }
    var rtsp = fs.read('/etc/rtsp.conf') || '';
    if (/listen\s*=\s*\S*:554/.test(rtsp) && fs.exists('/usr/bin/camd')) { ports.push({ p: 554, svc: 'camd(rtsp)' }); procs.push('/usr/bin/camd'); }
    if (fs.exists('/www') || fs.exists('/www/index.html')) { ports.push({ p: 80, svc: 'httpd' }); procs.push('/usr/sbin/httpd'); }
    // rc.local 에 심긴 문서에 없는 서비스(백도어) — 정적으로는 놓치기 쉽고 부팅해야 드러난다
    var m = (rcS + '\n' + rclocal).match(/(\/\S+?)\s+.*?-p\s*(\d{3,5})/);
    if (m) { ports.push({ p: +m[2], svc: m[1].split('/').pop() + '(?)' }); procs.push(m[1]); }
    return { ports: ports, procs: procs };
  };
  Shell.prototype._boot = function () {
    this.host._dyn = this._deriveDyn();
    this.host._booted = true;
    var d = this.host._dyn;
    return '부팅 중... init → /etc/init.d/rcS\n' +
      '올라온 서비스: ' + (d.procs.length ? d.procs.join(', ') : '(없음)') + '\n' +
      '[ok] 시스템 부팅 완료 — 이제 netstat -an / ps 로 실행 중인 상태를 확인하세요.';
  };
  Shell.prototype._netstat = function () {
    if (!this.host._booted) return 'netstat: 아직 부팅하지 않았습니다. boot ' + (this.host.image || {}).file + ' 를 먼저 실행하세요.';
    var d = this.host._dyn || { ports: [] };
    return 'Proto Recv-Q Send-Q Local Address           Foreign Address         State\n' +
      d.ports.map(function (p) {
        return 'tcp        0      0 0.0.0.0:' + String(p.p).padEnd(6) +
          '        0.0.0.0:*               LISTEN      ' + p.svc;
      }).join('\n');
  };
  Shell.prototype._ps = function () {
    if (!this.host._booted) return 'ps: 아직 부팅하지 않았습니다. boot ' + (this.host.image || {}).file + ' 를 먼저 실행하세요.';
    var d = this.host._dyn || { procs: [] };
    return 'PID   USER     COMMAND\n' +
      d.procs.map(function (c, i) { return String(100 + i * 7).padEnd(6) + 'root     ' + c; }).join('\n');
  };

  /* cve-check <패키지> <버전> — 자체작성 CVE DB 대조 */
  Shell.prototype._cvecheck = function (pkg, ver) {
    var db = (this.host.cvedb || {})[pkg];
    if (!db) return 'cve-check: ' + pkg + ': DB 에 등록된 항목이 없습니다.';
    function cmp(a, b) { a = a.split('.').map(Number); b = b.split('.').map(Number); for (var i = 0; i < 3; i++) { if ((a[i] || 0) !== (b[i] || 0)) return (a[i] || 0) - (b[i] || 0); } return 0; }
    var hits = db.filter(function (c) { return cmp(ver, c.fixed) < 0; });
    if (!hits.length) return pkg + ' ' + ver + ': 알려진 (DB 등록) 취약점 없음';
    return pkg + ' ' + ver + ' — 해당 CVE ' + hits.length + '건:\n' +
      hits.map(function (c) { return '  ' + c.id + '  [' + c.sev + ']  ' + c.desc + '  (수정: ' + c.fixed + ' 이상)'; }).join('\n');
  };

  Shell.prototype._one = function (cmd) {
    var fs = this.fs, m;

    if ((m = cmd.match(/^binwalk\s+(-e)\s+(\S+)$/))) return this._binwalk(m[2], true);
    if ((m = cmd.match(/^binwalk\s+(?:-\w+\s+)*(\S+)$/))) return this._binwalk(m[1], false);
    if ((m = cmd.match(/^entropy\s+(\S+)$/))) return this._entropy(m[1]);
    if ((m = cmd.match(/^(?:hexdump|xxd)\s+(?:-C\s+|-n\s+(\d+)\s+)*(\S+)$/))) return this._hexdump(m[2], m[1] ? +m[1] : 128);
    if ((m = cmd.match(/^strings\s+(?:-\w+\s+)*(\S+)$/))) return this._strings(m[1]);
    if ((m = cmd.match(/^file\s+(\S+)$/))) return this._file(m[1]);
    if ((m = cmd.match(/^nvram\s+(.+)$/))) return this._nvram(m[1].trim());
    if (/^(printenv|setenv|fw_printenv|fw_setenv)\b/i.test(cmd)) { var u = this._uboot(cmd); if (u !== null) return u; }
    if ((m = cmd.match(/^boot(?:\s+\S+)?\s*$/))) return this._boot();
    if (/^(netstat\s+-(an|tulpn|nlp)|ss\s+-(lntu|tulpn))/.test(cmd)) return this._netstat();
    if (/^ps(\s+-ef|\s+aux)?\s*$/.test(cmd)) return this._ps();
    if ((m = cmd.match(/^cve-check\s+(\S+)\s+(\S+)\s*$/))) return this._cvecheck(m[1], m[2]);

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
    if ((m = cmd.match(/^find\s+(\S+)\s+.*-name\s+(?:'([^']*)'|"([^"]*)"|(\S+))/))) return this._findName(m[1], m[2] || m[3] || m[4]);
    if ((m = cmd.match(/^find\s+(\S+)\s+.*-perm\s+-(\d+)/))) return this._findPerm(m[1], m[2]);
    if ((m = cmd.match(/^find\s+(\S+)\s+.*-type\s+f/))) return this._findType(m[1]);
    if (/^(id|whoami)$/.test(cmd)) return 'uid=0(root) gid=0(root)  # 추출된 rootfs 를 로컬에서 분석 중';
    if (/^help$|^\?$/.test(cmd)) return this.helpText();
    return cmd.split(/\s+/)[0] + ': 이 실습에서는 지원하지 않는 명령입니다. help 를 입력해 보세요.';
  };

  Shell.prototype._ls = function (path, long) {
    var fs = this.fs, f = fs.files[path];
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
    var fs = this.fs, out = [], pat = pattern.replace(/^['"]|['"]$/g, '');
    var re = new RegExp('^' + pat.replace(/[.+^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*').replace(/\?/g, '.') + '$');
    for (var p in fs.files) {
      var f = fs.files[p];
      if (f.missing) continue;
      if (p.indexOf(base === '/' ? '/' : base) !== 0) continue;
      if (re.test(p.slice(p.lastIndexOf('/') + 1))) out.push(p);
    }
    return out.sort().join('\n');
  };
  Shell.prototype._findPerm = function (base, perm) {
    var fs = this.fs, out = [], want = parseInt(perm, 8);
    for (var p in fs.files) {
      var f = fs.files[p];
      if (f.missing || f.dir) continue;
      if (p.indexOf(base === '/' ? '/' : base) !== 0) continue;
      if ((parseInt(f.mode, 8) & want) === want) out.push(modeToRwx(f.mode, false, f.dev) + ' 1 ' + f.owner + ' ' + f.group + '  ' + p);
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
      '  binwalk <이미지>           내장 시그니처·파일시스템 스캔 (실제 바이트 스캔)',
      '  binwalk -e <이미지>        추출 실행 → rootfs 카빙',
      '  entropy <이미지>           구간별 엔트로피 (압축/암호화 판별)',
      '  hexdump -C <경로>          바이트 16진 덤프 (매직 확인)',
      '  strings <파일|이미지>      사람이 읽을 수 있는 문자열 추출',
      '  file <경로>                파일 형식 판별',
      '  nvram show|get <이름>      기기 설정값',
      '  printenv / setenv          U-Boot 부트로더 환경변수',
      '  boot <이미지>              펌웨어를 부팅(정적→동적)',
      '  netstat -an / ps           (부팅 후) 열린 포트·실행 프로세스',
      '  cve-check <패키지> <버전>  버전을 알려진 CVE DB 와 대조',
      '  cat / ls -al / stat / grep / find -name|-perm|-type f',
      '  <명령> | grep <패턴>       파이프는 grep 한 단계까지',
    ].join('\n');
  };

  function grade(mission, fs, chosenVerdict, chosenEvidence) {
    var actual = mission.verdict(fs);
    var verdictOk = chosenVerdict === actual;
    var need = mission.evidence || [];
    var evidenceOk = need.length === 0 || need.some(function (e) { return chosenEvidence === e; });
    return { actual: actual, verdictOk: verdictOk, evidenceOk: evidenceOk, pass: verdictOk && evidenceOk };
  }

  window.WVS_FW_LAB = {
    FileSystem: FileSystem, Shell: Shell, grade: grade, esc: esc, modeToRwx: modeToRwx,
    buildImage: buildImage, shannon: shannon,
  };
})();
