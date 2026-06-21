# -*- coding: utf-8 -*-

PART = [

    # ============================================================
    # PC-21 (하, TP) 부적절한 예외 처리 - 광범위한 except
    # ============================================================
    {'id':'PC-21','lang':'Python','cat':'에러처리','diff':'하',
     'title':'설정 파일 읽기 처리의 예외 구문 검토',
     'code':'''def get_content():
    try:
        f = open('myfile.txt')
        s = f.readline()
        i = int(s.strip())
    except:
        print("Unexpected error ")''',
     'isTruePositive':True,'weaknessName':'부적절한 예외 처리','cwe':'CWE-755',
     'reasonKeywords':['except','광범위한 예외','세분화 미흡','오류 은폐'],
     'negKw':['부적절한 자원 해제','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''def get_content():
    try:
        f = open('myfile.txt')
        s = f.readline()
        i = int(s.strip())
    except FileNotFoundError:
        print("file is not found")
    except OSError:
        print("cannot open file")
    except ValueError:
        print("Could not convert data to an integer.")''',
     'safeCodeKeywords':['except FileNotFoundError','except OSError','except ValueError'],
     'explanation':'발생 가능한 오류 종류를 세분화할 수 있음에도 except로 모든 예외를 광범위하게 처리하여 서로 다른 오류를 구분하지 못하고 문제를 은폐하므로 부적절한 예외 처리에 해당합니다. 오류 종류별로 예외를 세분화해 처리해야 합니다.'},

    # ============================================================
    # PC-22 (중, TP) 부적절한 자원 해제 - 예외 시 close 미실행
    # ============================================================
    {'id':'PC-22','lang':'Java','cat':'코드오류','diff':'중',
     'title':'파일 복사 처리의 자원 반환 흐름 검토',
     'code':'''InputStream in = null;
OutputStream out = null;
try {
    in = new FileInputStream(inputFile);
    out = new FileOutputStream(outputFile);
    FileCopyUtils.copy(in, out);
    in.close();
    out.close();
} catch (IOException e) {
    logger.error(e);
}''',
     'isTruePositive':True,'weaknessName':'부적절한 자원 해제','cwe':'CWE-404',
     'reasonKeywords':['close','예외 발생 시 미반환','finally 없음','자원 누수'],
     'negKw':['부적절한 예외 처리','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''InputStream in = null;
OutputStream out = null;
try {
    in = new FileInputStream(inputFile);
    out = new FileOutputStream(outputFile);
    FileCopyUtils.copy(in, out);
} catch (IOException e) {
    logger.error(e);
} finally {
    if (in != null) {
        try { in.close(); } catch (IOException e) { logger.error(e); }
    }
    if (out != null) {
        try { out.close(); } catch (IOException e) { logger.error(e); }
    }
}''',
     'safeCodeKeywords':['finally','in.close()','out.close()'],
     'explanation':'close()를 try 블록 끝에서 호출하므로 copy 도중 예외가 발생하면 자원이 반환되지 않아 자원 누수가 생기는 부적절한 자원 해제에 취약합니다. 항상 실행되는 finally 블록에서 모든 자원을 해제해야 합니다.'},

    # ============================================================
    # PC-23 (중, TP) 해제된 자원 사용 - free 후 사용 (C)
    # ============================================================
    {'id':'PC-23','lang':'C','cat':'코드오류','diff':'중',
     'title':'동적 메모리 사용 순서의 안전성 검토',
     'code':'''int main(int argc, const char *argv[]) {
    char *temp;
    temp = (char *)malloc(BUFFER_SIZE);
    /* ... */
    free(temp);
    strncpy(temp, argv[1], BUFFER_SIZE-1);
}''',
     'isTruePositive':True,'weaknessName':'해제된 자원 사용','cwe':'CWE-416',
     'reasonKeywords':['free','해제 후 사용','dangling pointer','strncpy'],
     'negKw':['부적절한 자원 해제','버퍼 오버플로우','안전한 코드','취약하지 않'],
     'safeCode':'''int main(int argc, const char *argv[]) {
    char *temp;
    temp = (char *)malloc(BUFFER_SIZE);
    /* ... */
    strncpy(temp, argv[1], BUFFER_SIZE-1);
    free(temp);
}''',
     'safeCodeKeywords':['strncpy','free(temp)','malloc'],
     'explanation':'free()로 메모리를 해제한 뒤 같은 포인터 temp에 strncpy로 접근하므로 이미 해제된 자원을 사용하는(use-after-free) 취약점입니다. 자원은 최종 사용을 모두 마친 뒤 마지막에 해제해야 합니다.'},

    # ============================================================
    # PC-24 (하, TP) 초기화되지 않은 변수 사용 (C)
    # ============================================================
    {'id':'PC-24','lang':'C','cat':'코드오류','diff':'하',
     'title':'커서 좌표 계산 분기 로직 검토',
     'code':'''int x, y;
switch(position) {
    case 0: x = base_position; y = base_position; break;
    case 1: x = base_position + i; y = base_position - i; break;
    default: x = 1; break;
}
setCursorPosition(x, y);''',
     'isTruePositive':True,'weaknessName':'초기화되지 않은 변수 사용','cwe':'CWE-457',
     'reasonKeywords':['초기값 없음','default 분기','y 미초기화','쓰레기 값'],
     'negKw':['해제된 자원 사용','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''int x = 1, y = 1;
switch(position) {
    case 0: x = base_position; y = base_position; break;
    case 1: x = base_position + i; y = base_position - i; break;
    default: x = 1; break;
}
setCursorPosition(x, y);''',
     'safeCodeKeywords':['int x = 1, y = 1','switch','setCursorPosition'],
     'explanation':'default 분기에서는 y에 값이 할당되지 않아 초기화되지 않은 변수의 쓰레기 값이 그대로 사용되며, 이는 예측 불가능한 동작이나 공격에 악용될 수 있습니다. 변수는 선언 시 항상 초기값을 지정해야 합니다.'},

    # ============================================================
    # PC-25 (중, TP) 잘못된 세션에 의한 데이터 정보 노출 - 멤버 변수 공유
    # ============================================================
    {'id':'PC-25','lang':'Java','cat':'캡슐화','diff':'중',
     'title':'컨트롤러의 페이지 상태 보관 방식 검토',
     'code':'''@Controller
public class TrendForecastController {
    private int currentPage = 1;
    public void doSomething(HttpServletRequest request) {
        currentPage = Integer.parseInt(request.getParameter("page"));
    }
}''',
     'isTruePositive':True,'weaknessName':'잘못된 세션에 의한 데이터 정보 노출','cwe':'CWE-488',
     'reasonKeywords':['멤버 변수','싱글톤 컨트롤러','스레드 공유','세션 간 노출'],
     'negKw':['부적절한 인가','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''@Controller
public class TrendForecastController {
    public void doSomething(HttpServletRequest request) {
        int currentPage = Integer.parseInt(request.getParameter("page"));
    }
}''',
     'safeCodeKeywords':['int currentPage','getParameter','doSomething'],
     'explanation':'싱글톤으로 동작하는 컨트롤러에서 요청별 값을 인스턴스 멤버 변수에 저장하므로 여러 스레드(세션)가 같은 변수를 공유하여 다른 사용자의 데이터가 노출될 수 있습니다. 요청별 값은 지역변수로 처리해야 합니다.'},

    # ============================================================
    # PC-26 (중, TP) Public 메소드로부터 반환된 Private 배열
    # ============================================================
    {'id':'PC-26','lang':'Java','cat':'캡슐화','diff':'중',
     'title':'색상 목록 접근자 메소드의 반환 방식 검토',
     'code':'''private String[] colors;
public String[] getColors() {
    return colors;
}''',
     'isTruePositive':True,'weaknessName':'Public 메소드로부터 반환된 Private 배열','cwe':'CWE-495',
     'reasonKeywords':['private 배열','참조 반환','복제본 아님','외부 수정 가능'],
     'negKw':['Private 배열에 Public 데이터 할당','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''private String[] colors;
public String[] getColors() {
    String[] ret = null;
    if (this.colors != null) {
        ret = new String[colors.length];
        for (int i = 0; i < colors.length; i++) { ret[i] = this.colors[i]; }
    }
    return ret;
}''',
     'safeCodeKeywords':['new String[colors.length]','this.colors[i]','ret[i]'],
     'explanation':'public 메소드가 private 배열의 참조를 그대로 반환하므로 호출자가 내부 배열 원소를 직접 수정할 수 있어 캡슐화가 깨집니다. 배열 복제본을 만들어 반환해야 합니다.'},

    # ============================================================
    # PC-27 (중, TP) Private 배열에 Public 데이터 할당
    # ============================================================
    {'id':'PC-27','lang':'Java','cat':'캡슐화','diff':'중',
     'title':'사용자 권한 배열 설정 메소드 검토',
     'code':'''private String[] userRoles;
public void setUserRoles(String[] userRoles) {
    this.userRoles = userRoles;
}''',
     'isTruePositive':True,'weaknessName':'Private 배열에 Public 데이터 할당','cwe':'CWE-496',
     'reasonKeywords':['외부 배열 직접 할당','참조 공유','private 무력화','외부 수정 가능'],
     'negKw':['Public 메소드로부터 반환된 Private 배열','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''private String[] userRoles;
public void setUserRoles(String[] userRoles) {
    this.userRoles = new String[userRoles.length];
    for (int i = 0; i < userRoles.length; ++i)
        this.userRoles[i] = userRoles[i];
}''',
     'safeCodeKeywords':['new String[userRoles.length]','for (int i','this.userRoles[i]'],
     'explanation':'public setter가 외부에서 넘어온 배열의 참조를 private 필드에 그대로 할당하므로 외부에서 같은 배열을 수정하면 내부 상태가 바뀌어 사실상 public 필드처럼 됩니다. 원소를 복사하여 할당해야 합니다.'},

    # ============================================================
    # PC-28 (상, TP) DNS lookup에 의존한 보안 결정
    # ============================================================
    {'id':'PC-28','lang':'Java','cat':'API오용','diff':'상',
     'title':'신뢰 시스템 판별을 위한 호스트 검사 로직 검토',
     'code':'''public void doGet(HttpServletRequest req, HttpServletResponse res)
        throws ServletException, IOException {
    boolean trusted = false;
    String ip = req.getRemoteAddr();
    InetAddress addr = InetAddress.getByName(ip);
    if (addr.getCanonicalHostName().endsWith("trustme.com")) {
        do_something_for_Trust_System();
    }
}''',
     'isTruePositive':True,'weaknessName':'DNS lookup에 의존한 보안 결정','cwe':'CWE-350',
     'reasonKeywords':['getCanonicalHostName','DNS 역조회','도메인 신뢰','DNS 변조'],
     'negKw':['부적절한 인가','SSRF','안전한 코드','취약하지 않'],
     'safeCode':'''public void doGet(HttpServletRequest req, HttpServletResponse res)
        throws ServletException, IOException {
    String ip = req.getRemoteAddr();
    if (ip == null || "".equals(ip)) return;
    String trustedAddr = "127.0.0.1";
    if (ip.equals(trustedAddr)) {
        do_something_for_Trust_System();
    }
}''',
     'safeCodeKeywords':['ip.equals','trustedAddr','getRemoteAddr'],
     'explanation':'DNS 역조회로 얻은 도메인 이름(getCanonicalHostName)이 특정 도메인으로 끝나는지로 신뢰 여부를 결정하는데, 공격자가 자신의 서버 DNS를 조작해 우회할 수 있으므로 안전하지 않습니다. 실제 IP 주소를 직접 비교해야 합니다.'},

    # ============================================================
    # PC-29 (하, TP) 취약한 API 사용 - gets() (C)
    # ============================================================
    {'id':'PC-29','lang':'C','cat':'API오용','diff':'하',
     'title':'문자열 입력 처리 함수 사용의 안전성 검토',
     'code':'''#include <stdio.h>
void requestString()
{
    char str[100];
    gets(str);
}''',
     'isTruePositive':True,'weaknessName':'취약한 API 사용','cwe':'CWE-676',
     'reasonKeywords':['gets','길이 제한 불가','금지된 함수','버퍼 오버플로우'],
     'negKw':['초기화되지 않은 변수 사용','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''#include <stdio.h>
void requestString()
{
    char str[100];
    gets_s(str, sizeof(str));
}''',
     'safeCodeKeywords':['gets_s','sizeof(str)','char str[100]'],
     'explanation':'gets() 함수는 입력 문자열의 길이를 제한할 수 없어 버퍼 오버플로우를 유발하는 사용이 금지된 취약한 API입니다. 길이 제한이 가능한 gets_s() 등 안전한 대체 함수를 사용해야 합니다.'},
]
