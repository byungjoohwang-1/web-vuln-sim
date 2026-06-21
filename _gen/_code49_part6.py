# -*- coding: utf-8 -*-
PART = {
  '오류 메시지 정보 노출': {
    'javaLang': 'Java',
    'javaVuln': '''try {
    rd = new BufferedReader(new FileReader(new File(filename)));
} catch(IOException e) {
    // 에러 메시지로 스택 정보가 노출됨
    e.printStackTrace();
}''',
    'javaSafe': '''try {
    rd = new BufferedReader(new FileReader(new File(filename)));
} catch(IOException e) {
    // 에러 코드와 정보를 별도로 정의하고 최소 정보만 로깅
    logger.error("ERROR-01: 파일 열기 에러");
}''',
    'pyVuln': '''import traceback
def fetch_url(url, useragent, referer=None, retries=1, dimension=False):
    ......
    try:
        response = requests.get(
            url,
            stream=True,
            timeout=5,
            headers={ 'User-Agent': useragent, 'Referer': referer },
        )
        ......
    except IOError:
        # 에러메시지를 통해 스택 정보가 노출.
        traceback.print_exc()''',
    'pySafe': '''import logging
def fetch_url(url, useragent, referer=None, retries=1, dimension=False):
    ......
    try:
        response = requests.get(url, stream=True, timeout=5, headers={
            'User-Agent': useragent,
            'Referer': referer,
        })
        ......
    except IOError:
        # 에러 코드와 정보를 별도로 정의하고 최소 정보만 로깅
        logger.error('ERROR-01:통신에러')''',
    'note': '',
  },
  '오류 상황 대응 부재': {
    'javaLang': 'Java',
    'javaVuln': '''protected Element createContent(WebSession s) {
    ......
    try {
        username = s.getParser().getRawParameter(USERNAME);
        password = s.getParser().getRawParameter(PASSWORD);
        if (!"webgoat".equals(username) || !password.equals("webgoat")) {
            s.setMessage("Invalid username and password entered.");
            return (makeLogin(s));
        }
    } catch (NullPointerException e) {
        // PASSWORD가 없으면 NullPointerException이 발생하나 대응이 없어
        // 인증이 된 것으로 처리됨
    }''',
    'javaSafe': '''protected Element createContent(WebSession s) {
    ......
    try {
        username = s.getParser().getRawParameter(USERNAME);
        password = s.getParser().getRawParameter(PASSWORD);
        if (!"webgoat".equals(username) || !password.equals("webgoat")) {
            s.setMessage("Invalid username and password entered.");
            return (makeLogin(s));
        }
    } catch (NullPointerException e) {
        // 예외 사항에 대해 적절한 조치를 수행하여야 한다.
        s.setMessage(e.getMessage());
        return (makeLogin(s));
    }''',
    'pyVuln': '''from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
static_keys = [{'key': b'1111111111111111', 'iv': b'2222222222222222'}]  # 등록된 키 목록
def encryption(key_id, plain_text):
    static_key = {'key':b'0000000000000000', 'iv':b'0000000000000000'}
    try:
        static_key = static_keys[key_id]
    except IndexError:
        # [취약] 오류를 pass로 무시 → 기본 약한 키 '0000...'로 암호화 수행(오류 상황 대응 부재)
        pass
    cipher_aes = AES.new(static_key['key'], AES.MODE_CBC, static_key['iv'])
    encrypted_data = base64.b64encode(cipher_aes.encrypt(pad(plain_text.encode(), 16)))
    return encrypted_data.decode('ASCII')''',
    'pySafe': '''from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64, secrets
static_keys = [{'key': b'1111111111111111', 'iv': b'2222222222222222'}]
def encryption(key_id, plain_text):
    static_key = {'key':b'0000000000000000', 'iv':b'0000000000000000'}
    try:
        static_key = static_keys[key_id]
    except IndexError:
        # [안전] 오류 상황에 대응: 약한 기본 키 대신 안전한 난수 키를 생성해 등록
        static_key = {'key': secrets.token_bytes(16), 'iv': secrets.token_bytes(16)}
        static_keys.append(static_key)
    cipher_aes = AES.new(static_key['key'], AES.MODE_CBC, static_key['iv'])
    encrypted_data = base64.b64encode(cipher_aes.encrypt(pad(plain_text.encode(), 16)))
    return encrypted_data.decode('ASCII')''',
    'note': '',
  },
  '부적절한 예외 처리': {
    'javaLang': 'Java',
    'javaVuln': '''try {
    ...
    reader = new BufferedReader(new InputStreamReader(url.openStream()));
    String line = reader.readLine();
    SimpleDateFormat format = new SimpleDateFormat("MM/DD/YY");
    Date date = format.parse(line);
    // 예외처리를 세분화 할 수 있음에도 광범위하게 사용하여 문제 발생 가능
} catch (Exception e) {
    System.err.println("Exception : " + e.getMessage());
}''',
    'javaSafe': '''try {
    ...
    reader = new BufferedReader(new InputStreamReader(url.openStream()));
    String line = reader.readLine();
    SimpleDateFormat format = new SimpleDateFormat("MM/DD/YY");
    Date date = format.parse(line);
    // 발생할 수 있는 오류의 종류와 순서에 맞춰서 예외 처리 한다.
} catch (MalformedURLException e) {
    System.err.println("MalformedURLException : " + e.getMessage());
} catch (IOException e) {
    System.err.println("IOException : " + e.getMessage());
} catch (ParseException e) {
    System.err.println("ParseException : " + e.getMessage());
}''',
    'pyVuln': '''import sys
def get_content():
    try:
        f = open('myfile.txt')
        s = f.readline()
        i = int(s.strip())
    # 예외처리를 세분화 할 수 있음에도 광범위하게 사용하여
    # 예기치 않은 문제가 발생할 수 있다
    except:
        print("Unexpected error ")''',
    'pySafe': '''def get_content():
    try:
        f = open('myfile.txt')
        s = f.readline()
        i = int(s.strip())
    # 발생할 수 있는 오류의 종류와 순서에 맞춰서 예외 처리 한다.
    except FileNotFoundError:
        print("file is not found")
    except OSError:
        print("cannot open file")
    except ValueError:
        print("Could not convert data to an integer.")''',
    'note': '',
  },
  'Null Pointer 역참조': {
    'javaLang': 'Java',
    'javaVuln': '''public static int cardinality (Object obj, final Collection col) {
    int count = 0;
    if (col == null) {
        return count;
    }
    Iterator it = col.iterator();
    while (it.hasNext()) {
        Object elt = it.next();
        // obj가 null이고 elt가 null이 아닐 경우 Null 포인터 역참조가 발생한다.
        if ((null == obj && null == elt) || obj.equals(elt)) {
            count++;
        }
    }
    return count;
}''',
    'javaSafe': '''public static int cardinality (Object obj, final Collection col) {
    int count = 0;
    if (col == null) {
        return count;
    }
    Iterator it = col.iterator();
    while (it.hasNext()) {
        Object elt = it.next();
        // obj가 null이 아닌 경우에만 obj.equals를 실행한다.
        if ((null == obj && null == elt) || (null != obj && obj.equals(elt))) {
            count++;
        }
    }
    return count;
}''',
    'pyVuln': '''def parse_xml(request):
    filename = request.POST.get('filename')
    # filename의 None 체크를 하지 않아 에러 발생 가능
    if (filename.count('.') > 0):
        name, ext = os.path.splitext(filename)
    else:
        ext = ''
    if ext == ".xml":
        parser = make_parser()
        parser.setContentHandler(Handler())
        parser.parse(filename)
        return render(request, "/success.html", {"result": parser})''',
    'pySafe': '''def parse_xml(request):
    filename = request.POST.get('filename')
    # filename이 None 인지 체크
    if filename is None or filename.strip() == "":
        return render(request, "/error.html", {"error": "파일 이름이 없습니다."})
    if (filename.count('.') > 0):
        name, ext = os.path.splitext(filename)
    else:
        ext = ''
    if ext == ".xml":
        parser = make_parser()
        parser.setContentHandler(Handler())
        parser.parse(filename)
        return render(request, "/success.html", {"result": parser})''',
    'note': '',
  },
  '부적절한 자원 해제': {
    'javaLang': 'Java',
    'javaVuln': '''InputStream in = null;
OutputStream out = null;
try {
    in = new FileInputStream(inputFile);
    out = new FileOutputStream(outputFile);
    ...
    FileCopyUtils.copy(fis, os);
    // 자원반환 실행 전에 오류가 발생할 경우 자원이 반환되지 않는다.
    in.close();
    out.close();
} catch (IOException e) {
    logger.error(e);
}''',
    'javaSafe': '''InputStream in = null;
OutputStream out = null;
try {
    in = new FileInputStream(inputFile);
    out = new FileOutputStream(outputFile);
    ...
    FileCopyUtils.copy(fis, os);
} catch (IOException e) {
    logger.error(e);
// 항상 수행되는 finally 블록에서 모든 자원을 해제한다.
} finally {
    if (in != null) {
        try { in.close(); } catch (IOException e) { logger.error(e); }
    }
    if (out != null) {
        try { out.close(); } catch (IOException e) { logger.error(e); }
    }
}''',
    'pyVuln': '''def get_config():
    lines = None
    try:
        f = open('config.cfg')
        lines = f.readlines()
        # 예외 발생 상황 가정
        raise Exception("Throwing the exception!")
        # try 절에서 할당한 자원이 반환(close)되기 전에
        # 예외가 발생하면 할당된 자원이 시스템에 반환되지 않음
        f.close()
        return lines
    except Exception as e:
        ...
        return ''
''',
    'pySafe': '''def get_config():
    lines = None
    try:
        f = open('config.cfg')
        lines = f.readlines()
        # 예외 발생 상황 가정
        raise Exception("Throwing the exception!")
    except Exception as e:
        ...
    finally:
        # try 절에서 할당한 자원은 finally 절에서 시스템에 반환을 해야 한다
        f.close()
        return lines

# 또는 with 문을 사용하면 블록이 끝날 때 자동으로 자원이 반환된다.
with open('config.cfg') as f:
    print(f.read())''',
    'note': '',
  },
  '해제된 자원 사용': {
    'javaLang': 'C',
    'javaVuln': '''int main(int argc, const char *argv[]) {
    char *temp;
    temp = (char *)malloc(BUFFER_SIZE);
    ......
    free(temp);
    // 해제한 자원을 사용하고 있어 의도하지 않은 결과가 발생하게 된다.
    strncpy(temp, argv[1], BUFFER_SIZE-1);
}''',
    'javaSafe': '''int main(int argc, const char *argv[]) {
    char *temp;
    temp = (char *)malloc(BUFFER_SIZE);
    ......
    // 할당된 자원을 최종적으로 사용하고 해제하여야 한다.
    strncpy(temp, argv[1], BUFFER_SIZE-1);
    free(temp);
}''',
    'pyVuln': '',
    'pySafe': '',
    'note': 'diag는 C 예제만 제공. Python 가이드는 C 메모리 관리 항목(해제된 자원 사용)을 다루지 않아 Python 예제 없음.',
  },
  '초기화되지 않은 변수 사용': {
    'javaLang': 'C',
    'javaVuln': '''// 변수의 초기값을 지정하지 않을 경우 공격에 사용될 수 있어 안전하지 않다.
int x, y;
switch(position) {
    case 0: x = base_position; y = base_position; break;
    case 1: x = base_position + i; y = base_position - i; break;
    default: x = 1; break;
}
setCursorPosition(x, y);''',
    'javaSafe': '''// 변수의 초기값은 항상 지정하여야 한다.
int x = 1, y = 1;
switch(position) {
    case 0: x = base_position; y = base_position; break;
    case 1: x = base_position + i; y = base_position - i; break;
    default: x = 1; break;
}
setCursorPosition(x, y);''',
    'pyVuln': '',
    'pySafe': '',
    'note': 'diag는 C 예제만 제공. Python 가이드는 초기화되지 않은 변수 사용 항목을 다루지 않아 Python 예제 없음.',
  },
}
