# -*- coding: utf-8 -*-
"""SEI CERT C++ 규칙 (파트2: CTR·STR·MEM) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제).
강화판: bad/good 를 현실적 맥락의 컴파일 가능 C++ 프로그램(int main 포함)으로 작성하고
KO/EN 이중언어(title_en/why_en) 제공. Wandbox gcc-13.2.0 `-std=gnu++17` 기준."""

RULES = [
 {'id':'CTR50-CPP','cat':'CTR · Rule · L1','compiles':True,
  'title':'컨테이너 인덱스/반복자가 유효 범위 안에 있도록 보장한다',
  'title_en':'Guarantee that container indices and iterators are within the valid range',
  'bad': r"""#include <iostream>
#include <vector>
static int element_at(const std::vector<int>& v, std::size_t idx) {
    return v[idx];        // idx 범위 미검증 — 범위 밖이면 메모리 손상
}
int main() {
    std::vector<int> v{1, 2, 3};
    std::cout << element_at(v, 7) << '\n';   // 범위 밖 접근 — 미정의 동작
}""",
  'good': r"""#include <iostream>
#include <vector>
#include <stdexcept>
static int element_at(const std::vector<int>& v, std::size_t idx) {
    return v.at(idx);     // 경계 검사 — 범위 밖이면 std::out_of_range
}
int main() {
    std::vector<int> v{1, 2, 3};
    try { std::cout << element_at(v, 7) << '\n'; }
    catch (const std::out_of_range& e) { std::cout << "out of range\n"; }
}""",
  'why':'근거: operator[] 는 성능을 위해 범위를 전혀 검사하지 않으므로, 잘못된 인덱스는 컨테이너 버퍼 밖의 메모리를 읽거나 쓴다. 영향: 범위 밖 접근은 인접 데이터 손상·정보 유출·크래시를 일으키고, 입력으로 제어되면 보안 취약점이 된다. 대응: 인덱스를 size() 와 비교하거나 경계 검사를 수행하는 at() 을 사용한다.',
  'why_en':'Rationale: operator[] performs no bounds checking for speed, so an invalid index reads or writes memory outside the container buffer. Impact: an out-of-range access corrupts adjacent data, leaks information, or crashes, and becomes a security flaw when driven by input. Fix: compare the index against size() or use at(), which performs bounds checking.'},

 {'id':'CTR51-CPP','cat':'CTR · Rule · L1','compiles':True,
  'title':'컨테이너 원소에 대한 유효한 참조/포인터/반복자만 사용한다',
  'title_en':'Use valid references, pointers, and iterators to reference container elements',
  'bad': r"""#include <iostream>
#include <vector>
int main() {
    std::vector<int> v{1, 2, 3};
    int& r = v[0];        // 첫 원소 참조
    v.push_back(4);       // 용량 초과 시 재할당 → 기존 버퍼 해제, r 무효화
    r = 9;                // 댕글링 참조에 쓰기 — 미정의 동작
    std::cout << v[0] << '\n';
}""",
  'good': r"""#include <iostream>
#include <vector>
int main() {
    std::vector<int> v{1, 2, 3};
    v.push_back(4);       // 먼저 컨테이너를 수정
    v[0] = 9;             // 그 다음 안전하게 인덱스로 접근
    std::cout << v[0] << '\n';
}""",
  'why':'근거: vector 는 용량을 초과하는 삽입 시 더 큰 버퍼를 새로 할당하고 기존 버퍼를 해제하므로, 원소를 가리키던 참조·포인터·반복자가 모두 무효화된다. 영향: 무효화된 참조에 접근하면 해제된 힙을 읽거나 써서 댕글링 버그가 되고 데이터가 손상된다. 대응: 컨테이너를 수정한 뒤에는 참조·반복자를 다시 얻거나, 인덱스로 재접근한다.',
  'why_en':'Rationale: a vector allocates a new larger buffer and frees the old one when an insertion exceeds capacity, invalidating every reference, pointer, and iterator to its elements. Impact: accessing an invalidated reference reads or writes freed heap, a dangling bug that corrupts data. Fix: re-obtain references/iterators after modifying the container, or re-access by index.'},

 {'id':'CTR53-CPP','cat':'CTR · Rule · L1','compiles':True,
  'title':'유효한 반복자 범위(iterator range)를 사용한다',
  'title_en':'Use valid iterator ranges',
  'bad': r"""#include <iostream>
#include <vector>
#include <algorithm>
int main() {
    std::vector<int> v{3, 1, 2};
    std::sort(v.end(), v.begin());   // first 가 last 뒤 — 범위 무효, 미정의 동작
    for (int x : v) std::cout << x << ' ';
    std::cout << '\n';
}""",
  'good': r"""#include <iostream>
#include <vector>
#include <algorithm>
int main() {
    std::vector<int> v{3, 1, 2};
    std::sort(v.begin(), v.end());   // [begin, end) — 유효한 반(half-open) 범위
    for (int x : v) std::cout << x << ' ';
    std::cout << '\n';
}""",
  'why':'근거: 표준 알고리즘은 [first, last) 가 반복적으로 first 를 증가시켜 last 에 도달할 수 있는 유효 범위라고 가정한다. 영향: first 가 last 보다 뒤이거나 서로 다른 컨테이너의 반복자를 섞으면 알고리즘이 끝을 넘어 순회해 메모리 손상·무한 루프가 된다. 대응: 같은 컨테이너에서 얻은 begin/end 를 올바른 순서로 전달한다.',
  'why_en':'Rationale: standard algorithms assume [first, last) is a valid range where repeatedly incrementing first reaches last. Impact: if first is after last, or iterators from different containers are mixed, the algorithm runs past the end, causing memory corruption or an infinite loop. Fix: pass begin/end obtained from the same container in the correct order.'},

 {'id':'CTR54-CPP','cat':'CTR · Rule · L2','compiles':True,
  'title':'같은 컨테이너에 속하지 않는 반복자를 비교/빼지 않는다',
  'title_en':'Do not subtract or compare iterators that do not refer to the same container',
  'bad': r"""#include <iostream>
#include <vector>
int main() {
    std::vector<int> a{1, 2, 3};
    std::vector<int> b{4, 5};
    auto d = a.begin() - b.begin();   // 서로 다른 컨테이너 반복자 뺄셈 — 미정의
    std::cout << d << '\n';
}""",
  'good': r"""#include <iostream>
#include <vector>
int main() {
    std::vector<int> a{1, 2, 3};
    auto d = a.end() - a.begin();     // 같은 컨테이너 — 유효한 거리
    std::cout << d << '\n';           // 3
}""",
  'why':'근거: 반복자 뺄셈·관계 비교는 두 반복자가 같은 배열(컨테이너)의 원소를 가리킬 때만 의미가 정의된다. 영향: 서로 다른 컨테이너의 반복자를 빼면 무관한 두 메모리 주소의 차이를 계산해 의미 없는 값이 나오고 미정의 동작이 된다. 대응: 거리·순서 비교는 같은 컨테이너에서 얻은 반복자끼리만 수행한다.',
  'why_en':'Rationale: iterator subtraction and relational comparison are defined only when both iterators refer to elements of the same array (container). Impact: subtracting iterators from different containers computes the difference of two unrelated addresses, yielding a meaningless value and undefined behaviour. Fix: perform distance and ordering comparisons only between iterators obtained from the same container.'},

 {'id':'CTR56-CPP','cat':'CTR · Rule · L2','compiles':True,
  'title':'다형 객체에 포인터 산술을 적용하지 않는다',
  'title_en':'Do not use pointer arithmetic on polymorphic objects',
  'bad': r"""#include <iostream>
#include <memory>
struct Base { virtual void f(){ std::cout << "Base\n"; } virtual ~Base()=default; };
struct Derived : Base { long extra=0; void f() override { std::cout << "Derived\n"; } };
int main() {
    Base* arr = new Derived[3];   // 배열 요소는 Derived 크기
    arr[1].f();                   // Base 크기로 인덱싱 → 잘못된 주소, 미정의 동작
    delete[] static_cast<Derived*>(arr);
}""",
  'good': r"""#include <iostream>
#include <memory>
#include <vector>
struct Base { virtual void f(){ std::cout << "Base\n"; } virtual ~Base()=default; };
struct Derived : Base { long extra=0; void f() override { std::cout << "Derived\n"; } };
int main() {
    std::vector<std::unique_ptr<Base>> v;     // 다형 컬렉션 — 포인터 산술 없음
    v.push_back(std::make_unique<Derived>());
    v.push_back(std::make_unique<Derived>());
    v[1]->f();                                // 정확한 다형 디스패치
}""",
  'why':'근거: arr[i] 와 포인터 산술은 정적 포인터 타입의 크기를 보폭으로 사용하는데, 실제 배열 요소가 더 큰 파생 타입이면 보폭이 어긋난다. 영향: 두 번째 이후 요소의 주소가 객체 경계와 맞지 않아 잘못된 메모리를 가상 호출 대상으로 삼아 미정의 동작·크래시가 난다. 대응: 다형 객체 컬렉션은 raw 배열 대신 스마트 포인터 컨테이너(vector<unique_ptr<Base>>)로 구성한다.',
  'why_en':'Rationale: arr[i] and pointer arithmetic use the size of the static pointer type as the stride, but when the real array elements are a larger derived type the stride is wrong. Impact: addresses of elements past the first do not line up with object boundaries, so a virtual call targets wrong memory, causing undefined behaviour or a crash. Fix: build polymorphic collections with smart-pointer containers (vector<unique_ptr<Base>>) instead of raw arrays.'},

 {'id':'CTR57-CPP','cat':'CTR · Rule · L2','compiles':True,
  'title':'정렬/연관 컨테이너에 유효한 순서 술어(predicate)를 제공한다',
  'title_en':'Provide a valid ordering predicate for sorted and associative containers',
  'bad': r"""#include <iostream>
#include <vector>
#include <algorithm>
int main() {
    std::vector<int> v{5, 2, 8, 2, 1};
    std::sort(v.begin(), v.end(),
              [](int a, int b){ return a <= b; });   // <= 는 엄격 약순서 위반
    for (int x : v) std::cout << x << ' ';
    std::cout << '\n';
}""",
  'good': r"""#include <iostream>
#include <vector>
#include <algorithm>
int main() {
    std::vector<int> v{5, 2, 8, 2, 1};
    std::sort(v.begin(), v.end(),
              [](int a, int b){ return a < b; });     // 동치를 false 로 — 엄격 약순서
    for (int x : v) std::cout << x << ' ';
    std::cout << '\n';
}""",
  'why':'근거: sort·map·set 같은 정렬/연관 컨테이너는 비교 술어가 엄격 약순서(strict weak ordering)를 만족한다고 가정하는데, 핵심은 같은 값에 대해 comp(a,a) 가 false 여야 한다는 것이다. 영향: <= 처럼 동치에 true 를 주는 술어는 두 동일 원소에서 모순을 만들어 알고리즘이 범위를 넘어 순회하거나 트리 불변식을 깨 미정의 동작이 된다. 대응: < 처럼 동치를 false 로 두는 술어를 사용한다.',
  'why_en':'Rationale: sorted and associative containers like sort, map, and set assume the comparison predicate is a strict weak ordering, whose key requirement is that comp(a,a) is false for equal values. Impact: a predicate like <= that returns true for equal elements creates a contradiction on duplicates, letting the algorithm run past the range or break tree invariants — undefined behaviour. Fix: use a predicate such as < that returns false for equivalent values.'},

 {'id':'CTR58-CPP','cat':'CTR · Rule · L3','compiles':True,
  'title':'술어 함수 객체는 호출 간 상태를 변경하지 않게 한다',
  'title_en':'Predicate function objects should not mutate state across calls',
  'bad': r"""#include <iostream>
#include <vector>
#include <algorithm>
struct Pred {                            // 호출마다 변하는 상태
    int n = 0;
    bool operator()(int) { return n++ < 2; }
};
int main() {
    std::vector<int> v{1, 2, 3, 4, 5};
    auto it = std::remove_if(v.begin(), v.end(), Pred{});   // 술어 복사·재호출 시 비결정적
    v.erase(it, v.end());
    for (int x : v) std::cout << x << ' ';
    std::cout << '\n';
}""",
  'good': r"""#include <iostream>
#include <vector>
#include <algorithm>
int main() {
    std::vector<int> v{1, 2, 3, 4, 5};
    auto it = std::remove_if(v.begin(), v.end(),
                             [](int x){ return x < 3; });    // 무상태 순수 술어
    v.erase(it, v.end());
    for (int x : v) std::cout << x << ' ';
    std::cout << '\n';
}""",
  'why':'근거: 표준 알고리즘은 술어 함수 객체를 명세상 임의 횟수로 복사하고 호출할 수 있어, 호출 순서·횟수에 의존하는 가변 상태(카운터 등)는 사본마다 독립적으로 동작한다. 영향: 어떤 원소가 제거될지가 구현·최적화에 따라 달라지는 비결정적 결과가 되어 이식성과 재현성이 깨진다. 대응: 술어는 입력만으로 결과가 정해지는 부작용 없는 순수 함수(또는 무상태 람다)로 작성한다.',
  'why_en':'Rationale: standard algorithms are permitted to copy and invoke a predicate function object any number of times, so mutable state (such as a counter) that depends on call order or count behaves independently in each copy. Impact: which elements are removed becomes nondeterministic across implementations and optimizations, breaking portability and reproducibility. Fix: write predicates as side-effect-free pure functions (or stateless lambdas) whose result depends only on the input.'},

 {'id':'STR50-CPP','cat':'STR · Rule · L1','compiles':True,
  'title':'문자열을 다룰 때 충분한 저장 공간을 보장한다',
  'title_en':'Guarantee that storage for strings has sufficient space',
  'bad': r"""#include <iostream>
#include <cstring>
#include <string>
int main() {
    std::string s = "this is far longer than eight bytes";
    char buf[8];
    std::strcpy(buf, s.c_str());   // s 가 8바이트 초과 → 스택 버퍼 오버플로우
    std::cout << buf << '\n';
}""",
  'good': r"""#include <iostream>
#include <string>
int main() {
    std::string s = "this is far longer than eight bytes";
    std::string buf = s;           // std::string 이 길이에 맞춰 동적 관리
    std::cout << buf << '\n';
}""",
  'why':'근거: strcpy 같은 C 문자열 함수는 대상 버퍼 크기를 인자로 받지 않아, 원본이 고정 버퍼보다 길면 경계를 넘어 인접 메모리에 기록한다. 영향: 스택 버퍼 오버플로우는 반환 주소·인접 변수를 덮어 크래시·메모리 손상은 물론 코드 실행 공격의 통로가 된다. 대응: std::string 으로 길이를 자동 관리하거나, C 버퍼가 꼭 필요하면 길이를 검사한 뒤 한정된 복사를 한다.',
  'why_en':'Rationale: C string functions like strcpy take no destination size, so if the source is longer than the fixed buffer it writes past the boundary into adjacent memory. Impact: a stack buffer overflow overwrites the return address and neighbouring variables, causing crashes and memory corruption and opening a path to code-execution attacks. Fix: manage length automatically with std::string, or when a C buffer is required, copy a bounded amount after checking the length.'},

 {'id':'STR51-CPP','cat':'STR · Rule · L1','compiles':True,
  'title':'널 포인터로 std::string 을 생성하지 않는다',
  'title_en':'Do not attempt to create a std::string from a null pointer',
  'bad': r"""#include <iostream>
#include <cstdlib>
#include <string>
int main() {
    const char* p = std::getenv("DOES_NOT_EXIST");   // 미설정 시 nullptr
    std::string s(p);     // nullptr 로 string 생성 — strlen(nullptr) 미정의, 크래시
    std::cout << s << '\n';
}""",
  'good': r"""#include <iostream>
#include <cstdlib>
#include <string>
int main() {
    const char* p = std::getenv("DOES_NOT_EXIST");
    std::string s = (p != nullptr) ? std::string(p) : std::string{};   // 널 검사
    std::cout << "[" << s << "]\n";
}""",
  'why':'근거: const char* 를 받는 std::string 생성자는 내부적으로 strlen 으로 길이를 재는데, 인자가 nullptr 이면 널 포인터를 역참조하게 되어 미정의 동작이다. 영향: getenv·검색 함수 등 nullptr 을 반환할 수 있는 API 결과를 그대로 넘기면 대개 즉시 크래시가 난다. 대응: 포인터가 nullptr 이 아닌지 확인한 뒤 생성하고, 널이면 빈 문자열로 대체한다.',
  'why_en':'Rationale: the std::string constructor taking const char* measures length internally with strlen, so a nullptr argument dereferences a null pointer — undefined behaviour. Impact: passing the result of APIs that may return nullptr (getenv, lookup functions) directly usually crashes immediately. Fix: check that the pointer is not nullptr before constructing, substituting an empty string when it is null.'},

 {'id':'STR52-CPP','cat':'STR · Rule · L1','compiles':True,
  'title':'basic_string 원소의 유효한 참조/반복자만 사용한다',
  'title_en':'Use valid references, pointers, and iterators to reference elements of a basic_string',
  'bad': r"""#include <iostream>
#include <string>
int main() {
    std::string s = "hello";
    const char& c = s[0];   // 첫 문자 참조
    s += " world and a much longer suffix";   // 재할당 → c 무효화
    std::cout << c << '\n';  // 댕글링 참조 — 미정의 동작
}""",
  'good': r"""#include <iostream>
#include <string>
int main() {
    std::string s = "hello";
    s += " world and a much longer suffix";   // 먼저 수정
    const char& c = s[0];   // 그 다음 참조 획득
    std::cout << c << '\n';
}""",
  'why':'근거: append·insert·operator+= 로 문자열이 현재 용량을 초과하면 내부 버퍼가 재할당되어 기존 문자에 대한 참조·포인터·반복자가 모두 무효화된다. 영향: 무효화된 참조를 읽으면 해제된 버퍼를 가리켜 쓰레기 값·크래시가 난다. 대응: 문자열을 수정한 뒤 참조·반복자를 다시 얻는다.',
  'why_en':'Rationale: when an append, insert, or operator+= grows a string past its current capacity, the internal buffer is reallocated, invalidating all references, pointers, and iterators to existing characters. Impact: reading an invalidated reference points into the freed buffer, yielding garbage or a crash. Fix: re-obtain references/iterators after modifying the string.'},

 {'id':'STR53-CPP','cat':'STR · Rule · L1','compiles':True,
  'title':'문자열 원소 접근 시 범위를 검사한다',
  'title_en':'Range check element access',
  'bad': r"""#include <iostream>
#include <string>
int main() {
    std::string s = "ab";
    char c = s[5];        // 길이 2 인데 인덱스 5 — 범위 밖, 미정의 동작
    std::cout << static_cast<int>(c) << '\n';
}""",
  'good': r"""#include <iostream>
#include <string>
#include <stdexcept>
int main() {
    std::string s = "ab";
    try { char c = s.at(5); std::cout << c << '\n'; }   // 범위 밖이면 예외
    catch (const std::out_of_range&) { std::cout << "out of range\n"; }
}""",
  'why':'근거: std::string::operator[] 는 컨테이너와 마찬가지로 범위를 검사하지 않아 size() 이상의 인덱스 접근은 미정의 동작이다. 영향: 길이를 넘는 읽기는 인접 메모리 내용을 노출하거나 쓰기 시 손상을 일으키며, 외부 입력 인덱스면 보안 결함이 된다. 대응: 인덱스를 size() 와 비교하거나 예외를 던지는 at() 으로 안전하게 접근한다.',
  'why_en':'Rationale: std::string::operator[], like a container, does not check bounds, so accessing an index at or beyond size() is undefined behaviour. Impact: a read past the length exposes adjacent memory contents, a write corrupts it, and an externally supplied index makes it a security flaw. Fix: compare the index against size() or access safely via at(), which throws on out-of-range.'},

 {'id':'MEM50-CPP','cat':'MEM · Rule · L1','compiles':True,
  'title':'해제된 메모리에 접근하지 않는다(use-after-free)',
  'title_en':'Do not access freed memory',
  'bad': r"""#include <iostream>
int main() {
    int* p = new int(5);
    delete p;             // 메모리 해제
    *p = 7;               // 해제 후 사용 — 미정의 동작
    std::cout << *p << '\n';
}""",
  'good': r"""#include <iostream>
#include <memory>
int main() {
    auto p = std::make_unique<int>(5);
    *p = 7;               // 스코프 종료 시 자동 해제 — 댕글링 불가능
    std::cout << *p << '\n';
}""",
  'why':'근거: delete 후의 포인터는 댕글링 상태가 되어, 그것을 역참조해 읽거나 쓰는 것은 미정의 동작이다(해당 메모리가 이미 다른 객체에 재사용됐을 수 있다). 영향: use-after-free 는 힙 메타데이터·다른 객체를 손상시키고, 공격자가 해제와 재할당 사이를 노리면 정보 유출·임의 코드 실행으로 악용된다. 대응: RAII 스마트 포인터(unique_ptr/shared_ptr)로 수명을 소유권에 묶어 수동 delete 와 댕글링을 제거한다.',
  'why_en':'Rationale: a pointer after delete is dangling, and dereferencing it to read or write is undefined behaviour, since that memory may already be reused by another object. Impact: a use-after-free corrupts heap metadata and other objects, and an attacker timing the gap between free and reallocation can exploit it for information disclosure or arbitrary code execution. Fix: tie lifetime to ownership with RAII smart pointers (unique_ptr/shared_ptr), eliminating manual delete and dangling.'},

 {'id':'MEM51-CPP','cat':'MEM · Rule · L1','compiles':True,
  'title':'동적 자원을 올바른 형식으로 해제한다',
  'title_en':'Properly deallocate dynamically allocated resources',
  'bad': r"""#include <iostream>
int main() {
    int* a = new int[10];   // 배열 형태로 할당
    a[0] = 1;
    delete a;               // new[] 를 delete 로 해제 — 미정의 동작
    std::cout << "done\n";
}""",
  'good': r"""#include <iostream>
#include <vector>
int main() {
    std::vector<int> a(10);   // 컨테이너가 올바른 해제를 보장
    a[0] = 1;
    std::cout << a[0] << '\n';
}""",
  'why':'근거: new 와 new[] 는 서로 다른 할당 경로를 쓰며, 표준은 new 는 delete 로, new[] 는 delete[] 로만 해제하도록 요구한다. 영향: 형식이 어긋나면 배열 원소 소멸자가 호출되지 않거나 잘못된 크기로 반환되어 힙이 손상되는 미정의 동작이 된다. 대응: 직접 new/delete 대신 std::vector 나 std::make_unique<T[]> 로 할당·해제를 자동화한다.',
  'why_en':'Rationale: new and new[] use different allocation paths, and the standard requires new to be matched with delete and new[] with delete[]. Impact: a mismatch skips element destructors or frees with the wrong size, corrupting the heap — undefined behaviour. Fix: replace raw new/delete with std::vector or std::make_unique<T[]> to automate matched allocation and deallocation.'},

 {'id':'MEM52-CPP','cat':'MEM · Rule · L1','compiles':True,
  'title':'메모리 할당 오류를 검출하고 처리한다',
  'title_en':'Detect and handle memory allocation errors',
  'bad': r"""#include <iostream>
#include <cstdlib>
int main() {
    std::size_t n = 1000;
    int* p = static_cast<int*>(std::malloc(n * sizeof(int)));
    p[0] = 1;             // malloc 실패(nullptr) 미검사 → 널 역참조 가능
    std::cout << p[0] << '\n';
    std::free(p);
}""",
  'good': r"""#include <iostream>
#include <memory>
#include <new>
int main() {
    std::size_t n = 1000;
    try {
        auto p = std::make_unique<int[]>(n);   // 실패 시 std::bad_alloc
        p[0] = 1;
        std::cout << p[0] << '\n';
    } catch (const std::bad_alloc&) { std::cout << "alloc failed\n"; }
}""",
  'why':'근거: malloc 은 실패 시 nullptr 을 반환하고 new 는 std::bad_alloc 을 던지는데, 두 신호 모두 처리하지 않으면 실패가 정상 흐름으로 새어든다. 영향: 검사 없이 malloc 반환을 역참조하면 널 포인터 역참조로 크래시가 나고, 일부 환경에서는 공격 가능한 상태가 된다. 대응: malloc 반환을 nullptr 과 비교해 처리하거나, new 의 bad_alloc 예외를 catch 한다.',
  'why_en':'Rationale: malloc returns nullptr on failure and new throws std::bad_alloc, and ignoring either signal lets a failure leak into normal flow. Impact: dereferencing an unchecked malloc result is a null-pointer dereference that crashes, and in some environments leaves an exploitable state. Fix: compare the malloc result against nullptr and handle it, or catch the bad_alloc exception from new.'},

 {'id':'MEM53-CPP','cat':'MEM · Rule · L2','compiles':True,
  'title':'수동 수명 관리 시 객체를 명시적으로 생성·소멸한다',
  'title_en':'Explicitly construct and destruct objects when manually managing object lifetime',
  'bad': r"""#include <iostream>
#include <string>
struct S { std::string name = "init"; void use(){ std::cout << name << '\n'; } };
int main() {
    alignas(S) unsigned char buf[sizeof(S)];
    S* p = reinterpret_cast<S*>(buf);   // 생성자 미호출 — name 미초기화
    p->use();                           // 불변식 미성립 객체 사용 — 미정의 동작
}""",
  'good': r"""#include <iostream>
#include <string>
#include <new>
struct S { std::string name = "init"; void use(){ std::cout << name << '\n'; } };
int main() {
    alignas(S) unsigned char buf[sizeof(S)];
    S* p = new (buf) S();   // placement new 로 명시적 생성
    p->use();
    p->~S();                // 명시적 소멸
}""",
  'why':'근거: 원시 바이트 저장소를 객체 타입으로 캐스트만 하면 생성자가 실행되지 않아, 멤버 초기화와 클래스 불변식이 성립하지 않은 채 객체로 취급된다. 영향: 미초기화된 std::string 같은 멤버를 사용하면 잘못된 내부 포인터를 따라가 크래시·손상이 나고, 소멸도 누락된다. 대응: 수동 저장소에서는 placement new 로 생성하고, 사용 후 소멸자를 명시적으로 호출한다.',
  'why_en':'Rationale: merely casting raw byte storage to an object type does not run the constructor, so the object is treated as live without member initialization or class invariants. Impact: using a member like an uninitialized std::string follows an invalid internal pointer and crashes or corrupts, and destruction is also missed. Fix: construct with placement new in manual storage and call the destructor explicitly after use.'},

 {'id':'MEM54-CPP','cat':'MEM · Rule · L1','compiles':True,
  'title':'placement new 에 적절히 정렬된 충분한 저장소를 제공한다',
  'title_en':'Provide placement new with properly aligned pointers to sufficient storage capacity',
  'bad': r"""#include <iostream>
#include <new>
#include <cstdint>
struct alignas(16) Vec4 { double a, b; };   // 16바이트 정렬 요구
int main() {
    unsigned char buf[sizeof(Vec4)];   // 정렬 미보장 — char 배열은 1바이트 정렬
    Vec4* p = new (buf) Vec4{1, 2};     // 오정렬 저장소에 배치 — 미정의 동작
    std::cout << p->a << '\n';
}""",
  'good': r"""#include <iostream>
#include <new>
struct alignas(16) Vec4 { double a, b; };
int main() {
    alignas(Vec4) unsigned char buf[sizeof(Vec4)];   // 대상 타입 정렬 보장
    Vec4* p = new (buf) Vec4{1, 2};
    std::cout << p->a << '\n';
    p->~Vec4();
}""",
  'why':'근거: placement new 는 주어진 주소에 그대로 객체를 배치할 뿐 정렬을 보정하지 않으므로, 저장소가 대상 타입의 정렬 요건을 만족해야 한다. 영향: 과도 정렬(alignas) 타입을 1바이트 정렬 버퍼에 배치하면 일부 아키텍처에서 정렬 폴트가 나거나 SIMD 명령이 실패하는 미정의 동작이 된다. 대응: 저장소를 alignas(대상 타입) 으로 선언하거나 std::aligned_alloc 으로 정렬된 메모리를 확보한다.',
  'why_en':'Rationale: placement new simply constructs an object at the given address without correcting alignment, so the storage must meet the alignment requirement of the target type. Impact: placing an over-aligned (alignas) type into a 1-byte-aligned buffer causes alignment faults or failed SIMD instructions on some architectures — undefined behaviour. Fix: declare the storage with alignas(target type) or obtain aligned memory via std::aligned_alloc.'},

 {'id':'MEM56-CPP','cat':'MEM · Rule · L1','compiles':True,
  'title':'이미 소유된 포인터를 무관한 스마트 포인터에 저장하지 않는다',
  'title_en':'Do not store an already-owned pointer value in an unrelated smart pointer',
  'bad': r"""#include <iostream>
#include <memory>
int main() {
    int* raw = new int(1);
    std::shared_ptr<int> a(raw);
    std::shared_ptr<int> b(raw);   // 같은 raw 로 독립 제어블록 2개 — 이중 해제
    std::cout << *a << '\n';
}                                   // a, b 소멸 시 raw 를 두 번 delete""",
  'good': r"""#include <iostream>
#include <memory>
int main() {
    auto a = std::make_shared<int>(1);
    std::shared_ptr<int> b = a;    // 같은 제어블록 공유 — 참조 카운트 2
    std::cout << *a << " count=" << a.use_count() << '\n';
}""",
  'why':'근거: shared_ptr 는 자신이 생성한 제어 블록으로 참조 수를 추적하는데, 같은 raw 포인터로 별개의 shared_ptr 두 개를 생성하면 제어 블록이 둘로 나뉘어 서로의 존재를 모른다. 영향: 두 shared_ptr 가 각자 참조 수를 0 으로 떨어뜨리며 같은 메모리를 두 번 delete 해 이중 해제로 힙이 손상된다. 대응: 소유권은 make_shared 로 한 번 만들고 복사로 공유하며, 단일 소유는 unique_ptr 로 표현한다.',
  'why_en':'Rationale: a shared_ptr tracks references with the control block it created, but constructing two separate shared_ptrs from the same raw pointer creates two control blocks that are unaware of each other. Impact: each shared_ptr drives its own reference count to zero and deletes the same memory twice, a double free that corrupts the heap. Fix: create ownership once with make_shared and share by copying, and express single ownership with unique_ptr.'},

 {'id':'MEM57-CPP','cat':'MEM · Rule · L2','compiles':True,
  'title':'과도 정렬(over-aligned) 타입에 기본 operator new 가정에 의존하지 않는다',
  'title_en':'Avoid using default operator new for over-aligned types',
  'bad': r"""#include <iostream>
#include <cstdint>
struct alignas(64) CacheLine { char data[64]; };   // 캐시라인 정렬 요구
int main() {
    CacheLine* p = new CacheLine();   // 정렬 인식 new 미지원 환경에선 64B 정렬 미보장
    bool aligned = (reinterpret_cast<std::uintptr_t>(p) % 64) == 0;
    std::cout << (aligned ? "aligned" : "MISALIGNED") << '\n';
    delete p;
}""",
  'good': r"""#include <iostream>
#include <cstdlib>
#include <new>
#include <cstdint>
struct alignas(64) CacheLine { char data[64]; };
int main() {
    void* m = std::aligned_alloc(64, sizeof(CacheLine));   // 정렬 보장 할당
    CacheLine* p = new (m) CacheLine();
    bool aligned = (reinterpret_cast<std::uintptr_t>(p) % 64) == 0;
    std::cout << (aligned ? "aligned" : "MISALIGNED") << '\n';
    p->~CacheLine();
    std::free(m);
}""",
  'why':'근거: C++17 이전 또는 정렬 인식 operator new 를 제공하지 않는 구현에서는 기본 할당자가 기본 정렬(보통 16바이트)까지만 보장하므로, 확장 정렬을 요구하는 타입이 오정렬될 수 있다. 영향: SIMD 레지스터 로드나 캐시라인 정렬을 가정한 코드가 오정렬 메모리에서 정렬 폴트·성능 저하·미정의 동작을 일으킨다. 대응: 정렬 인식 operator new 를 쓰거나 std::aligned_alloc 으로 정렬을 명시 보장한 뒤 placement new 한다.',
  'why_en':'Rationale: before C++17, or on implementations without an alignment-aware operator new, the default allocator only guarantees default alignment (typically 16 bytes), so a type requiring extended alignment can be misaligned. Impact: code assuming SIMD register loads or cache-line alignment hits alignment faults, performance loss, or undefined behaviour on misaligned memory. Fix: use an alignment-aware operator new, or guarantee alignment explicitly with std::aligned_alloc followed by placement new.'},

 {'id':'CTR52-CPP','cat':'CTR · Rule · L2','compiles':True,
  'title':'컨테이너 연산이 용량을 넘쳐 오버플로우하지 않게 한다',
  'title_en':'Guarantee that library functions do not overflow',
  'bad': r"""#include <iostream>
#include <vector>
#include <cstdint>
int main() {
    std::vector<int> v;
    std::size_t huge = SIZE_MAX / 2;   // 거대한 요청
    v.reserve(huge);                   // max_size 초과 → length_error/실패
    std::cout << v.capacity() << '\n';
}""",
  'good': r"""#include <iostream>
#include <vector>
#include <cstdint>
int main() {
    std::vector<int> v;
    std::size_t huge = SIZE_MAX / 2;
    if (huge <= v.max_size()) v.reserve(huge);   // 한계 검증 후 예약
    else std::cout << "request exceeds max_size\n";
    std::cout << v.capacity() << '\n';
}""",
  'why':'근거: reserve·resize 에 전달한 원소 수에 원소 크기를 곱한 바이트 수가 size_t 범위를 넘거나 max_size() 를 초과하면 컨테이너가 할당을 수행할 수 없다. 영향: 검증 없이 거대한 값을 넘기면 std::length_error 나 bad_alloc 으로 갑작스러운 종료가 되고, 곱셈이 오버플로우하면 의도보다 작은 버퍼가 할당되어 이후 접근이 경계를 넘는다. 대응: 요청 크기를 max_size() 와 비교해 한계 안에서만 예약·확장한다.',
  'why_en':'Rationale: if the requested element count times the element size exceeds the size_t range or max_size(), the container cannot perform the allocation. Impact: passing a huge value unchecked aborts abruptly via std::length_error or bad_alloc, and if the multiplication overflows, a smaller-than-intended buffer is allocated so later accesses run past the boundary. Fix: compare the requested size against max_size() and reserve or grow only within the limit.'},
]
