/**
 * 정보보호시스템(보안장비) 진단 실습 엔진 — 모의 어플라이언스 CLI (ISS-*)
 *
 * 왜 만들었나
 * -----------
 * 보안장비 점검은 지금까지 "설명을 읽고 양호/취약을 고르는" 형태였다.
 * 실무에서 하는 일은 그게 아니라 **장비에 접속해 show 명령으로 설정을 뽑고,
 * 그 출력을 판단기준과 맞춰 보고, 고친 뒤 같은 명령으로 다시 확인하는 것**이다.
 * 서버 점검(srv-lab)을 명령 기반으로 만든 것과 같은 이유로 장비도 그렇게 만든다.
 *
 * 서버와 무엇이 다른가
 *   서버는 설정이 파일로 있어서 cat 으로 읽는다. 장비는 파일이 아니라
 *   구조화된 설정이고 show 명령으로 단면을 본다. 그래서 가상 파일시스템이
 *   아니라 **설정 객체 + show 명령 렌더러**로 만든다.
 *
 * 설계 원칙 (srv-lab 과 동일)
 * ---------------------------
 * 1. 판정 근거는 화면에 다 있다. 외우는 게 아니라 출력을 읽어서 답이 나와야 한다.
 * 2. 정답은 "양호/취약" 한 글자가 아니라 **어느 줄을 보고 그렇게 판단했는가**까지다.
 * 3. 고치면 같은 show 명령의 출력이 실제로 바뀐다. 말로만 고치고 넘어가지 않는다.
 * 4. 실제 장비에 접속하지 않는다. 전부 이 페이지 안의 가상 설정이다.
 * 5. 실존 장비 상표를 쓰지 않는다. 가상 벤더(SENTRA)와 가상 모델명을 쓴다.
 *
 * 평가대상 구분
 *   같은 항목이라도 장비 종류(FW/VPN/IDS/IPS/DDoS/WAF)에 따라 해당 없음이 된다.
 *   실제 평가표가 장비별 ○ 표로 그 범위를 정하므로, 미션에 appliesTo 를 두고
 *   대상이 아닌 장비에서는 '해당없음(N/A)'으로 처리한다.
 */
