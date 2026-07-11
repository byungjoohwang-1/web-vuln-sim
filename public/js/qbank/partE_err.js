window.__QBANK = window.__QBANK || { QUIZ: [], THEORY: [] };
window.__QBANK.QUIZ.push(
  {
    c: "에러처리",
    q: "다음 Java 코드의 보안약점으로 가장 적절한 것은?",
    o: [
      "오류 메시지를 통한 정보 노출(CWE-209)",
      "확인되지 않은 오류 조건(CWE-391)",
      "부적절한 자원 해제(CWE-460)",
      "반환값 미확인(CWE-252)"
    ],
    a: 0,
    e: "예외의 e.getMessage() 또는 스택트레이스를 사용자 응답에 그대로 반환하면 내부 경로·SQL·라이브러리 버전 등 민감정보가 노출된다. 이는 CWE-209(오류 메시지를 통한 정보 노출)에 해당한다. 상세 정보는 서버 로그에만 남기고 사용자에게는 일반화된 메시지를 반환해야 한다.",
    code: `try {
    user = repository.find(userId);
} catch (SQLException e) {
    response.getWriter().write("오류: " + e.getMessage());
}`
  },
  {
    c: "에러처리",
    q: "예외를 catch한 뒤 아무런 조치도 하지 않는 아래 코드의 약점은?",
    o: [
      "처리되지 않은 예외(CWE-248)",
      "예외처리 후 적절한 조치 없음 / 빈 catch(CWE-390)",
      "오류 메시지 정보 노출(CWE-209)",
      "부적절한 반환값 확인(CWE-253)"
    ],
    a: 1,
    e: "catch 블록을 비워두면(빈 catch) 오류가 조용히 무시되어 프로그램이 잘못된 상태로 계속 실행된다. 이는 CWE-390(오류 조건을 감지했으나 조치하지 않음)에 해당한다. 최소한 로깅하거나 적절히 복구/전파해야 한다.",
    code: `try {
    transfer(amount);
} catch (Exception e) {
    // 아무것도 하지 않음
}`
  },
  {
    c: "에러처리",
    q: "e.printStackTrace()를 운영 환경 웹 애플리케이션에서 사용할 때의 주된 문제는?",
    o: [
      "성능이 크게 저하된다",
      "스택트레이스가 표준 출력/에러로 나가 노출되거나 내부 구조 정보를 흘릴 수 있다(CWE-209)",
      "예외가 다시 던져진다",
      "컴파일 경고가 발생한다"
    ],
    a: 1,
    e: "printStackTrace()는 스택트레이스를 표준 에러 스트림으로 출력하며, 이 출력이 사용자에게 노출되거나 로그를 통해 클래스명·경로·프레임워크 정보를 흘려 CWE-209로 이어질 수 있다. 통제된 로거를 사용해 서버 측에만 기록해야 한다.",
    code: `try {
    process(request);
} catch (Exception e) {
    e.printStackTrace();
}`
  },
  {
    c: "에러처리",
    q: "다음 Python 코드에서 나타나는 보안약점은?",
    o: [
      "확인되지 않은 오류 조건(CWE-391)",
      "예외처리 후 적절한 조치 없음(CWE-390)",
      "부적절한 정리(CWE-460)",
      "반환값 부적절 확인(CWE-253)"
    ],
    a: 1,
    e: "except: pass는 발생한 모든 예외(bare except)를 무시하고 아무 조치도 하지 않는다. 오류가 은폐되어 잘못된 상태로 실행이 계속되므로 CWE-390에 해당한다. 또한 bare except는 KeyboardInterrupt/SystemExit까지 삼킨다는 부가 문제도 있다.",
    code: `try:
    balance = get_balance(account)
except:
    pass`
  },
  {
    c: "에러처리",
    q: "C/Java에서 함수의 반환값을 확인하지 않아 실패를 성공으로 오인하는 약점의 CWE는?",
    o: [
      "CWE-209",
      "CWE-252 (반환값 미확인)",
      "CWE-390",
      "CWE-460"
    ],
    a: 1,
    e: "malloc, file open, 인증 함수 등이 실패를 반환값으로 알리는데 이를 확인하지 않으면 NULL 역참조·권한 우회 등이 발생한다. 이는 CWE-252(Unchecked Return Value)에 해당한다.",
    code: `File f = new File(path);
f.delete(); // boolean 반환값을 무시 -> 삭제 실패를 감지 못함`
  },
  {
    c: "에러처리",
    q: "아래 Java 코드에서 파일 스트림 해제와 관련한 가장 안전한 접근은?",
    o: [
      "정상 경로 끝에서만 close()를 호출한다",
      "finally 블록 또는 try-with-resources로 항상 close()가 호출되도록 한다",
      "close()를 호출하지 않고 GC에 맡긴다",
      "catch 블록에서만 close()를 호출한다"
    ],
    a: 1,
    e: "예외가 발생하면 정상 경로의 close()는 실행되지 않아 자원 누수가 생긴다(CWE-460 부적절한 정리 / CWE-404 자원 미해제). finally 블록이나 try-with-resources를 사용해 예외 여부와 무관하게 자원이 해제되도록 보장해야 한다.",
    code: `InputStream in = new FileInputStream(path);
process(in);
in.close(); // process()에서 예외 시 실행 안 됨`
  },
  {
    c: "에러처리",
    q: "Exception 또는 Throwable을 광범위하게 catch하는 것이 위험한 이유로 가장 적절한 것은?",
    o: [
      "컴파일 속도가 느려진다",
      "의도치 않은 예외(예: NPE, OutOfMemoryError)까지 삼켜 진짜 결함을 은폐한다",
      "checked 예외를 던질 수 없게 된다",
      "finally 블록이 실행되지 않는다"
    ],
    a: 1,
    e: "catch(Exception) 또는 catch(Throwable)은 예상한 특정 예외뿐 아니라 프로그래밍 오류(NullPointerException)나 심각한 오류(Error)까지 잡아 은폐한다. 이는 CWE-396(광범위한 catch)·CWE-397과 관련되며, 필요한 예외만 구체적으로 잡아야 한다.",
    code: `try {
    doWork();
} catch (Throwable t) {
    log.warn("무시");
}`
  },
  {
    c: "에러처리",
    q: "다음 코드에서 fail-safe(안전한 기본값) 원칙을 위반한 부분은?",
    o: [
      "예외 발생 시 권한을 true(허용)로 기본 설정한 것",
      "예외를 로깅한 것",
      "함수가 boolean을 반환한 것",
      "try 블록에서 DB를 조회한 것"
    ],
    a: 0,
    e: "인증/인가 검사에서 예외가 발생하면 접근을 거부(fail-secure)해야 한다. 예외 시 true를 반환하면 오류 상황이 곧 권한 우회로 이어진다. 안전한 기본값은 '거부'이며 이는 CWE-636(안전하지 않은 기본 동작)/CWE-703과 관련된다.",
    code: `boolean isAllowed(User u) {
    try {
        return acl.check(u);
    } catch (Exception e) {
        return true; // 오류 시 허용
    }
}`
  },
  {
    c: "에러처리",
    q: "'처리되지 않은 예외(CWE-248)'의 대표적 위험은?",
    o: [
      "스레드/프로세스가 비정상 종료되거나 서버가 기본 오류 페이지로 스택트레이스를 노출한다",
      "반환값이 항상 0이 된다",
      "메모리 사용량이 감소한다",
      "예외가 자동으로 재시도된다"
    ],
    a: 0,
    e: "잡히지 않은(uncaught) 예외는 스레드/프로세스를 중단시키거나, 웹 컨테이너가 기본 오류 페이지에 스택트레이스를 출력하게 만들어 가용성 저하와 정보 노출(CWE-209 연계)을 유발한다. 이것이 CWE-248(처리되지 않은 예외)이다.",
    code: ""
  },
  {
    c: "에러처리",
    q: "다음 Python 코드에서 로깅과 노출을 올바르게 분리한 방식은?",
    o: [
      "예외 상세를 사용자에게 반환하고 로그는 남기지 않는다",
      "상세는 logging으로 서버에만 남기고 사용자에게는 일반 메시지를 반환한다",
      "print(e)로 콘솔에 출력한다",
      "예외를 그대로 다시 raise해 사용자 응답으로 보낸다"
    ],
    a: 1,
    e: "민감정보 노출(CWE-209)을 막으려면 예외의 상세 내용은 logging을 통해 서버 로그에만 남기고, 사용자에게는 식별자(요청 ID) 정도만 포함한 일반화된 메시지를 반환해야 한다.",
    code: `try:
    result = do_work()
except Exception:
    logging.exception("작업 실패")
    return "요청을 처리할 수 없습니다.", 500`
  },
  {
    c: "에러처리",
    q: "C에서 시스템 호출 후 errno를 확인하지 않고 사용하는 것과 관련된 약점은?",
    o: [
      "반환값/오류 표시자(errno)를 확인하지 않음(CWE-252/CWE-391)",
      "오류 메시지 노출(CWE-209)",
      "광범위 catch(CWE-396)",
      "부적절한 정리(CWE-460)"
    ],
    a: 0,
    e: "많은 C 라이브러리 함수는 실패를 반환값과 errno로 알린다. 반환값이나 errno를 확인하지 않으면 실패를 감지하지 못해(CWE-252/CWE-391) 잘못된 데이터로 진행한다. errno는 성공 시 초기화되지 않으므로 반환값이 실패를 표시할 때에만 참조해야 한다.",
    code: ""
  },
  {
    c: "에러처리",
    q: "다음 코드에서 finally 블록의 부적절한 사용으로 발생하는 문제는?",
    o: [
      "finally에서 return이 try/catch의 예외와 반환을 덮어써 오류가 은폐된다",
      "finally는 항상 실행되지 않는다",
      "finally에서 예외를 던질 수 없다",
      "finally는 catch보다 먼저 실행된다"
    ],
    a: 0,
    e: "finally 블록의 return이나 새 예외는 try/catch에서 발생·전파되던 예외를 삼켜 오류를 은폐한다. 이는 CWE-584(finally 내 return)와 CWE-703(예외 조건의 부적절한 처리)과 관련된다. finally에서는 정리만 수행하고 제어 흐름을 바꾸지 않아야 한다.",
    code: `try {
    return compute();
} finally {
    return -1; // compute()의 예외/결과를 덮어씀
}`
  },
  {
    c: "에러처리",
    q: "웹 애플리케이션의 운영 배포 시 스택트레이스 노출을 막는 가장 적절한 조치는?",
    o: [
      "디버그 모드를 끄고 커스텀 오류 페이지로 일반 메시지만 노출한다",
      "모든 예외를 catch(Exception)로 잡아 무시한다",
      "스택트레이스를 HTML 주석으로 숨겨 응답에 포함한다",
      "예외 메시지를 그대로 사용자에게 보여준다"
    ],
    a: 0,
    e: "운영 환경에서는 프레임워크의 debug 모드를 비활성화하고, 통일된 커스텀 오류 페이지(예: 500 페이지)로 일반화된 메시지만 노출해야 한다. HTML 주석에 숨기는 것은 소스만 보면 드러나므로 여전히 CWE-209 노출이다.",
    code: ""
  },
  {
    c: "에러처리",
    q: "다음 Java 코드에서 반환값을 '부적절하게' 확인한 사례(CWE-253)는?",
    o: [
      "실패 시 음수를 반환하는 함수를 == -1로만 비교하고 그 외 오류 코드는 무시",
      "예외를 로깅한 것",
      "try-with-resources를 사용한 것",
      "일반 메시지를 반환한 것"
    ],
    a: 0,
    e: "CWE-253은 반환값을 확인은 하되 잘못된 방식으로 비교하는 경우다. 여러 오류 코드(예: 음수 전체가 실패)를 == -1 하나로만 검사하면 다른 실패값을 성공으로 오인한다. 성공/실패 판정 조건을 명세대로 정확히 검사해야 한다.",
    code: `int rc = native.read(buf);
if (rc == -1) { handleError(); }
// -2, -3 등 다른 실패 코드는 성공으로 처리됨`
  },
  {
    c: "에러처리",
    q: "예외 발생 시 자원 정리를 제대로 하지 못하는 약점(CWE-460)을 방지하는 방법으로 옳지 않은 것은?",
    o: [
      "Java의 try-with-resources 사용",
      "Python의 with 문(context manager) 사용",
      "예외를 빈 catch로 잡아 흐름을 계속 진행",
      "finally에서 획득한 자원을 역순으로 해제"
    ],
    a: 2,
    e: "빈 catch로 예외를 삼키면 오류가 은폐될 뿐 자원 정리와는 무관하며 오히려 상태를 악화시킨다(CWE-390). 자원 정리는 try-with-resources, with 문, finally 블록으로 예외 여부와 무관하게 보장해야 한다(CWE-460 예방).",
    code: ""
  },
  {
    c: "에러처리",
    q: "다음 중 CWE-703(예외적 조건의 부적절한 검사·처리)의 개념을 가장 잘 설명한 것은?",
    o: [
      "프로그램이 예외적/비정상 조건을 감지하지 못하거나 잘못 처리하는 상위 개념의 약점",
      "SQL 인젝션의 한 형태",
      "암호 알고리즘의 취약점",
      "세션 고정 공격"
    ],
    a: 0,
    e: "CWE-703은 예외적 조건(오류, 실패, 예상치 못한 입력 등)을 적절히 검사·처리하지 못하는 문제를 포괄하는 상위 카테고리다. CWE-248, CWE-252, CWE-390, CWE-391 등이 그 하위에 속한다.",
    code: ""
  },
  {
    c: "에러처리",
    q: "다음 Python bare except의 부가적 위험으로 옳은 것은?",
    o: [
      "SystemExit, KeyboardInterrupt까지 잡아 정상 종료/중단을 방해한다",
      "구문 오류가 발생한다",
      "예외가 두 번 발생한다",
      "로깅이 자동으로 활성화된다"
    ],
    a: 0,
    e: "bare except(except:)는 BaseException을 상속하는 SystemExit, KeyboardInterrupt까지 포착해 Ctrl+C나 정상 종료를 방해할 수 있다. 필요한 예외만 잡거나 최소한 except Exception:을 사용해야 한다. 무시하면 CWE-390으로도 이어진다.",
    code: `try:
    run()
except:   # KeyboardInterrupt까지 삼킴
    pass`
  },
  {
    c: "에러처리",
    q: "여러 예외 유형을 하나의 catch(Exception)로 처리할 때 권장되는 개선 방향은?",
    o: [
      "발생 가능한 예외 유형별로 구체적으로 catch하고 각기 적절히 처리한다",
      "catch(Throwable)로 범위를 더 넓힌다",
      "예외를 모두 무시한다",
      "printStackTrace로 사용자에게 출력한다"
    ],
    a: 0,
    e: "광범위 catch는 서로 다른 오류를 동일하게 처리해 복구 로직과 로깅을 부정확하게 만든다(CWE-396). 예상되는 예외를 유형별로 구체적으로 잡아 상황에 맞게 복구·전파·로깅해야 한다.",
    code: ""
  }
);
window.__QBANK.THEORY.push(
  {
    type: "OX",
    cat: "에러처리",
    q: "예외의 e.getMessage()나 스택트레이스를 사용자 응답에 그대로 반환하면 CWE-209(오류 메시지를 통한 정보 노출)에 해당한다.",
    a: true,
    e: "내부 경로, SQL 구문, 프레임워크/버전 정보 등이 노출되어 공격자에게 정찰 정보를 제공하므로 CWE-209에 해당한다. 사용자에게는 일반화된 메시지만 반환해야 한다."
  },
  {
    type: "OX",
    cat: "에러처리",
    q: "빈 catch 블록(catch(Exception e){})은 오류를 무시하므로 안전한 방어적 코딩 기법이다.",
    a: false,
    e: "빈 catch는 오류를 은폐하여 프로그램이 잘못된 상태로 계속 실행되게 만든다. 이는 CWE-390(오류 조건 감지 후 조치 없음) 약점이며 방어적 코딩이 아니다."
  },
  {
    type: "OX",
    cat: "에러처리",
    q: "인증/인가 검사 중 예외가 발생하면 접근을 '거부'하는 것이 안전한 기본값(fail-secure)이다.",
    a: true,
    e: "예외 상황에서 접근을 허용(fail-open)하면 오류가 곧 권한 우회로 이어진다. 안전한 기본값은 거부이며, 이를 어기면 CWE-636/CWE-703 관련 약점이 된다."
  },
  {
    type: "OX",
    cat: "에러처리",
    q: "Python의 bare except(except:)는 SystemExit와 KeyboardInterrupt까지 포착할 수 있다.",
    a: true,
    e: "bare except는 BaseException 계열까지 잡으므로 Ctrl+C(KeyboardInterrupt)와 정상 종료(SystemExit)를 방해할 수 있다. except Exception: 또는 구체적 예외 사용이 권장된다."
  },
  {
    type: "OX",
    cat: "에러처리",
    q: "finally 블록에서 return을 사용하면 try/catch에서 전파되던 예외가 은폐될 수 있다.",
    a: true,
    e: "finally의 return은 try/catch에서 던져지던 예외나 반환값을 덮어써 오류를 은폐한다(CWE-584/CWE-703). finally에서는 정리만 하고 제어 흐름을 바꾸지 말아야 한다."
  },
  {
    type: "OX",
    cat: "에러처리",
    q: "잡히지 않은 예외(uncaught exception)는 웹 서버가 기본 오류 페이지로 스택트레이스를 노출하게 만들 수 있다.",
    a: true,
    e: "처리되지 않은 예외(CWE-248)는 컨테이너의 기본 오류 처리로 넘어가 스택트레이스를 노출(CWE-209 연계)하거나 스레드를 중단시킬 수 있다."
  },
  {
    type: "OX",
    cat: "에러처리",
    q: "catch(Throwable)는 catch(Exception)보다 안전하므로 항상 권장된다.",
    a: false,
    e: "Throwable은 Error(OutOfMemoryError 등)까지 포함해 복구 불가능한 심각한 오류까지 삼킨다. 광범위 catch는 오히려 CWE-396 약점이며 권장되지 않는다. 필요한 예외만 구체적으로 잡아야 한다."
  },
  {
    type: "SHORT",
    cat: "에러처리",
    q: "오류 메시지나 스택트레이스로 내부 민감정보가 노출되는 보안약점의 CWE 번호를 쓰시오. (예: CWE-000)",
    a: "CWE-209",
    answers: ["CWE-209", "209", "cwe-209"],
    e: "CWE-209는 오류 메시지를 통한 정보 노출(Information Exposure Through an Error Message)이다."
  },
  {
    type: "SHORT",
    cat: "에러처리",
    q: "예외를 잡은 후 아무런 조치(로깅/복구/전파)도 하지 않는, 빈 catch로 대표되는 보안약점의 CWE 번호를 쓰시오.",
    a: "CWE-390",
    answers: ["CWE-390", "390", "cwe-390"],
    e: "CWE-390은 오류 조건을 감지했으나 조치하지 않음(Detection of Error Condition Without Action)이다. 빈 catch, except: pass가 대표 예다."
  },
  {
    type: "SHORT",
    cat: "에러처리",
    q: "함수의 반환값을 확인하지 않아 실패를 성공으로 오인하는 보안약점의 CWE 번호를 쓰시오.",
    a: "CWE-252",
    answers: ["CWE-252", "252", "cwe-252"],
    e: "CWE-252는 반환값 미확인(Unchecked Return Value)이다. malloc/파일열기/인증 함수 등의 실패 반환을 무시하면 발생한다."
  },
  {
    type: "SHORT",
    cat: "에러처리",
    q: "Java에서 예외 여부와 무관하게 자원(파일, 소켓 등)을 자동으로 닫아 주는 구문 이름을 쓰시오.",
    a: "try-with-resources",
    answers: ["try-with-resources", "try with resources", "트라이 위드 리소스", "try(자원)"],
    e: "try-with-resources는 AutoCloseable 자원을 선언하면 블록 종료 시 예외 여부와 무관하게 close()를 호출해 CWE-460/CWE-404를 예방한다."
  },
  {
    type: "SHORT",
    cat: "에러처리",
    q: "예외적/비정상 조건의 부적절한 검사·처리를 포괄하는 상위 CWE 카테고리 번호를 쓰시오.",
    a: "CWE-703",
    answers: ["CWE-703", "703", "cwe-703"],
    e: "CWE-703은 예외적 조건의 부적절한 검사 또는 처리(Improper Check or Handling of Exceptional Conditions)로, CWE-248/252/390/391 등의 상위 카테고리다."
  },
  {
    type: "MC",
    cat: "에러처리",
    q: "다음 중 '처리되지 않은 예외'를 가리키는 CWE는?",
    o: ["CWE-209", "CWE-248", "CWE-252", "CWE-390"],
    a: 1,
    e: "CWE-248은 처리되지 않은 예외(Uncaught Exception)로, 잡히지 않은 예외가 프로세스 중단이나 스택트레이스 노출을 유발한다."
  },
  {
    type: "MC",
    cat: "에러처리",
    q: "Python에서 예외 상세를 노출하지 않으면서 서버 측에 기록하기 위한 가장 적절한 방법은?",
    o: [
      "print(e)로 콘솔에 출력",
      "logging.exception()으로 로그에 남기고 사용자에게는 일반 메시지 반환",
      "예외를 사용자 응답 본문에 그대로 반환",
      "except: pass로 무시"
    ],
    a: 1,
    e: "logging.exception()은 스택트레이스를 서버 로그에만 기록한다. 사용자에게는 일반화된 메시지만 반환해야 CWE-209 노출을 막는다."
  },
  {
    type: "MC",
    cat: "에러처리",
    q: "반환값을 확인은 하지만 성공/실패 판정 조건을 잘못 비교해 일부 실패를 성공으로 처리하는 약점의 CWE는?",
    o: ["CWE-252", "CWE-253", "CWE-391", "CWE-460"],
    a: 1,
    e: "CWE-253은 반환값의 부적절한 확인(Incorrect Check of Function Return Value)이다. 실패 코드 전체를 검사하지 않고 특정 값 하나로만 비교하는 경우가 해당된다."
  },
  {
    type: "MC",
    cat: "에러처리",
    q: "다음 중 광범위한 예외 포착(catch(Exception)/catch(Throwable)) 남용의 문제로 옳지 않은 것은?",
    o: [
      "프로그래밍 오류(NPE)까지 삼켜 결함이 은폐된다",
      "서로 다른 오류를 동일하게 처리해 복구 로직이 부정확해진다",
      "Error 등 복구 불가능한 심각한 오류까지 잡을 수 있다",
      "checked 예외를 컴파일 시점에 강제로 처리하게 만들어 안전해진다"
    ],
    a: 3,
    e: "광범위 catch는 결함 은폐, 부정확한 복구, 심각한 오류 포착 등의 문제를 낳는다(CWE-396). 컴파일 안전성을 높이는 것과는 무관하며 오히려 구체적 예외 처리를 회피하게 만든다."
  },
  {
    type: "OX",
    cat: "에러처리",
    q: "C에서 errno는 함수가 성공한 경우에도 이전 값이 남아 있을 수 있으므로, 반환값이 실패를 표시할 때에만 참조해야 한다.",
    a: true,
    e: "errno는 성공 시 0으로 초기화되지 않는다. 따라서 함수의 반환값이 실패를 나타낼 때에만 errno를 확인해야 하며, 그렇지 않으면 오탐이 생긴다(CWE-391 관련)."
  }
);
