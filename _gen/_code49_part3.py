# -*- coding: utf-8 -*-
PART = {
  '보안기능 결정에 사용되는 부적절한 입력값': {
    'javaLang': 'Java',
    'javaVuln': '''<input type="hidden" name="price" value="1000"/>
<br/>품목 : HDTV
<br/>수량 : <input type="hidden" name="quantity" />개
try {
  // 서버가 보유한 가격(단가)을 사용자 화면에서 받아서 처리
  price = request.getParameter("price");
  quantity = request.getParameter("quantity");
  total = Integer.parseInt(quantity) * Float.parseFloat(price);
} catch (Exception e) {
  ...
}''',
    'javaSafe': '''<input type="hidden" name="price" value="1000"/>
<br/>품목 : HDTV
<br/>수량 : <input type="hidden" name="quantity" />개
try {
  // 가격이 아니라 item 항목을 받아 서버가 보유한 가격 정보로 계산
  item = request.getParameter("item");
  price = productService.getPrice(item);
  quantity = request.getParameter("quantity");
  total = Integer.parseInt(quantity) * price;
} catch (Exception e) {
  ...
}''',
    'pyVuln': '''from django.shortcuts import render
def init_password(request):
    # 쿠키에서 권한 정보를 가져온다
    role = request.COOKIE['role']
    request_id = request.POST.get('user_id', '')
    request_mail = request.POST.get('user_email', '')
    # 쿠키에서 가져온 권한이 관리자인지 비교
    if role == 'admin':
        password_init_and_sendmail(request_id, request_mail)
        return render(request, '/success.html')
    else:
        return render(request, '/failed.html')''',
    'pySafe': '''from django.shortcuts import render
def init_password(request):
    # 세션에서 권한 정보를 가져옴
    role = request.session['role']
    request_id = request.POST.get('user_id', '')
    request_mail = request.POST.get('user_email', '')
    # 세션에서 가져온 권한이 관리자인지 비교
    if role == 'admin':
        password_init_and_sendmail(request_id, request_mail)
        return render(request, '/success.html')
    else:
        return render(request, '/failed.html')''',
    'note': '',
  },
  '메모리 버퍼 오버플로우': {
    'javaLang': 'C',
    'javaVuln': '''typedef struct _charvoid {
    char x[16];
    void * y;
    void * z;
} charvoid;
void badCode() {
    charvoid cv_struct;
    cv_struct.y = (void *) SRC_STR;
    printLine((char *) cv_struct.y);
    /* sizeof(cv_struct) 사용으로 포인터 y에 덮어쓰기 발생 */
    memcpy(cv_struct.x, SRC_STR, sizeof(cv_struct));
    printLine((char *) cv_struct.x);
    printLine((char *) cv_struct.y);
}''',
    'javaSafe': '''typedef struct _charvoid {
    char x[16];
    void * y;
    void * z;
} charvoid;
static void goodCode() {
    charvoid cv_struct;
    cv_struct.y = (void *) SRC_STR;
    printLine((char *) cv_struct.y);
    /* sizeof(cv_struct.x)로 변경하여 포인터 y의 덮어쓰기를 방지 */
    memcpy(cv_struct.x, SRC_STR, sizeof(cv_struct.x));
    /* 문자열 종료를 위해 널 문자를 삽입 */
    cv_struct.x[(sizeof(cv_struct.x)/sizeof(char))-1] = '\\0';
    printLine((char *) cv_struct.x);
    printLine((char *) cv_struct.y);
}''',
    'pyVuln': '',
    'pySafe': '',
    'note': 'Python 미수록',
  },
  '포맷 스트링 삽입': {
    'javaLang': 'Java',
    'javaVuln': '''import java.util.Calendar;
// args[0]에 "%1$tY-%1$tm-%1$te"를 전달하면 시스템 날짜 정보가 노출됨
public static void main(String[] args) {
    Calendar validDate = Calendar.getInstance();
    validDate.set(2014, Calendar.OCTOBER, 14);
    // 외부 입력값을 포맷 문자열에 직접 포함하여 안전하지 않음
    System.out.printf(args[0] + " did not match! HINT: It was issued on %1$terd of some month", validDate);
}''',
    'javaSafe': '''import java.util.Calendar;
// 외부 입력값이 포맷 문자열 출력에 사용되지 않도록 수정
public static void main(String[] args) {
    Calendar validDate = Calendar.getInstance();
    validDate.set(2014, Calendar.OCTOBER, 14);
    // %s 포맷 문자열을 사용하고 사용자 입력값은 인자로 전달
    System.out.printf("%s did not match! HINT: It was issued on %2$terd of some month", args[0], validDate);
}''',
    'pyVuln': '''from django.shortcuts import render
AUTHENTICATE_KEY = 'Passw0rd'
def make_user_message(request):
    user_info = get_user_info(request.POST.get('user_id', ''))
    format_string = request.POST.get('msg_format', '')
    # 사용자가 입력한 문자열을 포맷 문자열로 사용하고 있어 안전하지 않음
    # 내부의 민감한 정보가 외부로 노출될 수 있다
    message = format_string.format(user=user_info)
    return render(request, '/user_page.html', {'message': message})''',
    'pySafe': '''from django.shortcuts import render
AUTHENTICATE_KEY = 'Passw0rd'
def make_user_message(request):
    user_info = get_user_info(request.POST.get('user_id', ''))
    # 사용자가 입력한 문자열을 포맷 문자열로 사용하지 않아 안전함
    message = 'user name is {}'.format(user_info.name)
    return render(request, '/user_page.html', {'message': message})''',
    'note': '',
  },
  '적절한 인증 없는 중요기능 허용': {
    'javaLang': 'Java',
    'javaVuln': '''@RequestMapping(value = "/modify.do", method = RequestMethod.POST)
public ModelAndView memberModifyProcess(@ModelAttribute("MemberModel") MemberModel memberModel,
        BindingResult result, HttpServletRequest request, HttpSession session) {
    ModelAndView mav = new ModelAndView();
    String userId = (String) session.getAttribute("userId");
    String passwd = request.getParameter("oldUserPw");
    // 수정하는 사용자와 로그인 사용자의 일치 여부를 확인하지 않아 안전하지 않음
    if (service.modifyMember(memberModel)) {
        mav.setViewName("redirect:/board/list.do");
        session.setAttribute("userName", memberModel.getUserName());
        return mav;
    } else {
        mav.addObject("errCode", 2);
        mav.setViewName("/board/member_modify");
        return mav;
    }
}''',
    'javaSafe': '''@RequestMapping(value = "/modify.do", method = RequestMethod.POST)
public ModelAndView memberModifyProcess(@ModelAttribute("MemberModel") MemberModel memberModel,
        BindingResult result, HttpServletRequest request, HttpSession session) {
    ModelAndView mav = new ModelAndView();
    String userId = (String) session.getAttribute("userId");
    String passwd = request.getParameter("oldUserPw");
    // 수정하는 사용자와 로그인 사용자가 동일한지 확인
    String requestUser = memberModel.getUserId();
    if (userId != null && requestUser != null && !userId.equals(requestUser)) {
        mav.addObject("errCode", 1);
        mav.addObject("member", memberModel);
        mav.setViewName("/board/member_modify");
        return mav;
    }
    // 동일한 경우에만 회원정보를 수정
    if (service.modifyMember(memberModel)) {
        ...
    }
}''',
    'pyVuln': '''from django.shortcuts import render
from re import escape
import hashlib
def change_password(request):
    new_pwd = request.POST.get('new_password', '')
    user = '%s' % escape(request.session['userid'])
    # 현재 password와 일치 여부를 확인하지 않고 수정함
    sha = hashlib.sha256(new_pwd.encode())
    update_password_from_db(user, sha.hexdigest())
    return render(request, '/success.html')''',
    'pySafe': '''from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from re import escape
import hashlib
# login_required로 로그인된 사용자만 접근하도록 처리
@login_required
def change_password(request):
    new_pwd = request.POST.get('new_password', '')
    crnt_pwd = request.POST.get('current_password', '')
    user = '%s' % escape(request.session['userid'])
    h_pwd = hashlib.sha256(crnt_pwd.encode()).hexdigest()
    old_pwd = get_password_from_db(user)
    # 패스워드 변경 전 사용자에 대한 재인증을 수행
    if old_pwd == h_pwd:
        new_h = hashlib.sha256(new_pwd.encode())
        update_password_from_db(user, new_h.hexdigest())
        return render(request, '/success.html')
    else:
        return render(request, 'failed.html', {'error': '패스워드가 일치하지 않습니다'})''',
    'note': '',
  },
  '부적절한 인가': {
    'javaLang': 'Java',
    'javaVuln': '''private BoardDao boardDao;
String action = request.getParameter("action");
String contentId = request.getParameter("contentId");
// 요청 사용자의 delete 권한 확인 없이 수행하고 있어 안전하지 않음
if (action != null && action.equals("delete")) {
    boardDao.delete(contentId);
}''',
    'javaSafe': '''private BoardDao boardDao;
String action = request.getParameter("action");
String contentId = request.getParameter("contentId");
// 세션에 저장된 사용자 정보를 얻어온다
User user = (User) session.getAttribute("user");
// 해당 사용자가 delete 권한이 있는지 확인한 뒤 삭제 작업을 수행
if (action != null && action.equals("delete") && checkAccessControlList(user, action)) {
    boardDao.delete(contentId);
}''',
    'pyVuln': '''from django.shortcuts import render
from .model import Content
def delete_content(request):
    action = request.POST.get('action', '')
    content_id = request.POST.get('content_id', '')
    # 작업 요청 사용자의 권한 확인 없이 delete를 수행
    if action is not None and action == "delete":
        Content.objects.filter(id=content_id).delete()
        return render(request, '/success.html')
    else:
        return render(request, '/error.html', {'error': '접근 권한이 없습니다.'})''',
    'pySafe': '''from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from .model import Content
@login_required
# 해당 기능을 수행할 권한이 있는지 확인
@permission_required('content.delete', raise_exception=True)
def delete_content(request):
    action = request.POST.get('action', '')
    content_id = request.POST.get('content_id', '')
    if action is not None and action == "delete":
        Content.objects.filter(id=content_id).delete()
        return render(request, '/success.html')
    else:
        return render(request, '/error.html', {'error': '삭제 실패'})''',
    'note': '',
  },
  '중요한 자원에 대한 잘못된 권한 설정': {
    'javaLang': 'Java',
    'javaVuln': '''File file = new File("/home/setup/system.ini");
// 모든 사용자에게 실행 권한을 허용하여 안전하지 않음
file.setExecutable(true, false);
// 모든 사용자에게 읽기 권한을 허용하여 안전하지 않음
file.setReadable(true, false);
// 모든 사용자에게 쓰기 권한을 허용하여 안전하지 않음
file.setWritable(true, false);''',
    'javaSafe': '''File file = new File("/home/setup/system.ini");
// 소유자에게 실행 권한을 금지
file.setExecutable(false);
// 소유자에게 읽기 권한만 허용
file.setReadable(true);
// 소유자에게 쓰기 권한을 금지
file.setWritable(false);''',
    'pyVuln': '''import os
def write_file():
    # 모든 사용자가 읽기, 쓰기, 실행 권한을 가지게 된다
    os.chmod('/root/system_config', 0o777)
    with open("/root/system_config", 'w') as f:
        f.write("your config is broken")''',
    'pySafe': '''import os
def write_file():
    # 소유자 외에는 아무런 권한을 주지 않음
    os.chmod('/root/system_config', 0o700)
    with open("/root/system_config", 'w') as f:
        f.write("your config is broken")''',
    'note': '',
  },
  '취약한 암호화 알고리즘 사용': {
    'javaLang': 'Java',
    'javaVuln': '''import java.security.*;
import javax.crypto.Cipher;
public class CryptoUtils {
    public byte[] encrypt(byte[] msg, Key k) {
        byte[] rslt = null;
        try {
            // 키 길이가 짧아 취약한 암호화 알고리즘인 DES를 사용하여 안전하지 않음
            Cipher c = Cipher.getInstance("DES");
            c.init(Cipher.ENCRYPT_MODE, k);
            rslt = c.update(msg);
        }
        ...
    }
}''',
    'javaSafe': '''import java.security.*;
import javax.crypto.Cipher;
public class CryptoUtils {
    public byte[] encrypt(byte[] msg, Key k) {
        byte[] rslt = null;
        try {
            // 강력한 알고리즘인 AES를 사용하여 안전함
            Cipher c = Cipher.getInstance("AES/CBC/PKCS5Padding");
            c.init(Cipher.ENCRYPT_MODE, k);
            rslt = c.update(msg);
        }
        ...
    }
}''',
    'pyVuln': '''import base64
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad
def get_enc_text(plain_text, key):
    # 취약한 암호화 알고리즘인 DES를 사용하여 안전하지 않음
    cipher_des = DES.new(key, DES.MODE_ECB)
    encrypted_data = base64.b64encode(cipher_des.encrypt(pad(plain_text, 32)))
    return encrypted_data.decode('ASCII')''',
    'pySafe': '''import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
def get_enc_text(plain_text, key, iv):
    # 안전한 알고리즘인 AES를 사용하여 안전함
    cipher_aes = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = base64.b64encode(cipher_aes.encrypt(pad(plain_text, 32)))
    return encrypted_data.decode('ASCII')''',
    'note': '',
  },
}
