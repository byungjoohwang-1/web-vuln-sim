# -*- coding: utf-8 -*-
"""MISRA C++:2023 수기 보강 예제.
로컬 PDF에 분리 가능한 bad/good 코드 블록이 없던(지시어·전처리·헤더 금지) 룰에
대해, 규칙 의미를 개념적으로 재구성한 자체 작성 예제를 제공한다.
원문(규범 텍스트·예제 코드) 비복제 — 규칙 ID/제목/분류만 표준에서 인용한다.
gen_standards.merge_pdf_full_rules() 가 id 로 매칭해 PDF 룰 위에 덮어쓴다."""

RULES = [
    {
        'id': 'Dir 0.3.1',
        'cat': 'Advisory',
        'title': '부동소수점 연산을 적절히 사용해야 한다',
        'title_en': 'Floating-point arithmetic should be used appropriately',
        'bad': (
            'bool isNan(double d) {\n'
            '    return d == std::numeric_limits<double>::quiet_NaN(); // NaN==x 는 항상 false\n'
            '}\n'
            'bool equal(double a, double b) {\n'
            '    return a == b;   // 부동소수 정확 비교 — 반올림 오차로 실패\n'
            '}'
        ),
        'good': (
            '#include <cmath>\n'
            '#include <algorithm>\n'
            'bool isNan(double d) { return std::isnan(d); }\n'
            'bool equal(double a, double b) {\n'
            '    return std::abs(a - b) <= 1e-9 * std::max(std::abs(a), std::abs(b));\n'
            '}'
        ),
        'why': '부동소수의 안전한 사용은 높은 수치해석 지식을 요구한다. NaN/무한대/정밀도 손실/상쇄 오차 등을 고려하지 않은 == 비교나 quiet_NaN 비교는 잘못된 결과를 낳는다.',
        'why_en': 'Safe floating-point use needs strong numerical-analysis knowledge; naive == comparisons or comparing against quiet_NaN ignore NaN/infinity/precision-loss/cancellation and give wrong results.',
    },
    {
        'id': 'Dir 0.3.2',
        'cat': 'Required',
        'title': '함수 호출은 함수의 전제조건을 위반하지 않아야 한다',
        'title_en': "A function call shall not violate the function's preconditions",
        'bad': (
            'int first(const std::vector<int>& v) {\n'
            '    return v.front();   // 전제조건(비어있지 않음) 위반 시 미정의 동작\n'
            '}\n'
            'int caller() {\n'
            '    std::vector<int> empty;\n'
            '    return first(empty);  // 빈 벡터로 호출 → 전제조건 위반\n'
            '}'
        ),
        'good': (
            '#include <optional>\n'
            'std::optional<int> first(const std::vector<int>& v) {\n'
            '    if (v.empty()) return std::nullopt;  // 전제조건을 호출 전에 보장\n'
            '    return v.front();\n'
            '}'
        ),
        'why': '함수의 암시적·명시적 전제조건(비어있지 않은 컨테이너, 0이 아닌 제수 등)을 위반하면 예기치 못한 결과나 미정의 동작이 발생한다. 호출 전에 전제조건을 보장해야 한다.',
        'why_en': "Violating a function's implicit or explicit preconditions (non-empty container, non-zero divisor, …) causes unexpected results or undefined behaviour; guarantee preconditions before calling.",
    },
    {
        'id': 'Rule 18.5.2',
        'cat': 'Advisory · Decidable',
        'title': '프로그램 종료 함수를 사용하지 않아야 한다',
        'title_en': 'Program-terminating functions should not be used',
        'bad': (
            'void load(const Config& c) {\n'
            '    if (!c.valid()) {\n'
            '        std::exit(1);   // 스택 언와인딩·소멸자 호출 없이 즉시 종료\n'
            '    }\n'
            '}'
        ),
        'good': (
            'struct ConfigError {};\n'
            'void load(const Config& c) {\n'
            '    if (!c.valid()) {\n'
            '        throw ConfigError{};  // 예외로 정상 언와인딩 → 소멸자가 자원 해제\n'
            '    }\n'
            '}'
        ),
        'why': 'abort/exit/_Exit/quick_exit/terminate 호출은 스택 언와인딩과 소멸자 호출을 건너뛰어, 잠긴 파일 등 자원을 비정상 상태로 남길 수 있다. 예외나 반환값으로 정상 흐름을 통해 종료해야 한다.',
        'why_en': 'Calling abort/exit/_Exit/quick_exit/terminate skips stack unwinding and destructors, potentially leaving resources (e.g. a locked file) in a bad state; signal termination via exceptions or return values instead.',
    },
    {
        'id': 'Rule 19.3.1',
        'cat': 'Advisory · Decidable',
        'title': '# 및 ## 전처리기 연산자를 사용하지 않아야 한다',
        'title_en': 'The # and ## preprocessor operators should not be used',
        'bad': (
            '#define NAME(x)   #x        // 스트링화(stringize) 연산자\n'
            '#define JOIN(a,b) a##b      // 토큰 결합(concatenation) 연산자\n'
            'const char* s = NAME(value);\n'
            'int JOIN(foo, 1) = 0;'
        ),
        'good': (
            '// 전처리기 # / ## 대신 타입 안전한 언어 기능 사용\n'
            'constexpr const char* s = "value";\n'
            'int foo1 = 0;\n'
            'template <class T> const char* name();  // 필요 시 함수/템플릿으로 대체'
        ),
        'why': '여러 #/## 또는 혼합 사용 시 평가 순서가 unspecified 라 매크로 확장 결과를 예측하기 어렵고, ## 는 코드 가독성을 떨어뜨린다. constexpr·템플릿 등 언어 기능으로 대체한다.',
        'why_en': 'The evaluation order of multiple/mixed # and ## operators is unspecified, making macro expansion unpredictable, and ## hurts readability; replace with language features such as constexpr and templates.',
    },
    {
        'id': 'Rule 21.2.3',
        'cat': 'Required · Decidable',
        'title': '<cstdlib>의 system 함수를 사용하지 않아야 한다',
        'title_en': 'The library function system from <cstdlib> shall not be used',
        'bad': (
            '#include <cstdlib>\n'
            'void run(const std::string& name) {\n'
            '    std::system(("rm " + name).c_str());  // 셸 주입·미정의 동작 위험\n'
            '}'
        ),
        'good': (
            '#include <cstdio>\n'
            'void run(const std::string& path) {\n'
            '    std::remove(path.c_str());  // 셸을 거치지 않는 표준 API 사용\n'
            '}'
        ),
        'why': 'system 은 미정의·구현 정의 동작을 가지며 명령 주입 등 보안 취약점의 흔한 원인이다(<stdlib.h> 의 system 에도 동일 적용). 셸을 거치지 않는 전용 API로 대체한다.',
        'why_en': 'system has undefined and implementation-defined behaviour and is a common source of security flaws such as command injection (the same applies to system from <stdlib.h>); use dedicated, non-shell APIs.',
    },
    {
        'id': 'Rule 21.10.3',
        'cat': 'Required · Decidable',
        'title': '<csignal> 표준 헤더가 제공하는 기능을 사용하지 않아야 한다',
        'title_en': 'The facilities provided by the standard header file <csignal> shall not be used',
        'bad': (
            '#include <csignal>\n'
            'volatile std::sig_atomic_t g_stop = 0;\n'
            'void onSig(int) { g_stop = 1; }     // 시그널 핸들러 내 동작 제약·미정의 위험\n'
            'void setup() { std::signal(SIGINT, onSig); }'
        ),
        'good': (
            '// 시그널 핸들링 대신 협조적 종료 플래그를 일반 제어 흐름으로 관리\n'
            '#include <atomic>\n'
            'std::atomic<bool> g_stop{false};\n'
            'void request_stop() { g_stop.store(true); }  // <csignal> 미사용'
        ),
        'why': '부적절한 시그널 처리는 미정의·구현 정의 동작을 유발한다(<signal.h> 에도 동일 적용). 일반 제어 흐름으로 종료를 관리하라. (예외: 시그널을 끄기 위한 signal(x, SIG_IGN) 호출은 허용)',
        'why_en': 'Inappropriate signal handling causes undefined and implementation-defined behaviour (the same applies to <signal.h>); manage termination via normal control flow. (Exception: signal(x, SIG_IGN) to disable a signal is permitted.)',
    },
]
