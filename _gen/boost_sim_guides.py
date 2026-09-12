# -*- coding: utf-8 -*-
"""sim-* 정적 개념 가이드 4종에 O/X 퀴즈 인터랙티브 섹션을 멱등 주입한다.

대상: sim-time-state.html(2-3), sim-error-handling.html(2-4),
      sim-quality.html(2-5), sim-encap.html(2-6)
주입 위치: 본문 컨테이너 닫는 div 직전(콘텐츠 영역 안), bootstrap 스크립트 앞.
재실행 시 마커(WVS-QUIZ-BOOST:v1)가 있으면 건너뛴다.
"""
import json
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public')
MARKER = '<!-- WVS-QUIZ-BOOST:v1 -->'

# 페이지별 퀴즈 데이터: q(문항), a(True=O), why(해설)
QUIZZES = {
    'sim-time-state.html': [
        {'q': '파일 접근 권한을 검사한 시점과 실제로 파일을 사용하는 시점 사이에 공격자가 파일을 바꿔치기할 수 있는 취약점을 TOCTOU(Time-Of-Check to Time-Of-Use)라고 한다.',
         'a': True,
         'why': '"검사 시점과 사용 시점" 사이의 짧은 창(window)이 공격 기회가 됩니다. 검사가 참이었어도 사용 순간의 상태는 바뀌어 있을 수 있습니다.'},
        {'q': '경쟁 조건(Race Condition)은 두 프로세스가 같은 파일에 동시에 접근할 때 발생하므로, 파일 락(lock)이나 원자적 연산을 사용하면 오히려 위험이 커진다.',
         'a': False,
         'why': '반대입니다. 파일 락(flock)·원자적 생성(O_CREAT|O_EXCL)·단일 디스크립터 사용은 경쟁 조건 창을 좁히는 "올바른 대응"입니다.'},
        {'q': '권한 검사 후 파일을 이름으로 다시 여는 대신, 검사와 사용을 한 번에 열린 파일 디스크립터(핸들)로 처리하면 검사-사용 사이의 바꿔치기 창을 줄일 수 있다.',
         'a': True,
         'why': '이미 열린 디스크립터가 가리키는 대상은 이름으로 다시 여는 것과 달리 중간에 심볼릭 링크 등으로 교체될 수 없습니다.'},
        {'q': '임시 파일을 만들 때 예측 가능한 이름(tmp-1.tmp)을 쓰더라도, 생성 시 O_EXCL 플래그를 지정하면 이미 존재하는 파일(심볼릭 링크)을 통한 공격을 차단할 수 있다.',
         'a': True,
         'why': 'O_CREAT|O_EXCL은 파일이 이미 존재하면 생성에 실패시킵니다. 더 안전한 방법은 예측 불가능한 이름을 만들어 주는 mkstemp() 계열 사용입니다.'},
    ],
    'sim-error-handling.html': [
        {'q': '예외 발생 시 스택 트레이스(e.printStackTrace() 출력)를 사용자 화면에 그대로 보여주면 내부 경로·클래스명·라이브러리 버전이 공격자의 정찰 재료가 된다.',
         'a': True,
         'why': '"오류 메시지를 통한 정보노출" 약점입니다. 상세 정보는 서버 로그로, 사용자에게는 "일시적 오류가 발생했습니다" 수준의 일반화된 메시지를 보여야 합니다.'},
        {'q': 'catch(Exception e) {} 처럼 catch 블록을 비워 두면 예외가 조용히 무시되어, 장애·공격의 원인 추적이 어려워지는 보안 약점이 된다.',
         'a': True,
         'why': '"오류 상황 대응 부재"입니다. 무시된 예외는 데이터 불일치·자원 누수로 이어지고, 침입 흔적이 로그에 남지 않게 만듭니다.'},
        {'q': '에러 메시지는 상세할수록 사용자에게 도움이 되므로, 실패한 SQL 쿼리 문장도 그대로 응답에 포함해서 보여주는 것이 좋다.',
         'a': False,
         'why': '쿼리·테이블 구조 노출은 SQL 인젝션의 재료가 됩니다. 상세한 원인은 로그에 기록하고, 응답은 요청 ID가 포함된 일반 메시지로 제한합니다.'},
        {'q': '데이터베이스 연결·파일 핸들 같은 자원은 finally 블록이나 try-with-resources로 반드시 해제해야, 누적된 자원 고갈이 서비스 거부로 이어지는 것을 막을 수 있다.',
         'a': True,
         'why': '해제되지 않은 자원은 누적되어 결국 전체 서비스가 거부되는 결과를 낳습니다. try-with-resources(또는 finally의 close)로 해제를 보장하세요.'},
    ],
    'sim-quality.html': [
        {'q': '널(Null) 포인터 역참조는 프로그램이 죽는 가용성 문제일 뿐, 보안 관점에서는 다룰 위험이 없다.',
         'a': False,
         'why': '크래시 자체가 서비스 거부(DoS)이며, 예외 처리 경계가 흐트러지면 인증 우회 같은 논리 결함으로 번질 수 있습니다. 사용 전 널 검사가 필요합니다.'},
        {'q': '사용이 끝난 자원(메모리·소켓·파일 핸들)은 가비지 컬렉터가 즉시 회수해 주므로 명시적으로 해제하지 않아도 안전하다.',
         'a': False,
         'why': 'GC 실행 시점은 보장되지 않으며, 네이티브 자원(소켓·fd)은 회수 대상이 아닐 수 있습니다. "부적절한 자원 해제"는 자원 고갈·서비스 거부로 이어집니다.'},
        {'q': '신뢰 경계 밖에서 들어온 데이터(요청 파라미터·파일·환경변수)는 검증 없이 반복 횟수나 버퍼 크기 같은 자원 사용량 결정에 써도 된다.',
         'a': False,
         'why': '신뢰되지 않은 데이터는 길이·값 범위를 검증한 뒤 사용해야 합니다. 검증 없는 사용은 자원 고갈(대용량 업로드, 무한 반복)의 직접 원인이 됩니다.'},
        {'q': '의도된 데몬의 대기 루프는 괜찮지만, 입력값에 따라 반복문의 종료 조건이 건너뛰어질 수 있다면 자원 고갈·서비스 거부 위험이므로 종료 조건을 검증해야 한다.',
         'a': True,
         'why': '문제는 "빠져나올 수 없는 반복"입니다. 반복 횟수 상한을 검증된 범위로 제한하면 의도치 않은 무한 루프를 막을 수 있습니다.'},
    ],
    'sim-encap.html': [
        {'q': 'public 메서드가 내부 private 배열을 그대로 return 하면, 외부 코드가 반환된 배열을 수정해 내부 상태를 바꿀 수 있다.',
         'a': True,
         'why': '배열은 참조이므로 반환 시 내부 데이터가 그대로 노출됩니다. 방어적 복사본(clone)을 반환해 내부 상태를 보호해야 합니다.'},
        {'q': '생성자에서 외부에서 전달된 배열을 private 필드에 그대로 저장해도, 호출 이후 원본 배열을 수정하면 내부 데이터가 함께 바뀌므로 복사본을 저장하는 것이 안전하다.',
         'a': True,
         'why': '입력 배열도 참조입니다. 저장 시 복사하고, 필요 시 반환 시에도 복사하는 "이중 방어적 복사"로 캡슐화를 완성합니다.'},
        {'q': '배포 전에 남겨 둔 System.out.println 디버깅 코드는 일반 사용자가 콘솔을 볼 수 없으므로 정보노출 위험이 없다.',
         'a': False,
         'why': '"제거되지 않은 디버깅 코드"는 로그·에러 콘솔·모니터링 도구로 그대로 노출됩니다. 민감정보(비밀번호·내부 URL) 출력은 침해 단서가 됩니다.'},
        {'q': '자원 해제는 finalize()를 오버라이딩해 맡기면 GC가 즉시 호출해 주므로, try-finally로 명시적으로 해제하는 것보다 안전하다.',
         'a': False,
         'why': 'API 오용 사례입니다. finalize()는 호출 시점·호출 여부 보장이 없고(Java 9+ 사용 중단 권고), 명시적 해제(try-with-resources)가 정답입니다.'},
    ],
}