(function () {
  'use strict';

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  /* 값이 열 너비에 딱 맞거나 넘치면 다음 열과 붙어 버린다. 실제로
     "08:41:122023-11-02" 처럼 두 값이 한 덩어리로 보이는 출력이 나왔다.
     열이 넘치더라도 최소 한 칸은 띄워 둔다. */
  function pad(s, n) {
    s = String(s == null ? '' : s);
    if (s.length >= n) return s + ' ';
    while (s.length < n) s += ' ';
    return s;
  }
  function rpad(s, n) {
    s = String(s == null ? '' : s);
    while (s.length < n) s = ' ' + s;
    return s;
  }
  function onoff(v) { return v ? 'enabled' : 'disabled'; }
  function yesno(v) { return v ? 'yes' : 'no'; }
  function line(ch, n) { var s = ''; for (var i = 0; i < n; i++) s += ch; return s; }

  /* ── 설정 객체 ──────────────────────────────────────────
     경로 문자열로 읽고 쓴다. 미션의 verdict/fix 가 같은 경로를 쓰므로
     "무엇을 보고 판단했는지"와 "무엇을 고쳤는지"가 코드상에서도 이어진다. */
  function Config(spec) {
    this.data = JSON.parse(JSON.stringify(spec));
    this._initial = JSON.stringify(spec);
  }
  Config.prototype.get = function (path) {
    var parts = String(path).split('.'), cur = this.data;
    for (var i = 0; i < parts.length; i++) {
      if (cur == null) return undefined;
      cur = cur[parts[i]];
    }
    return cur;
  };
  Config.prototype.set = function (path, value) {
    var parts = String(path).split('.'), cur = this.data;
    for (var i = 0; i < parts.length - 1; i++) {
      if (cur[parts[i]] == null || typeof cur[parts[i]] !== 'object') cur[parts[i]] = {};
      cur = cur[parts[i]];
    }
    cur[parts[parts.length - 1]] = value;
    return value;
  };
  Config.prototype.reset = function () { this.data = JSON.parse(this._initial); };

  /* ── show 명령 렌더러 ───────────────────────────────────
     실제 장비의 출력 형태를 따라간다. 표 폭을 고정해 둔 것은 눈으로 열을
     맞춰 읽는 실무 습관을 그대로 옮기기 위한 것이다. */
  var VIEWS = {
    'show version': function (c) {
      var s = c.get('system') || {};
      var eosWarn = s.eosPassed ? '  *** End of Service ***' : '';
      return [
        'Model            : ' + s.model,
        'Serial           : ' + s.serial,
        'Software         : ' + s.os,
        'Build            : ' + s.build,
        'Device role      : ' + s.role,
        'Uptime           : ' + s.uptime,
        'Support end (EoS): ' + s.eosDate + eosWarn,
        'Signature set    : ' + (s.sigVersion || '(n/a)') + '   updated ' + (s.sigDate || '-'),
      ].join('\n');
    },

    'show admin': function (c) {
      var a = c.get('admins') || [];
      var out = ['NAME        ROLE          SHARED  LAST-LOGIN           PW-CHANGED', line('-', 70)];
      a.forEach(function (u) {
        out.push(pad(u.name, 12) + pad(u.role, 14) + pad(yesno(u.shared), 8) +
          pad(u.lastLogin, 21) + u.pwChanged);
      });
      var d = c.get('auth.defaultAccount');
      out.push('');
      out.push('Factory default account : ' + (d && d.present
        ? d.name + ' (present, password ' + (d.passwordChanged ? 'changed' : 'UNCHANGED') + ')'
        : 'removed'));
      return out.join('\n');
    },

    'show password-policy': function (c) {
      var p = c.get('auth.password') || {}, l = c.get('auth.lockout') || {};
      return [
        'min-length          : ' + p.minLength,
        'complexity          : ' + (p.complexity || 'none'),
        'max-age (days)      : ' + (p.maxAgeDays === 0 ? '0  (no expiry)' : p.maxAgeDays),
        'reuse-check         : ' + onoff(p.reuseCheck),
        '',
        'lockout             : ' + onoff(l.enabled),
        'lockout threshold   : ' + (l.enabled ? l.threshold + ' failures' : '-'),
        'lockout duration    : ' + (l.enabled ? l.durationMin + ' min' : '-'),
      ].join('\n');
    },

    'show session': function (c) {
      var s = c.get('auth.session') || {};
      var out = ['LINE        TIMEOUT'];
      out.push(line('-', 28));
      (s.lines || []).forEach(function (l) {
        out.push(pad(l.name, 12) + (l.timeoutMin === 0 ? 'never' : l.timeoutMin + ' min'));
      });
      return out.join('\n');
    },

    'show management': function (c) {
      var m = c.get('mgmt') || {};
      var out = ['PROTOCOL   PORT   STATE      ENCRYPTED'];
      out.push(line('-', 44));
      (m.protocols || []).forEach(function (p) {
        out.push(pad(p.name, 11) + pad(p.port, 7) + pad(onoff(p.enabled), 11) + yesno(p.encrypted));
      });
      out.push('');
      var ips = m.allowedIps || [];
      out.push('Management access list : ' + (ips.length ? '' : '(none — any source permitted)'));
      ips.forEach(function (i) { out.push('  permit ' + i); });
      out.push('Login banner           : ' + (m.banner ? 'configured' : 'not configured'));
      return out.join('\n');
    },

    'show snmp': function (c) {
      var s = c.get('snmp') || {};
      if (!s.enabled) return 'SNMP agent : disabled';
      var out = ['SNMP agent : enabled', 'Version    : ' + s.version];
      if (s.version === 'v3') {
        out.push('Security   : ' + s.secLevel);
        out.push('User       : ' + s.user);
      } else {
        out.push('Community  : ' + s.community + '   (' + s.access + ')');
      }
      out.push('Purpose    : ' + (s.purpose || '(not recorded)'));
      return out.join('\n');
    },

    'show logging': function (c) {
      var g = c.get('logging') || {}, r = g.remote || {};
      return [
        'Local logging       : ' + onoff(g.enabled),
        'Login success       : ' + onoff(g.loginSuccess),
        'Login failure       : ' + onoff(g.loginFail),
        'Config change       : ' + onoff(g.configChange),
        'Raw packet capture  : ' + onoff(g.rawPacket) +
          (g.rawPacket ? '   (severity >= ' + g.rawPacketSeverity + ')' : ''),
        'Local retention     : ' + g.retentionDays + ' days',
        '',
        'Remote log server   : ' + onoff(r.enabled) +
          (r.enabled ? '   ' + r.proto + ' ' + r.host + ':' + r.port : ''),
        'Remote retention    : ' + (r.enabled ? r.retentionDays + ' days' : '-'),
      ].join('\n');
    },

    'show ntp': function (c) {
      var n = c.get('ntp') || {};
      if (!n.enabled) return 'NTP : disabled\nClock source : local (free-running)';
      var out = ['NTP : enabled', 'SERVER            STRATUM  STATE'];
      out.push(line('-', 40));
      (n.servers || []).forEach(function (s) {
        out.push(pad(s.host, 18) + pad(s.stratum, 9) + s.state);
      });
      return out.join('\n');
    },

    'show interface': function (c) {
      var ifs = c.get('interfaces') || [];
      var out = ['NAME      ZONE        ADDRESS             STATE'];
      out.push(line('-', 56));
      ifs.forEach(function (i) {
        out.push(pad(i.name, 10) + pad(i.zone, 12) + pad(i.address, 20) + i.state);
      });
      return out.join('\n');
    },

    'show nat': function (c) {
      var n = c.get('nat') || [];
      if (!n.length) return 'No NAT rules configured.';
      var out = ['NO  NAME             ORIGINAL              TRANSLATED          NOTE'];
      out.push(line('-', 76));
      n.forEach(function (r, i) {
        out.push(pad(i + 1, 4) + pad(r.name, 17) + pad(r.original, 22) + pad(r.translated, 20) + (r.note || ''));
      });
      return out.join('\n');
    },

    'show policy': function (c) {
      var r = c.get('rules') || [];
      var out = ['NO  SOURCE            DESTINATION       SERVICE          ACT    LOG  DIR   HITS      LAST-HIT'];
      out.push(line('-', 104));
      r.forEach(function (x) {
        out.push(pad(x.n, 4) + pad(x.src, 18) + pad(x.dst, 18) + pad(x.svc, 17) +
          pad(x.action, 7) + pad(yesno(x.log), 5) + pad(x.bidir ? 'both' : '->', 6) +
          pad(x.hits, 10) + (x.lastHit || 'never'));
      });
      out.push('');
      out.push('Default policy : ' + (c.get('policyDefault') || 'deny'));
      return out.join('\n');
    },

    'show service': function (c) {
      var s = c.get('services') || [];
      var out = ['SERVICE      PORT    STATE      PURPOSE'];
      out.push(line('-', 58));
      s.forEach(function (x) {
        out.push(pad(x.name, 13) + pad(x.port, 8) + pad(onoff(x.enabled), 11) + (x.purpose || '-'));
      });
      out.push('');
      out.push('IP source-routing : ' + onoff(c.get('net.sourceRouting')));
      return out.join('\n');
    },

    'show signature': function (c) {
      var d = c.get('detect') || {};
      var out = ['PATTERN GROUP          STATE      ACTION'];
      out.push(line('-', 50));
      (d.groups || []).forEach(function (g) {
        out.push(pad(g.name, 23) + pad(onoff(g.enabled), 11) + g.action);
      });
      out.push('');
      out.push('Blocking mode      : ' + (d.blockMode || 'n/a'));
      out.push('Hardware bypass    : ' + onoff(d.hwBypass));
      out.push('Blocks last 30d    : ' + (d.blocks30d == null ? '-' : d.blocks30d));
      return out.join('\n');
    },

    'show resource': function (c) {
      var m = c.get('monitor') || {};
      return [
        'CPU (5 min avg)      : ' + m.cpu + ' %',
        'Memory               : ' + m.memory + ' %',
        'Session table        : ' + m.sessions + ' / ' + m.sessionMax,
        '',
        'Usage review         : ' + (m.usageReview ? m.usageReviewCycle : 'not performed'),
        'Realtime monitoring  : ' + onoff(m.realtime),
        'Alerting             : ' + (m.alerting && m.alerting.length ? m.alerting.join(', ') : 'none'),
        'Event/log review     : ' + (m.logReview ? m.logReviewCycle : 'not performed'),
      ].join('\n');
    },

    'show backup': function (c) {
      var b = c.get('backup') || {};
      return [
        'Policy backup   : ' + onoff(b.policy) + (b.policy ? '   cycle ' + b.policyCycle : ''),
        'Log backup      : ' + onoff(b.log) + (b.log ? '   cycle ' + b.logCycle : ''),
        'Last backup     : ' + (b.last || 'never'),
        'Destination     : ' + (b.dest || '-'),
        '',
        'Integrity check : ' + (b.integrity ? b.integrityCycle : 'not performed'),
      ].join('\n');
    },

    'show patch': function (c) {
      var s = c.get('system') || {}, p = c.get('patch') || {};
      return [
        'Software         : ' + s.os + '   build ' + s.build,
        'Latest available : ' + p.latest,
        'Signature set    : ' + (s.sigVersion || '(n/a)') + '   updated ' + (s.sigDate || '-'),
        'Latest signature : ' + (p.latestSig || '(n/a)'),
        '',
        'Patch review     : ' + (p.review ? p.reviewCycle : 'not performed'),
        'Vendor advisories: ' + (p.advisoriesApplied == null ? '-'
          : p.advisoriesApplied + ' / ' + p.advisoriesTotal + ' applied'),
      ].join('\n');
    },

    'show change-control': function (c) {
      var g = c.get('change') || {};
      return [
        'Change procedure    : ' + (g.procedure ? 'documented' : 'not documented'),
        'Request form        : ' + (g.requestForm ? 'required' : 'not required'),
        'Technical review    : ' + (g.techReview ? 'required before apply' : 'not required'),
        'Recent changes (30d): ' + (g.recent || 0) +
          '   of which unapproved: ' + (g.unapproved || 0),
      ].join('\n');
    },
  };

  /* running-config 는 위 단면들을 모아 한 번에 보여 준다. 실제 장비에서
     제일 먼저 뽑는 산출물이라 학습자도 여기서 출발할 수 있어야 한다. */
  function runningConfig(cfg, device) {
    var order = ['show version', 'show interface', 'show admin', 'show password-policy',
      'show session', 'show management', 'show snmp', 'show logging', 'show ntp',
      'show nat', 'show policy', 'show service', 'show signature', 'show resource',
      'show backup', 'show patch', 'show change-control'];
    var out = ['! ' + device.name + ' running configuration',
      '! generated ' + (device.configDate || '-'), ''];
    order.forEach(function (k) {
      if (!VIEWS[k]) return;
      var body = VIEWS[k](cfg);
      if (body == null) return;
      out.push('! ===== ' + k.replace('show ', '').toUpperCase() + ' =====');
      out.push(body);
      out.push('');
    });
    return out.join('\n');
  }

  /* ── CLI ────────────────────────────────────────────────
     실제 장비처럼 축약형을 받는다(sh ver). 모르는 명령은 장비가 내는 것과
     같은 형태로 거절한다 — 아무거나 받아 주면 명령을 배우는 의미가 없다. */
  var ALIAS = {
    'sh': 'show', 'sho': 'show',
    'ver': 'version', 'int': 'interface', 'pol': 'policy', 'polic': 'policy',
    'log': 'logging', 'logg': 'logging', 'sig': 'signature', 'res': 'resource',
    'mgmt': 'management', 'man': 'management', 'sess': 'session',
    'pw-policy': 'password-policy', 'pass': 'password-policy', 'password': 'password-policy',
    'run': 'running-config', 'running': 'running-config',
    'svc': 'service', 'serv': 'service', 'cc': 'change-control',
  };
  function normalize(cmd) {
    var t = String(cmd).trim().replace(/\s+/g, ' ').toLowerCase();
    if (!t) return '';
    var parts = t.split(' ').map(function (w) { return ALIAS[w] || w; });
    return parts.join(' ');
  }

  function Cli(cfg, device) {
    this.cfg = cfg;
    this.device = device;
  }
  Cli.prototype.commands = function () {
    return Object.keys(VIEWS).concat(['show running-config']);
  };
  Cli.prototype.run = function (raw) {
    var cmd = normalize(raw);
    if (!cmd) return '';
    if (cmd === 'show running-config' || cmd === 'show config') {
      return runningConfig(this.cfg, this.device);
    }
    if (cmd === '?' || cmd === 'help' || cmd === 'show ?') {
      return '사용 가능한 명령\n' + this.commands().map(function (c) { return '  ' + c; }).join('\n');
    }
    if (VIEWS[cmd]) return VIEWS[cmd](this.cfg);
    if (cmd.indexOf('show ') === 0) {
      return '% Invalid input detected at "' + raw.trim() + '"\n' +
        '  "show ?" 로 사용 가능한 명령을 볼 수 있습니다.';
    }
    if (/^(conf|configure|set|no |enable)/.test(cmd)) {
      return '% 이 실습에서는 설정 명령을 직접 입력하지 않습니다.\n' +
        '  항목별 [조치 적용] 버튼으로 설정을 바꾸고, 같은 show 명령으로 결과를 확인하세요.';
    }
    return '% Unknown command: ' + raw.trim() + '\n  "?" 를 입력하면 명령 목록이 나옵니다.';
  };

  /* ── 채점 ───────────────────────────────────────────────
     srv-lab 과 같은 계약. 판정만 맞히고 근거를 못 고르면 통과가 아니다. */
  function grade(mission, cfg, chosenVerdict, chosenEvidence) {
    var actual = mission.verdict(cfg);
    var verdictOk = chosenVerdict === actual;
    var want = mission.evidence || [];
    var got = chosenEvidence || [];
    var evidenceOk = want.length === got.length &&
      want.every(function (e) { return got.indexOf(e) >= 0; });
    return {
      actual: actual,
      verdictOk: verdictOk,
      evidenceOk: evidenceOk,
      pass: verdictOk && evidenceOk,
    };
  }

  /** 이 장비 종류가 해당 항목의 평가대상인지. 대상이 아니면 N/A 로 다룬다. */
  function applies(mission, deviceType) {
    if (!mission.appliesTo || !mission.appliesTo.length) return true;
    return mission.appliesTo.indexOf(deviceType) >= 0;
  }

  window.WVS_ISS_LAB = {
    Config: Config,
    Cli: Cli,
    grade: grade,
    applies: applies,
    esc: esc,
    views: VIEWS,
  };
})();
