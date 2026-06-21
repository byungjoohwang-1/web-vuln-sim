# -*- coding: utf-8 -*-
"""기초 과정 — 진단원이 코드를 읽고 정·오탐을 판별하려면 먼저 Java/C/Python 기본을 알아야 한다.
각 항목: lang / topic / desc(개념) / code(예제) / sec(보안 진단과의 연결).
academy의 '기초 과정' 탭에서 언어별로 렌더.
"""

BASICS = [
    # ===================== Java =====================
    {'lang':'Java','topic':'변수와 자료형','desc':'Java는 정적 타입 언어로 변수 선언 시 자료형을 명시한다. 기본형(int, long, double, boolean, char)과 참조형(String, 배열, 객체)이 있다.',
     'code':'int age = 30;\nlong big = 10_000_000_000L;\ndouble rate = 0.75;\nboolean ok = true;\nString name = "홍길동";',
     'sec':'정수형은 표현 범위가 있어 한계를 넘으면 "정수형 오버플로우"가 발생한다. 입력을 자료형으로 바꿀 때(parseInt 등) 범위·예외 검증이 진단 포인트다.'},
    {'lang':'Java','topic':'제어문과 반복','desc':'조건 분기는 if/else·switch, 반복은 for/while로 표현한다. 조건식의 참/거짓에 따라 실행 흐름이 갈린다.',
     'code':'if (user.isAdmin()) {\n    grantAccess();\n} else {\n    denyAccess();\n}\nfor (int i = 0; i < items.size(); i++) {\n    process(items.get(i));\n}',
     'sec':'인가(권한) 검사는 if 분기로 구현된다. 이 분기가 서버에서 수행되는지, 우회 가능한지가 "부적절한 인가" 진단의 핵심이다.'},
    {'lang':'Java','topic':'메소드','desc':'메소드는 입력(매개변수)을 받아 처리하고 값을 반환(return)하는 코드 단위다. 접근제어자(public/private)로 외부 노출 범위를 정한다.',
     'code':'public int add(int a, int b) {\n    return a + b;\n}\nprivate String[] secretKeys() {\n    return this.keys;\n}',
     'sec':'public 메소드가 내부 private 배열을 그대로 반환하면 외부에서 내부 상태를 바꿀 수 있다("Public 메소드로부터 반환된 Private 배열"). 복사본 반환이 안전하다.'},
    {'lang':'Java','topic':'클래스와 객체','desc':'클래스는 데이터(필드)와 동작(메소드)을 묶은 설계도이고, 객체는 그 인스턴스다. 캡슐화로 내부 데이터를 보호한다.',
     'code':'public class Account {\n    private long balance;          // 외부 직접 접근 차단\n    public void deposit(long amt) {\n        if (amt > 0) balance += amt;\n    }\n}',
     'sec':'중요 필드를 public으로 노출하거나 검증 없이 변경하게 두면 "캡슐화" 유형 약점이 된다. private + 검증 메소드가 기본이다.'},
    {'lang':'Java','topic':'예외 처리','desc':'오류 상황은 예외(Exception)로 표현되며 try-catch-finally로 처리한다. finally는 예외 여부와 무관하게 항상 실행된다.',
     'code':'try {\n    conn = open();\n    use(conn);\n} catch (IOException e) {\n    logger.error("ERROR-01");   // 최소 정보만\n} finally {\n    if (conn != null) conn.close();   // 자원 해제\n}',
     'sec':'예외를 너무 광범위하게 잡거나(빈 catch) 스택을 사용자에게 노출하면 "에러처리" 유형 약점이다. 자원은 finally에서 해제해야 "자원 해제" 약점을 막는다.'},
    {'lang':'Java','topic':'외부 입력과 DB 접근','desc':'웹에서 외부 입력은 HttpServletRequest로 들어온다. DB 질의는 Statement(문자열 결합) 대신 PreparedStatement(파라미터 바인딩)로 작성한다.',
     'code':'String id = request.getParameter("id");          // 외부 입력(신뢰 불가)\nPreparedStatement ps = conn.prepareStatement(\n    "SELECT * FROM users WHERE id = ?");\nps.setString(1, id);                              // 안전한 바인딩\nps.executeQuery();',
     'sec':'외부 입력을 문자열로 SQL에 결합하면 "SQL 삽입"이다. PreparedStatement + setXxx 바인딩 구조가 정탐/오탐 판별의 1순위 단서다.'},

    # ===================== C =====================
    {'lang':'C','topic':'변수와 자료형','desc':'C는 하드웨어에 가까운 언어로 자료형 크기가 메모리에 직접 대응한다(int, char, long, float). 초기화하지 않은 변수는 쓰레기 값을 가진다.',
     'code':'int count = 0;        /* 반드시 초기화 */\nchar grade = \'A\';\nlong total = 0L;\nunsigned int size = 10u;',
     'sec':'초기화하지 않고 사용하면 "초기화되지 않은 변수 사용" 약점이 된다. 선언과 동시에 안전한 기본값을 주는지 확인한다.'},
    {'lang':'C','topic':'포인터','desc':'포인터는 메모리 주소를 담는 변수다. * 로 가리키는 값에 접근(역참조)하고, & 로 주소를 얻는다. NULL 포인터 역참조는 비정상 종료를 일으킨다.',
     'code':'int x = 10;\nint *p = &x;     /* p는 x의 주소 */\nprintf("%d", *p); /* 역참조: 10 */\nif (p != NULL) { *p = 20; }  /* NULL 검사 후 사용 */',
     'sec':'NULL 또는 해제된 주소를 역참조하면 "Null Pointer 역참조"·"해제된 자원 사용" 약점이다. 사용 전 NULL 검사, free 후 재사용 금지가 진단 포인트다.'},
    {'lang':'C','topic':'배열과 문자열','desc':'C 문자열은 널 문자(\\0)로 끝나는 char 배열이다. 배열 경계를 넘어 쓰면 인접 메모리가 손상된다(버퍼 오버플로우).',
     'code':'char buf[16];\n/* 위험: strcpy(buf, src);  경계 검사 없음 */\nstrncpy(buf, src, sizeof(buf) - 1);   /* 대상 크기만큼만 */\nbuf[sizeof(buf) - 1] = \'\\0\';           /* 널 종료 보장 */',
     'sec':'대상 버퍼 크기를 넘겨 복사하면 "메모리 버퍼 오버플로우"다. strcpy/gets 대신 strncpy/snprintf 등 크기를 받는 안전 API 사용이 핵심 단서다.'},
    {'lang':'C','topic':'동적 메모리','desc':'malloc으로 힙 메모리를 할당하고 free로 해제한다. 해제 후에는 그 포인터를 다시 쓰면 안 되며, 해제하지 않으면 누수가 된다.',
     'code':'char *temp = (char *)malloc(BUFFER_SIZE);\nif (temp != NULL) {\n    strncpy(temp, src, BUFFER_SIZE - 1);\n    free(temp);     /* 마지막 사용 이후 해제 */\n    temp = NULL;    /* 재사용 방지 */\n}',
     'sec':'free 후 사용은 "해제된 자원 사용", 해제 누락은 "부적절한 자원 해제"다. 할당-사용-해제 순서와 해제 후 NULL 처리를 확인한다.'},
    {'lang':'C','topic':'함수와 재귀','desc':'함수는 작업 단위이며 자기 자신을 호출(재귀)할 수 있다. 재귀는 반드시 종료 조건(기저 사례)이 있어야 무한 반복을 피한다.',
     'code':'int factorial(int n) {\n    if (n <= 1) return 1;   /* 종료 조건(기저 사례) */\n    return n * factorial(n - 1);\n}',
     'sec':'종료 조건이 없거나 잘못되면 "종료되지 않는 반복문/재귀함수"로 스택 고갈이 발생한다. 기저 사례 존재 여부가 진단 포인트다.'},
    {'lang':'C','topic':'표준 입출력과 위험 함수','desc':'C 표준 라이브러리에는 경계를 검사하지 않는 위험 함수(gets, strcpy, sprintf, scanf "%s")가 있다. 크기를 받는 안전 버전으로 대체한다.',
     'code':'char str[100];\n/* 위험: gets(str);  입력 길이 무제한 */\nfgets(str, sizeof(str), stdin);   /* 크기 제한 */\n/* 또는 gets_s(str, sizeof(str)); */',
     'sec':'gets 등 폐기·위험 API 사용은 "취약한 API 사용"이다. 안전 대체 함수(fgets/gets_s/strncpy) 사용 여부가 정탐/오탐을 가른다.'},

    # ===================== Python =====================
    {'lang':'Python','topic':'변수와 자료형','desc':'Python은 동적 타입 언어로 변수에 타입을 명시하지 않는다. 숫자(int/float), 문자열(str), 불리언(bool) 등이 있고 타입은 실행 중 결정된다.',
     'code':'age = 30            # int\nrate = 0.75         # float\nname = "홍길동"      # str\nok = True           # bool\nitems = [1, 2, 3]   # list',
     'sec':'동적 타입이라 외부 입력이 예상과 다른 타입/형식일 수 있다. 입력 검증(형식·범위) 없이 사용하면 "입력검증" 유형 약점으로 이어진다.'},
    {'lang':'Python','topic':'제어문과 함수','desc':'들여쓰기로 블록을 구분한다. 조건은 if/elif/else, 반복은 for/while, 함수는 def로 정의한다.',
     'code':'def check_password(pw):\n    import re\n    pattern = re.compile(r"^(?=.*[A-Za-z])(?=.*\\d).{8,}$")\n    return bool(pattern.match(pw))\n\nif check_password(user_pw):\n    register()',
     'sec':'비밀번호 길이·복잡도 검증 정규식 같은 "보안기능"이 함수로 구현된다. 규칙이 충분한지(길이 8+ 등)가 "취약한 비밀번호 허용" 진단 포인트다.'},
    {'lang':'Python','topic':'자료구조(list·dict·set)','desc':'list(순서 있는 목록), dict(키-값), set(중복 없는 집합)이 핵심 컬렉션이다. 허용 목록(화이트리스트) 검증에 set/dict를 많이 쓴다.',
     'code':'ALLOWED_HOSTS = {"img.example.com", "cdn.example.com"}\nhost = urlparse(url).hostname\nif host not in ALLOWED_HOSTS:\n    raise ValueError("not allowed")',
     'sec':'허용 목록(set) 기반 검증은 SSRF·오픈 리다이렉트 방어의 핵심 구조다. "허용된 것만 통과"하는지가 정탐/오탐을 가른다.'},
    {'lang':'Python','topic':'모듈과 예외','desc':'import로 모듈을 가져온다. 예외는 try/except로 처리하되, 광범위한 except가 아니라 구체적 예외를 잡는다.',
     'code':'try:\n    i = int(s.strip())\nexcept ValueError:        # 구체적 예외\n    print("숫자가 아닙니다")\nexcept FileNotFoundError:\n    print("파일 없음")',
     'sec':'bare except(또는 except Exception)로 모두 삼키면 "부적절한 예외 처리"다. 예외를 구체적으로 구분·대응하는지가 진단 포인트다.'},
    {'lang':'Python','topic':'외부 명령과 위험 함수','desc':'eval/exec는 문자열을 코드로 실행해 매우 위험하다. 외부 명령은 os.system(셸 경유) 대신 subprocess를 인자 리스트로 실행한다.',
     'code':'# 위험: eval(user_input) / os.system(cmd)\nimport ast, subprocess\nval = ast.literal_eval(user_input)        # 안전한 평가\nsubprocess.run(["ping", "-c", "1", host]) # 셸 미경유(리스트)',
     'sec':'eval/exec에 외부 입력 → "코드 삽입", os.system에 입력 결합 → "운영체제 명령어 삽입". ast.literal_eval·subprocess 리스트 형태가 안전 단서다.'},
    {'lang':'Python','topic':'직렬화와 암호','desc':'객체 저장/복원(직렬화)에 pickle은 위험하고 json이 안전하다. 비밀번호는 평문/단순해시 대신 솔트+적응형 해시로 저장한다.',
     'code':'import json, bcrypt\nobj = json.loads(data)                 # pickle 대신 json\nhashed = bcrypt.hashpw(pw.encode(),\n                       bcrypt.gensalt())  # 솔트+적응형',
     'sec':'pickle.loads(외부데이터) → "신뢰할 수 없는 역직렬화", 솔트 없는 단순 해시 → "솔트 없이 일방향 해시"·"취약한 암호화". json·bcrypt 사용이 안전 단서다.'},
]