TPL = '''<!-- WVS-QUIZ-BOOST:v1 -->
<style>
.wvsq-card{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:26px 28px;margin:40px 0 24px;box-shadow:0 2px 8px rgba(15,23,42,.06)}
.wvsq-title{font-size:1.3rem;font-weight:800;margin:0 0 6px;color:#1e293b}
.wvsq-sub{color:#64748b;font-size:.92rem;margin:0 0 16px}
.wvsq-item{border:1px solid #e2e8f0;border-radius:10px;padding:15px 18px;margin:13px 0}
.wvsq-q{font-weight:700;margin:0 0 10px;line-height:1.65;color:#0f172a}
.wvsq-btn{min-width:64px;padding:7px 20px;border-radius:8px;border:2px solid #cbd5e1;background:#fff;font-weight:800;font-size:1rem;cursor:pointer;transition:all .15s}
.wvsq-btn:hover:not(:disabled){border-color:#4c3d8f;background:#f5f3ff}
.wvsq-btn:disabled{cursor:default;opacity:.5}
.wvsq-btn.wvsq-hit{border-color:#16a34a;background:#dcfce7;opacity:1}
.wvsq-btn.wvsq-miss{border-color:#dc2626;background:#fee2e2;opacity:1}
.wvsq-fb{margin-top:10px;padding:10px 14px;border-radius:8px;font-size:.9rem;line-height:1.7;display:none;color:#334155}
.wvsq-fb.ok{display:block;background:#f0fdf4;border:1px solid #bbf7d0}
.wvsq-fb.no{display:block;background:#fef2f2;border:1px solid #fecaca}
.wvsq-fb b{display:block;margin-bottom:3px}
.wvsq-score{margin-top:16px;padding:14px 18px;border-radius:10px;background:#f5f3ff;border:1px solid #ddd6fe;font-weight:700;color:#4c3d8f;display:none}
.wvsq-retry{margin-top:12px;padding:8px 22px;border-radius:8px;border:0;background:#4c3d8f;color:#fff;font-weight:700;cursor:pointer;display:none}
.wvsq-retry:hover{background:#3d3073}
</style>
<div class="wvsq-card" id="wvsqBox">
  <h2 class="wvsq-title">🎯 핵심 개념 O/X 퀴즈</h2>
  <p class="wvsq-sub">이 페이지의 보안 개념을 4문항으로 점검해 보세요. O/X를 고르면 즉시 해설이 표시됩니다. · 진행 <span id="wvsqProg">0 / 4</span></p>
  <div id="wvsqList"></div>
  <div class="wvsq-score" id="wvsqScore"></div>
  <button class="wvsq-retry" id="wvsqRetry" type="button">🔄 다시 풀기</button>
</div>
<script>
(function () {
  var QS = __QS__;
  var list = document.getElementById('wvsqList');
  var prog = document.getElementById('wvsqProg');
  var score = document.getElementById('wvsqScore');
  var retry = document.getElementById('wvsqRetry');
  var done = 0, right = 0;

  window.wvsqInit = function () {
    done = 0; right = 0;
    list.innerHTML = '';
    score.style.display = 'none';
    retry.style.display = 'none';
    prog.textContent = '0 / ' + QS.length;
    QS.forEach(function (item, i) {
      var box = document.createElement('div');
      box.className = 'wvsq-item';
      var q = document.createElement('p');
      q.className = 'wvsq-q';
      q.textContent = 'Q' + (i + 1) + '. ' + item.q;
      var btnO = document.createElement('button');
      btnO.type = 'button'; btnO.className = 'wvsq-btn'; btnO.textContent = 'O';
      var btnX = document.createElement('button');
      btnX.type = 'button'; btnX.className = 'wvsq-btn'; btnX.textContent = 'X';
      btnX.style.marginLeft = '6px';
      var fb = document.createElement('div');
      fb.className = 'wvsq-fb';
      function pick(val) {
        var correct = val === item.a;
        var picked = val ? btnO : btnX;
        var correctBtn = item.a ? btnO : btnX;
        btnO.disabled = true; btnX.disabled = true;
        correctBtn.classList.add('wvsq-hit');
        if (!correct) picked.classList.add('wvsq-miss');
        fb.className = 'wvsq-fb ' + (correct ? 'ok' : 'no');
        var head = document.createElement('b');
        head.textContent = correct ? '⭕ 정답입니다!' : '❌ 아쉽습니다. 정답은 ' + (item.a ? 'O' : 'X') + '.';
        var why = document.createElement('span');
        why.textContent = item.why;
        fb.appendChild(head); fb.appendChild(why);
        done++; if (correct) right++;
        prog.textContent = done + ' / ' + QS.length;
        if (done === QS.length) {
          var msg = right === QS.length ? '🏆 만점! 이 주제의 핵심을 완벽히 잡으셨습니다.'
            : right >= QS.length - 1 ? '👍 아주 좋습니다! 한 문항만 다시 복습해 보세요.'
            : '📖 해설을 다시 읽고 "다시 풀기"로 확인해 보세요.';
          score.textContent = '결과: ' + QS.length + '문항 중 ' + right + '문항 정답 — ' + msg;
          score.style.display = 'block';
          retry.style.display = 'inline-block';
        }
      }
      btnO.addEventListener('click', function () { pick(true); });
      btnX.addEventListener('click', function () { pick(false); });
      box.appendChild(q); box.appendChild(btnO); box.appendChild(btnX); box.appendChild(fb);
      list.appendChild(box);
    });
  };
  window.wvsqInit();
})();
</script>
<!-- /WVS-QUIZ-BOOST -->
'''

ANCHOR = ('\r\n\r\n        </div>\r\n    </div>\r\n</div>\r\n\r\n'
          '<script src="https://cdn.jsdelivr.net/npm/bootstrap')


def main():
    for fname, qs in QUIZZES.items():
        path = os.path.join(BASE, fname)
        with open(path, encoding='utf-8', newline='') as fp:
            h = fp.read()
        if MARKER in h:
            print('SKIP(이미 적용):', fname)
            continue
        if ANCHOR not in h:
            print('FAIL(앵커 없음):', fname)
            continue
        block = TPL.replace('__QS__', json.dumps(qs, ensure_ascii=False))
        # 대상 파일은 CRLF — 블록도 CRLF로 맞춘다
        block = block.replace('\n', '\r\n')
        h = h.replace(ANCHOR, '\r\n' + block + ANCHOR, 1)
        with open(path, 'w', encoding='utf-8', newline='') as fp:
            fp.write(h)
        print('OK:', fname)


if __name__ == '__main__':
    main()
