# -*- coding: utf-8 -*-
"""SEI CERT C++ 규칙 (파트2: CTR·STR·MEM) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제)."""

RULES = [
 {'id':'CTR50-CPP','cat':'CTR · Rule · L1',
  'title':'컨테이너 인덱스/반복자가 유효 범위 안에 있도록 보장한다',
  'bad': r"""std::vector<int> v{1, 2, 3};
int x = v[idx];        // idx 범위 미검증""",
  'good': r"""std::vector<int> v{1, 2, 3};
if (idx < v.size()) {
    int x = v[idx];
}
// 또는 경계 검사가 있는 v.at(idx)""",
  'why':'operator[]는 범위를 검사하지 않아 잘못된 인덱스로 메모리 손상이 난다. 인덱스를 size()와 비교하거나 at()을 사용한다.'},

 {'id':'CTR51-CPP','cat':'CTR · Rule · L1',
  'title':'컨테이너 원소에 대한 유효한 참조/포인터/반복자만 사용한다',
  'bad': r"""std::vector<int> v{1, 2, 3};
int& r = v[0];
v.push_back(4);        // 재할당 시 r 무효화
r = 9;                 // 댕글링 참조""",
  'good': r"""std::vector<int> v{1, 2, 3};
v.push_back(4);
v[0] = 9;              // 변경 후 다시 접근""",
  'why':'push_back 등으로 vector가 재할당되면 기존 참조·반복자가 무효화된다. 컨테이너를 수정한 뒤에는 참조를 다시 얻는다.'},

 {'id':'CTR53-CPP','cat':'CTR · Rule · L1',
  'title':'유효한 반복자 범위(iterator range)를 사용한다',
  'bad': r"""std::sort(v.end(), v.begin());   // 시작/끝 뒤바뀜 — 미정의""",
  'good': r"""std::sort(v.begin(), v.end());""",
  'why':'first가 last보다 뒤이거나 다른 컨테이너의 반복자를 섞으면 알고리즘이 범위를 넘어 미정의 동작이 된다. [begin, end) 순서의 유효 범위를 전달한다.'},

 {'id':'CTR54-CPP','cat':'CTR · Rule · L2',
  'title':'같은 컨테이너에 속하지 않는 반복자를 빼지 않는다',
  'bad': r"""auto d = it_a - it_b;   // 서로 다른 컨테이너의 반복자""",
  'good': r"""auto d = v.end() - v.begin();   // 동일 컨테이너""",
  'why':'서로 다른 컨테이너의 반복자 뺄셈은 미정의 동작이다. 같은 컨테이너에서 얻은 반복자끼리만 거리 연산한다.'},

 {'id':'CTR56-CPP','cat':'CTR · Rule · L2',
  'title':'다형 객체에 포인터 산술을 적용하지 않는다',
  'bad': r"""Base* arr = new Derived[3];   // 다형 배열
arr[1].f();             // 기반 크기로 인덱싱 — 어긋남""",
  'good': r"""std::vector<std::unique_ptr<Base>> v;
v.push_back(std::make_unique<Derived>());
v[0]->f();""",
  'why':'파생 객체 배열을 기반 포인터로 인덱싱하면 요소 크기가 달라 잘못된 주소를 계산한다. 다형 컬렉션은 스마트포인터 컨테이너로 구성한다.'},

 {'id':'CTR57-CPP','cat':'CTR · Rule · L2',
  'title':'정렬/연관 컨테이너에 유효한 순서 술어(predicate)를 제공한다',
  'bad': r"""std::sort(v.begin(), v.end(),
          [](int a, int b){ return a <= b; });   // strict-weak-ordering 위반""",
  'good': r"""std::sort(v.begin(), v.end(),
          [](int a, int b){ return a < b; });""",
  'why':'<= 같은 술어는 엄격 약순서(strict weak ordering)를 위반해 정렬 알고리즘에서 미정의 동작을 일으킨다. < 처럼 동치를 false로 두는 술어를 쓴다.'},

 {'id':'CTR58-CPP','cat':'CTR · Rule · L3',
  'title':'술어 함수 객체는 상태를 변경(mutable)하지 않게 한다',
  'bad': r"""struct Pred { int n = 0; bool operator()(int x){ return n++ < 3; } };
std::remove_if(v.begin(), v.end(), Pred{});   // 호출마다 상태 변함 — 미정의""",
  'good': r"""std::remove_if(v.begin(), v.end(),
               [](int x){ return x < 3; });    // 무상태 술어""",
  'why':'알고리즘은 술어를 여러 번 복사·호출할 수 있어 가변 상태 술어는 예측 불가능한 결과를 낸다. 술어는 부작용 없는 순수 함수로 만든다.'},

 {'id':'STR50-CPP','cat':'STR · Rule · L1',
  'title':'문자열을 다룰 때 충분한 저장 공간을 보장한다',
  'bad': r"""char buf[8];
std::strcpy(buf, s.c_str());   // s가 8바이트 이상이면 오버플로우""",
  'good': r"""std::string buf = s;           // std::string으로 동적 관리
// C 버퍼가 꼭 필요하면 길이 검사 후 복사""",
  'why':'C 문자열 함수로 고정 버퍼에 복사하면 길이를 초과해 오버플로우가 난다. std::string으로 길이를 자동 관리하거나 경계를 검사한다.'},

 {'id':'STR51-CPP','cat':'STR · Rule · L1',
  'title':'널 포인터로 std::string 을 생성하지 않는다',
  'bad': r"""const char* p = std::getenv("X");   // 미설정 시 nullptr
std::string s(p);                   // nullptr로 string 생성 — 미정의""",
  'good': r"""const char* p = std::getenv("X");
std::string s = (p != nullptr) ? std::string(p) : std::string();""",
  'why':'std::string을 nullptr로 생성하면 미정의 동작(대개 크래시)이다. 포인터가 널이 아닌지 확인한 뒤 생성한다.'},

 {'id':'STR52-CPP','cat':'STR · Rule · L1',
  'title':'basic_string 원소의 유효한 참조/반복자만 사용한다',
  'bad': r"""std::string s = "hello";
const char& c = s[0];
s += " world";          // 재할당 시 c 무효화
use(c);""",
  'good': r"""std::string s = "hello";
s += " world";
const char& c = s[0];   // 수정 후 참조 획득
use(c);""",
  'why':'append/insert 등으로 문자열 버퍼가 재할당되면 기존 참조·반복자가 무효가 된다. 수정 후 참조를 다시 얻는다.'},

 {'id':'STR53-CPP','cat':'STR · Rule · L1',
  'title':'문자열 원소 접근 시 범위를 검사한다',
  'bad': r"""std::string s = "ab";
char c = s[5];          // 범위 밖 — 미정의""",
  'good': r"""std::string s = "ab";
if (5 < s.size()) { char c = s[5]; }
// 또는 예외를 던지는 s.at(5)""",
  'why':'operator[]는 범위를 검사하지 않아 길이를 넘는 인덱스 접근은 미정의 동작이다. size()와 비교하거나 at()으로 검사한다.'},

 {'id':'MEM50-CPP','cat':'MEM · Rule · L1',
  'title':'해제된 메모리에 접근하지 않는다(use-after-free)',
  'bad': r"""int* p = new int(5);
delete p;
*p = 7;                 // 해제 후 사용""",
  'good': r"""auto p = std::make_unique<int>(5);
*p = 7;                 // 스코프 종료 시 자동 해제""",
  'why':'해제된 메모리에 접근하면 힙 손상·정보 유출·임의 코드 실행으로 이어진다. RAII(smart pointer)로 수명을 자동 관리해 댕글링을 방지한다.'},

 {'id':'MEM51-CPP','cat':'MEM · Rule · L1',
  'title':'동적 자원을 올바른 형식으로 해제한다',
  'bad': r"""int* a = new int[10];
delete a;               // new[]를 delete로 — 미정의""",
  'good': r"""std::vector<int> a(10);  // 또는 std::make_unique<int[]>(10)""",
  'why':'new[]는 delete[]로, new는 delete로 해제해야 하며 불일치는 미정의 동작이다. 컨테이너/스마트포인터로 올바른 해제를 자동화한다.'},

 {'id':'MEM52-CPP','cat':'MEM · Rule · L1',
  'title':'메모리 할당 오류를 검출하고 처리한다',
  'bad': r"""int* p = (int*)std::malloc(n * sizeof(int));
p[0] = 1;               // malloc 실패(NULL) 미검사""",
  'good': r"""try {
    auto p = std::make_unique<int[]>(n);  // 실패 시 bad_alloc
    p[0] = 1;
} catch (const std::bad_alloc&) { handle(); }""",
  'why':'할당 실패(NULL 또는 bad_alloc)를 처리하지 않으면 널 역참조·비정상 종료가 난다. malloc 반환을 검사하거나 new의 예외를 처리한다.'},

 {'id':'MEM53-CPP','cat':'MEM · Rule · L2',
  'title':'수동 수명 관리 시 객체를 명시적으로 생성·소멸한다',
  'bad': r"""alignas(S) unsigned char buf[sizeof(S)];
S* p = reinterpret_cast<S*>(buf);
p->use();               // 생성자 미호출 객체 사용""",
  'good': r"""alignas(S) unsigned char buf[sizeof(S)];
S* p = new (buf) S();   // placement new로 생성
p->use();
p->~S();                // 명시적 소멸""",
  'why':'원시 저장소를 객체로 캐스트만 하면 생성자가 호출되지 않아 불변식이 성립하지 않는다. placement new로 생성하고 소멸자를 명시 호출한다.'},

 {'id':'MEM54-CPP','cat':'MEM · Rule · L1',
  'title':'placement new 에 적절히 정렬된 저장소를 제공한다',
  'bad': r"""unsigned char buf[sizeof(S)];   // 정렬 미보장
S* p = new (buf) S();           // 정렬 위반 가능""",
  'good': r"""alignas(S) unsigned char buf[sizeof(S)];
S* p = new (buf) S();""",
  'why':'정렬 요건을 만족하지 않는 저장소에 객체를 배치하면 미정의 동작·폴트가 난다. alignas로 대상 타입 정렬을 보장한다.'},

 {'id':'MEM56-CPP','cat':'MEM · Rule · L1',
  'title':'이미 소유된 포인터를 무관한 스마트 포인터에 저장하지 않는다',
  'bad': r"""int* raw = new int(1);
std::shared_ptr<int> a(raw);
std::shared_ptr<int> b(raw);   // 별도 제어블록 — 이중 해제""",
  'good': r"""auto a = std::make_shared<int>(1);
std::shared_ptr<int> b = a;    // 소유권 공유""",
  'why':'같은 raw 포인터로 독립 shared_ptr 두 개를 만들면 제어 블록이 둘이라 이중 해제가 발생한다. 소유권은 복사로 공유한다.'},

 {'id':'MEM57-CPP','cat':'MEM · Rule · L2',
  'title':'과도 정렬(over-aligned) 타입에 기본 operator new 를 쓰지 않는다',
  'bad': r"""struct alignas(64) Cache { char data[64]; };
Cache* p = new Cache();   // 기본 new가 64B 정렬 보장 못할 수 있음(구버전)""",
  'good': r"""struct alignas(64) Cache { char data[64]; };
// C++17의 정렬 인식 operator new 사용 또는 std::aligned_alloc
void* m = std::aligned_alloc(64, sizeof(Cache));
Cache* p = new (m) Cache();""",
  'why':'기본 할당자는 확장 정렬을 보장하지 않을 수 있어 SIMD/캐시라인 타입이 오정렬된다. 정렬 인식 할당(aligned operator new / aligned_alloc)을 사용한다.'},

 {'id':'CTR52-CPP','cat':'CTR · Rule · L2',
  'title':'컨테이너 연산이 용량을 넘쳐 오버플로우하지 않게 한다',
  'bad': r"""std::vector<int> v;
v.reserve(huge * sizeof(int));   // 크기 계산 오버플로우 가능""",
  'good': r"""if (huge <= v.max_size()) {
    v.reserve(huge);
}""",
  'why':'크기 계산이 오버플로우하거나 max_size를 넘으면 예외 또는 손상이 발생한다. 요청 크기를 max_size와 비교해 검증한다.'},
]
