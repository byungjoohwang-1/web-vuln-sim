window.NETWORK_SYSTEM_CASEBOOK = {
  "version": "1.0.0",
  "cases": [
    {
      "id": "firewall",
      "title": "방화벽 변경 이후의 관리 포트 노출",
      "track": "network",
      "columns": [
        "timestamp",
        "src_ip",
        "dst_ip",
        "dst_port",
        "action",
        "rule_id",
        "bytes_out",
        "change_ticket"
      ],
      "intro": "가상 조직의 하루 방화벽 흐름입니다. CHG-042는 203.0.113.10에서 10.20.0.10의 TCP 22만 허용합니다. 실제 적중 규칙과 출발지를 비교하세요.",
      "questions": [
        "FW-900이 허용한 출발지는 승인된 주소뿐인가요?",
        "허용 로그와 계정 인증 성공을 구분할 추가 증거는 무엇인가요?",
        "BACKUP-10 통신과 외부 대량 송신의 차이는 무엇인가요?"
      ],
      "hints": [
        "먼저 rule_id=FW-900으로 범위를 좁혀보세요.",
        "198.51.100.77과 승인된 203.0.113.10을 구별하세요.",
        "백업 저장소는 10.40.0.20입니다. 허용된 세션도 대상 서버 기록이 필요합니다."
      ],
      "answer": "FW-900에는 승인 밖 출발지가 섞여 있습니다. 특정 연결 허용만으로 침해를 단정하지 말고 해당 시각의 관리 서버 인증과 후속 작업을 조사합니다.",
      "config": "[change CHG-042]\nsource = 203.0.113.10\ndestination = 10.20.0.10\nservice = tcp/22\nexpires = end-of-maintenance\n\n[current FW-900]\nsource = any\ndestination = 10.20.0.10\nservice = tcp/22\naction = allow"
    },
    {
      "id": "dns",
      "title": "정상 동적 질의와 조사할 DNS 패턴",
      "track": "network",
      "columns": [
        "timestamp",
        "client_ip",
        "query_name",
        "query_type",
        "rcode",
        "resolver",
        "latency_ms"
      ],
      "intro": "가상 단말의 DNS 관측 자료입니다. updates.example과 cdn.example은 승인 앱입니다. 이름의 길이만으로 공격을 판정하지 말고 10.10.3.77의 패턴과 변경 시간을 비교하세요.",
      "questions": [
        "같은 단말의 질의가 어떤 도메인에 집중되나요?",
        "NXDOMAIN과 SERVFAIL을 같은 원인으로 볼 수 있나요?",
        "추가로 필요한 단말 증거와 정상 대조군을 적어보세요."
      ],
      "hints": [
        "10.10.3.77 또는 review-zone.example을 검색하세요.",
        "긴 CDN 이름은 정상 대조군에도 있습니다.",
        "resolver=10.10.0.54의 변경 시간대에는 SERVFAIL 증가가 있습니다."
      ],
      "answer": "긴 이름과 실패 응답은 조사 단서이지 확정 증거가 아닙니다. 특정 단말의 반복 패턴과 전체 전달자 장애를 분리하고 실행 앱·승인 이력과 연결합니다.",
      "config": "[approved resolvers]\nprimary = 10.10.0.53\nsecondary = 10.10.0.54\n\n[change CHG-DNS-07]\nstart = 2026-09-14T12:00:00Z\nscope = secondary forwarder\nrollback = approved-previous-forwarder"
    },
    {
      "id": "authentication",
      "title": "원격 인증과 권한 사용의 시간 순서",
      "track": "linux",
      "columns": [
        "timestamp",
        "host",
        "service",
        "user",
        "source_ip",
        "outcome",
        "method",
        "session_id",
        "change_ticket"
      ],
      "intro": "가상 서버·VPN의 인증과 sudo 활동을 정규화한 자료입니다. ops-review 계정과 198.51.100.77의 실패·성공·후속 권한 사용을 조사하되 승인 유지보수와 구별하세요.",
      "questions": [
        "같은 세션으로 연결되는 사건은 무엇인가요?",
        "승인 작업과 계정 소유자 확인이 필요한 이유는?",
        "접근 제한과 업무 복구를 함께 수행할 계획을 작성하세요."
      ],
      "hints": [
        "ops-review로 검색해 시간 순으로 읽으세요.",
        "실패 뒤 성공한 세션의 sudo와 작업 번호를 비교하세요.",
        "success는 사용자 행위가 정당함을 증명하지 않습니다."
      ],
      "answer": "반복 실패 뒤 성공과 후속 권한 사용을 한 타임라인에 놓습니다. 승인 번호가 없는 경우에도 사용자·단말 확인을 거쳐 가설과 사실을 구분해 대응합니다.",
      "config": "[access policy]\nroot_direct_login = deny\nadmin_identity = named-account\nmfa = required-for-vpn\nsudo_scope = approved-role\n\n[maintenance]\naccounts = ops-maint\nchange_ticket = CHG-MAINT-18"
    },
    {
      "id": "integrity",
      "title": "기준선과 현재 파일 상태 비교",
      "track": "linux",
      "columns": [
        "timestamp",
        "host",
        "path",
        "baseline_mode",
        "current_mode",
        "baseline_owner",
        "current_owner",
        "change_ticket",
        "baseline_sha256",
        "current_sha256"
      ],
      "intro": "가상 자산 240대의 파일 상태 비교 자료입니다. 해시 차이, 권한 변경, 승인 패치, 일반 공유 데이터가 섞여 있습니다. 바이트 변화와 권한 변화를 따로 읽으세요.",
      "questions": [
        "내용 해시가 같아도 위험한 변화가 있나요?",
        "승인 패치와 승인 없는 설정 변경을 어떻게 구분하나요?",
        "authorized_keys·예약 작업·서비스 파일 중 무엇을 먼저 조사할까요?"
      ],
      "hints": [
        "current_mode=0777이나 Everyone:Modify를 검색하세요.",
        "baseline_sha256과 current_sha256이 같은 행도 권한 변화가 있을 수 있습니다.",
        "CHG-PATCH-18은 승인 패치이며, 빈 승인 번호는 추가 확인 대상입니다."
      ],
      "answer": "해시만 보지 말고 소유자·권한·파일 역할을 함께 봅니다. 고권한 서비스가 사용하는 쓰기 가능 파일은 우선 조사하고 승인된 변경만 기준선에 반영합니다.",
      "config": "[baseline]\nsource = approved-build-and-change-record\nwritable_by = integrity-admin-only\nmonitor = content,owner,permissions\n\n[approved deployment]\nchange_ticket = CHG-PATCH-18\nscope = approved-service-release\nunknown_changes = review-before-baseline-update"
    },
    {
      "id": "windows",
      "title": "Windows 로그인·권한·지속 실행 이벤트",
      "track": "windows",
      "columns": [
        "timestamp",
        "computer",
        "event_id",
        "user",
        "source_ip",
        "target",
        "logon_type",
        "change_ticket",
        "result"
      ],
      "intro": "원본 EVTX가 아니라 학습용 정규화 JSON입니다. 4624/4625 로그인, 4728 전역 보안 그룹 구성원 추가, 4698 예약 작업 생성, 4697 서비스 설치, 1102 로그 삭제를 관련 계정과 연결합니다.",
      "questions": [
        "4728의 대상 그룹이 중요한 이유는?",
        "예약 작업·서비스의 이름 외에 무엇을 조사하나요?",
        "1102가 나타나면 어떤 중앙 증거를 확보하나요?"
      ],
      "hints": [
        "event_id 또는 ops-review를 검색하세요.",
        "Domain Admins와 일반 업무 그룹을 구별하세요.",
        "설치·생성 이벤트 자체는 악성 여부를 확정하지 않습니다."
      ],
      "answer": "로그온, 그룹 구성원 변경, 작업·서비스 등록, 로그 삭제를 행위자와 시각으로 연결합니다. 각 단계에서 승인 내역과 실행 파일의 신뢰·권한을 별도로 확인합니다.",
      "config": "[audit coverage]\nlogon = success-and-failure\nsecurity_group_management = enabled\nscheduled_task_and_service = enabled\ncentral_forwarding = enabled\n\n[evidence model]\nformat = training-normalized-events\nnot_original_evtx = true"
    },
    {
      "id": "backup",
      "title": "백업 작업 결과와 복구 사본의 신뢰",
      "track": "windows",
      "columns": [
        "timestamp",
        "asset",
        "job_status",
        "restore_status",
        "retention_lock",
        "recovery_point",
        "rto_minutes",
        "restore_minutes",
        "source_sha256",
        "restored_sha256"
      ],
      "intro": "가상 자산 240대의 100일간 복구 점검 자료입니다. 작업 성공과 실제 복원 성공을 구분하고 해시 불일치, 미검증, 복구 시간 초과 사례를 찾아보세요.",
      "questions": [
        "job_status=success인데 복구가 준비되지 않은 행은?",
        "해시 일치만으로 RTO 충족을 판단할 수 있나요?",
        "사본 보호와 격리 복원, 원인 제거를 어떻게 연결하나요?"
      ],
      "hints": [
        "restore_status=mismatch 또는 not-tested를 찾아보세요.",
        "restore_minutes가 rto_minutes보다 큰 행도 따로 검토하세요.",
        "retention_lock은 사본 보호 단서이며 전체 복구 가능성의 보장은 아닙니다."
      ],
      "answer": "성공·실패·미검증을 구분하고 바이트 정합성과 업무 복구 시간·시점을 함께 평가합니다. 문제 사본을 숨기거나 정상으로 집계하지 말고 원인 조사와 재복원으로 확인합니다.",
      "config": "[recovery plan]\nrestore_environment = isolated\nsource_of_truth = approved-backup-manifest\nrto_minutes = per-asset-policy\nimmutable_copy = required\n\n[acceptance]\njob_status_alone = insufficient\ncheck = integrity,application,restore-time,recovery-point"
    }
  ],
  "glossary": [
    [
      "기준선",
      "승인된 상태를 비교 기준으로 보존한 기록. 차이가 있다고 항상 공격은 아니며 승인 변경과 대조합니다."
    ],
    [
      "유효 권한",
      "개별 허용 항목만이 아니라 그룹, 상속, 제한을 함께 평가한 실제 접근 범위입니다."
    ],
    [
      "상관 분석",
      "사용자·세션·자산·시각처럼 관련 키를 사용해 여러 기록을 연결하는 작업입니다."
    ],
    [
      "정상 대조군",
      "같은 환경의 승인된 정상 활동. 의심 패턴이 정말 다른지 비교할 기준입니다."
    ],
    [
      "RTO",
      "복구에 허용되는 목표 시간. 백업 생성 성공이나 파일 해시 일치만으로 충족되지 않습니다."
    ],
    [
      "복구 시점",
      "복원할 데이터가 어느 시점의 상태인지 나타냅니다. 가장 최신 파일이 항상 신뢰 가능한 사본은 아닙니다."
    ],
    [
      "무결성",
      "자료가 의도하지 않게 바뀌었는지 판단하는 속성. 해시 비교만으로 변경 승인을 증명하지 않습니다."
    ],
    [
      "증거와 가설",
      "기록으로 확인한 사실과 추가 확인이 필요한 설명을 구분해 작성합니다."
    ],
    [
      "최소 권한",
      "업무에 필요한 자원·행위·기간으로 접근을 제한하는 원칙입니다."
    ],
    [
      "중앙 수집",
      "원본 장비 외부에 기록을 모으는 방식. 전달 누락과 저장소 권한도 관리해야 합니다."
    ]
  ]
};
