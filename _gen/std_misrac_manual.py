# -*- coding: utf-8 -*-
"""MISRA C:2012 수기 보강 예제.
로컬 PDF에 분리 가능한 bad/good 코드 블록이 없던(지시어·구문·헤더 규칙) 룰에
대해, 규칙 의미를 개념적으로 재구성한 자체 작성 예제를 제공한다.
원문(규범 텍스트·예제 코드) 비복제 — 규칙 ID/제목/분류만 표준에서 인용한다.
gen_standards.merge_pdf_full_rules() 가 id 로 매칭해 PDF 룰 위에 덮어쓴다."""

RULES = [
    {
        'id': 'Dir 4.2',
        'cat': 'Advisory · Dir',
        'title': '어셈블리어 사용은 모두 문서화되어야 한다',
        'title_en': 'All usage of assembly language should be documented',
        'bad': (
            '/* 인라인 어셈블리에 사용 근거·C 연동 방식 설명이 전혀 없다 */\n'
            'void delay_cycles(void) {\n'
            '    __asm__("nop");   /* 왜 필요한지, 어떻게 연동되는지 문서 없음 */\n'
            '}'
        ),
        'good': (
            '/*\n'
            ' * [ASM 사용 근거] 타깃 MCU에서 1사이클 지연이 필요하며 C로는\n'
            ' *   컴파일러 최적화로 제거될 수 있어 NOP 명령을 직접 사용한다.\n'
            ' * [C-ASM 인터페이스] 입력/출력/clobber 없음. ARMv7-M nop 1개.\n'
            ' */\n'
            'void delay_cycles(void) {\n'
            '    __asm__ volatile("nop");\n'
            '}'
        ),
        'why': '어셈블리는 구현 정의(implementation-defined)이고 이식성이 없으므로, 사용 근거와 C와의 인터페이스 방식을 반드시 문서로 남겨 유지보수·이식 시 위험을 줄인다.',
        'why_en': 'Assembly is implementation-defined and non-portable, so document the rationale and the C-to-assembly interface to reduce maintenance and porting risk.',
    },
    {
        'id': 'Dir 4.8',
        'cat': 'Advisory · Dir',
        'title': '구조체/공용체 포인터가 역참조되지 않으면 구현을 숨겨야 한다',
        'title_en': 'If a pointer to a structure or union is never dereferenced within a translation unit, then the implementation of the object should be hidden',
        'bad': (
            '/* sensor.h — 구현 세부가 노출되어 외부에서 내부 멤버를 직접 변경할 수 있다 */\n'
            'typedef struct {\n'
            '    int32_t raw;\n'
            '    int32_t calibrated;   /* 내부 전용인데 외부 접근 가능 */\n'
            '} Sensor;\n'
            'void sensor_update(Sensor *s);'
        ),
        'good': (
            '/* sensor.h — 불완전 타입으로 구현을 숨긴다(opaque type) */\n'
            'typedef struct Sensor Sensor;        /* 정의는 sensor.c 안에만 존재 */\n'
            'Sensor *sensor_create(void);\n'
            'void    sensor_update(Sensor *s);\n'
            'int32_t sensor_value(const Sensor *s);  /* 접근은 함수로만 */'
        ),
        'why': '포인터를 역참조하지 않는다면 구현 세부가 필요 없으므로, 불완전 타입으로 감춰 의도치 않은 변경을 막고 모듈 경계를 명확히 한다.',
        'why_en': 'If the pointer is never dereferenced, the implementation details are unneeded; hide them behind an incomplete (opaque) type to prevent accidental modification and clarify module boundaries.',
    },
    {
        'id': 'Rule 1.1',
        'cat': 'Required · Decidable · Rule',
        'title': "표준 C 구문·제약을 위반하지 않고 구현의 변환 한계를 넘지 않아야 한다",
        'title_en': "The program shall contain no violations of the standard C syntax and constraints, and shall not exceed the implementation's translation limits",
        'bad': (
            '/* 표준 C 위반: 반환형 생략(암시적 int) + 프로토타입 없는 호출 */\n'
            'foo(void) {        /* C99에서 제거된 암시적 int */\n'
            '    bar();         /* bar 의 선언/프로토타입이 없음 */\n'
            '}                  /* 반환형이 있는데 값 미반환 */'
        ),
        'good': (
            'extern void bar(void);   /* 사용 전 프로토타입 선언 */\n'
            'int foo(void) {\n'
            '    bar();\n'
            '    return 0;            /* 표준 구문·제약 준수 */\n'
            '}'
        ),
        'why': '선택한 표준(C90/C99)이 정의한 기능만 사용해 구문·제약 위반과 변환 한계 초과를 피해야 정적 분석으로 검증 가능하고 동작이 예측된다.',
        'why_en': 'Use only features defined by the chosen Standard (C90/C99) so that the program is statically checkable and behaviour is predictable, avoiding syntax/constraint violations and translation-limit overruns.',
    },
    {
        'id': 'Rule 1.2',
        'cat': 'Advisory · Undecidable · Rule',
        'title': '언어 확장을 사용하지 않아야 한다',
        'title_en': 'Language extensions should not be used',
        'bad': (
            '/* GCC 확장에 의존 — 이식성 저하 */\n'
            '#define MAX(a,b) ({ typeof(a) _x=(a); typeof(b) _y=(b); _x>_y?_x:_y; })\n'
            'int arr[] = { [0 ... 3] = 1 };   /* GCC 범위 지정 초기화 확장 */'
        ),
        'good': (
            '/* 표준 C 기능만 사용 */\n'
            'static int imax(int a, int b) { return a > b ? a : b; }\n'
            'int arr[4] = { 1, 1, 1, 1 };'
        ),
        'why': '언어 확장에 의존하면 이식성이 떨어지고, 확장 동작이 문서로 충분히 보장되지 않아 위험하다. 불가피하게 쓸 경우 근거와 검증 방법을 문서화한다.',
        'why_en': 'Relying on language extensions reduces portability and their behaviour may be underspecified; if unavoidable, document the justification and how valid use is assured.',
    },
    {
        'id': 'Rule 4.2',
        'cat': 'Advisory · Decidable · Rule',
        'title': '트라이그래프를 사용하지 않아야 한다',
        'title_en': 'Trigraphs should not be used',
        'bad': (
            '/* "??)" 가 트라이그래프로 치환되어 의도와 다르게 해석된다 */\n'
            'const char *msg = "Enter date (yyyy-mm-dd??)";  /* ??) -> ] 로 치환 */'
        ),
        'good': (
            "/* '?' 중 하나를 이스케이프해 트라이그래프 형성을 막는다 */\n"
            'const char *msg = "Enter date (yyyy-mm-dd?\\?)";'
        ),
        'why': '트라이그래프(??x)는 전처리 이전에 다른 문자로 치환되어, 두 개의 물음표를 쓴 다른 의도와 혼동되고 예상치 못한 동작을 유발한다.',
        'why_en': 'Trigraphs (??x) are replaced before preprocessing and can be confused with other uses of two question marks, producing unexpected behaviour.',
    },
    {
        'id': 'Rule 6.2',
        'cat': 'Required · Decidable · Rule',
        'title': '단일 비트 명명 비트필드는 부호형이 아니어야 한다',
        'title_en': 'Single-bit named bit fields shall not be of a signed type',
        'bad': (
            'struct Flags {\n'
            '    signed int ready : 1;   /* 1비트 부호형: 표현 가능 값이 0과 -1 뿐 */\n'
            '    int        error : 1;   /* int 비트필드 = signed, 동일 문제 */\n'
            '};'
        ),
        'good': (
            'struct Flags {\n'
            '    unsigned int ready : 1;  /* 0 또는 1 을 명확히 표현 */\n'
            '    unsigned int error : 1;\n'
            '};'
        ),
        'why': '단일 비트 부호형 비트필드는 부호 비트 1개·값 비트 0개라 의미 있는 값을 담을 수 없다. 플래그는 unsigned 로 선언해야 의도대로 0/1 을 표현한다.',
        'why_en': 'A single-bit signed bit-field has one sign bit and zero value bits, so it cannot hold a meaningful value; declare flags as unsigned to represent 0/1 as intended.',
    },
    {
        'id': 'Rule 8.5',
        'cat': 'Required · Decidable · Rule',
        'title': '외부 객체/함수는 하나의 파일에서 단 한 번만 선언되어야 한다',
        'title_en': 'An external object or function shall be declared once in one and only one file',
        'bad': (
            '/* a.h */ extern int16_t g_count;   /* 선언 1 */\n'
            '/* b.h */ extern int16_t g_count;   /* 선언 2 — 두 헤더에 중복 선언 */'
        ),
        'good': (
            '/* shared.h — 외부 객체는 단 하나의 헤더에서만 선언 */\n'
            'extern int16_t g_count;\n'
            '/* shared.c */\n'
            '#include "shared.h"\n'
            'int16_t g_count = 0;   /* 정의는 한 곳 */'
        ),
        'why': '선언을 하나의 헤더로 단일화하면 선언과 정의, 그리고 서로 다른 번역 단위 간의 일관성이 보장되어 불일치로 인한 오류를 막는다.',
        'why_en': 'Keeping a single declaration in one header ensures consistency between the declaration and the definition, and across translation units, preventing mismatch errors.',
    },
    {
        'id': 'Rule 8.7',
        'cat': 'Advisory · Decidable · Rule',
        'title': '단일 번역 단위에서만 참조되는 함수/객체는 외부 링키지로 정의하지 않아야 한다',
        'title_en': 'Functions and objects should not be defined with external linkage if they are referenced in only one translation unit',
        'bad': (
            '/* util.c — 이 파일에서만 쓰는데 외부 링키지(전역)로 노출 */\n'
            'int helper_state = 0;\n'
            'void helper(void) { helper_state++; }'
        ),
        'good': (
            '/* util.c — 내부 링키지로 가시성을 제한 */\n'
            'static int helper_state = 0;\n'
            'static void helper(void) { helper_state++; }'
        ),
        'why': 'static 으로 가시성을 제한하면 다른 번역 단위에서 의도치 않게 접근/호출되거나 동일 식별자와 충돌할 가능성을 줄인다.',
        'why_en': 'Giving internal linkage with static reduces the chance of inadvertent access/calls from other translation units and of clashes with identical identifiers.',
    },
    {
        'id': 'Rule 8.10',
        'cat': 'Required · Decidable · Rule',
        'title': 'inline 함수는 static 저장 클래스로 선언되어야 한다',
        'title_en': 'An inline function shall be declared with the static storage class',
        'bad': (
            '/* 외부 링키지 inline — 정의가 없는 TU에서 호출 시 동작 미정의 */\n'
            'inline int square(int x) { return x * x; }'
        ),
        'good': (
            '/* static inline — 각 번역 단위에서 안전하게 인라인 */\n'
            'static inline int square(int x) { return x * x; }'
        ),
        'why': '외부 링키지 inline 함수가 같은 번역 단위에 정의되지 않으면 동작이 미정의이며, 외부 정의/인라인 정의 중 무엇이 호출될지 달라 실시간 타이밍에 영향을 줄 수 있다.',
        'why_en': 'An inline function with external linkage not defined in the same translation unit is undefined behaviour, and it is unspecified whether the external or inline definition is used, which can affect real-time timing.',
    },
    {
        'id': 'Rule 11.2',
        'cat': 'Required · Decidable · Rule',
        'title': '불완전 타입 포인터와 다른 타입 간 변환을 수행하지 않아야 한다',
        'title_en': 'Conversions shall not be performed between a pointer to an incomplete type and any other type',
        'bad': (
            'struct Opaque;                       /* 불완전 타입 */\n'
            'void use(struct Opaque *p) {\n'
            '    unsigned char *raw = (unsigned char *)p;  /* 불완전 타입 포인터를 변환 */\n'
            '    raw[0] = 0;                      /* 정렬/표현 미정의 동작 위험 */\n'
            '}'
        ),
        'good': (
            'struct Opaque;\n'
            'extern void opaque_reset(struct Opaque *p);  /* 변환 없이 전용 API로만 다룬다 */\n'
            'void use(struct Opaque *p) {\n'
            '    opaque_reset(p);\n'
            '}'
        ),
        'why': '불완전 타입 포인터를 다른 타입으로 변환하면 정렬이 맞지 않거나 부동소수 변환 시 항상 미정의 동작이 된다. 변환 없이 전용 API로만 다뤄야 한다.(void* 는 Rule 11.5 적용)',
        'why_en': 'Converting a pointer to an incomplete type may produce a misaligned pointer (and is always undefined with floating types); handle it only through dedicated APIs without conversion. (void* is covered by Rule 11.5.)',
    },
    {
        'id': 'Rule 15.3',
        'cat': 'Required · Decidable · Rule',
        'title': 'goto가 참조하는 라벨은 같은 블록이나 goto를 감싸는 블록에 선언되어야 한다',
        'title_en': 'Any label referenced by a goto statement shall be declared in the same block, or in any block enclosing the goto statement',
        'bad': (
            'void f(int a) {\n'
            '    if (a > 0) {\n'
            '        goto inner;   /* 바깥에서 안쪽(중첩) 블록 라벨로 점프 */\n'
            '    }\n'
            '    {\n'
            'inner:                /* goto 를 감싸지 않는 별도 블록 */\n'
            '        a = 0;\n'
            '    }\n'
            '}'
        ),
        'good': (
            'void f(int a) {\n'
            '    if (a > 0) {\n'
            '        goto done;    /* goto 를 감싸는 상위 블록의 라벨로만 점프 */\n'
            '    }\n'
            '    a = 1;\n'
            'done:\n'
            '    (void)a;\n'
            '}'
        ),
        'why': '중첩 블록으로 뛰어드는 goto 는 코드 구조를 무너뜨리고 가독성을 크게 해친다. 점프 대상은 같은 블록이나 goto 를 감싸는 블록의 라벨로 제한한다.',
        'why_en': 'A goto jumping into a nested block destroys structure and harms readability; restrict targets to labels in the same block or a block enclosing the goto.',
    },
    {
        'id': 'Rule 16.2',
        'cat': 'Required · Decidable · Rule',
        'title': 'switch 라벨은 가장 가까운 복합문이 switch 본문일 때만 사용해야 한다',
        'title_en': 'A switch label shall only be used when the most closely-enclosing compound statement is the body of a switch statement',
        'bad': (
            'switch (x) {\n'
            '    case 1:\n'
            '        if (flag) {\n'
            '    case 2:        /* if 블록 안의 case — switch 본문 최상위가 아님 */\n'
            '            x = 1;\n'
            '        }\n'
            '        break;\n'
            '    default:\n'
            '        break;\n'
            '}'
        ),
        'good': (
            'switch (x) {\n'
            '    case 1:\n'
            '        if (flag) { x = 1; }\n'
            '        break;\n'
            '    case 2:        /* 모든 라벨이 switch 본문 최상위에 위치 */\n'
            '        x = 1;\n'
            '        break;\n'
            '    default:\n'
            '        break;\n'
            '}'
        ),
        'why': '표준은 case/default 라벨을 switch 본문 안 어디에나 둘 수 있게 하지만, 이는 비구조적 코드(Duff’s device 류)를 만든다. 라벨은 switch 본문 복합문의 최상위에만 두어야 한다.',
        'why_en': 'The Standard allows case/default labels anywhere inside the switch body, enabling unstructured code; place labels only at the outermost level of the switch body compound statement.',
    },
    {
        'id': 'Rule 17.5',
        'cat': 'Advisory · Undecidable · Rule',
        'title': '배열 타입 매개변수에 대응하는 인자는 적절한 원소 수를 가져야 한다',
        'title_en': 'The function argument corresponding to a parameter declared to have an array type shall have an appropriate number of elements',
        'bad': (
            '/* 매개변수가 최소 4개 원소 배열을 기대한다고 선언 */\n'
            'void sum4(int a[4]);\n'
            'void caller(void) {\n'
            '    int two[2] = { 1, 2 };\n'
            '    sum4(two);     /* 원소 2개뿐 — 범위 밖 접근 위험 */\n'
            '}'
        ),
        'good': (
            'void sum4(int a[4]);\n'
            'void caller(void) {\n'
            '    int four[4] = { 1, 2, 3, 4 };\n'
            '    sum4(four);    /* 선언된 최소 원소 수를 충족 */\n'
            '}'
        ),
        'why': '크기를 명시한 배열 매개변수는 함수가 기대하는 최소 원소 수를 인터페이스로 드러낸다. 그보다 작은 배열을 넘기면 범위 밖 접근 위험이 생긴다.',
        'why_en': 'A sized array parameter documents the minimum number of elements the function expects; passing a smaller array risks out-of-bounds access.',
    },
]
