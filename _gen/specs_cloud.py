# -*- coding: utf-8 -*-
"""주요정보통신기반시설 클라우드·컨테이너 보안 점검 항목 20종 (정적 스펙)."""

HOST = 'cloud$'


def C(code, title, icon, cat, sev, desc, vt, st, fixes, chk, ref):
    return {'file': '11_cloud-%s.html' % code.lower().replace('-', ''),
            'code': code, 'title': title, 'icon': icon, 'category': '클라우드/컨테이너 · ' + cat, 'severity': sev,
            'description': desc, 'vuln_term': vt, 'secure_term': st, 'host': HOST,
            'fix_steps': fixes, 'checklist': chk, 'kisa_ref': ref}


SPECS = [
# ===== 계정/권한(IAM) =====
C('C-01', '루트 계정 MFA 미적용', '🔑', '계정/권한', '상',
  '최상위 권한인 루트(root) 계정에 다중인증(MFA)이 없으면 비밀번호 유출만으로 클라우드 전체가 장악됩니다. 루트 계정에 MFA를 적용해야 합니다.',
  [('cmt', '# 루트 MFA 상태'), ('prompt', '$ aws iam get-account-summary'), ('bad', 'AccountMFAEnabled: 0'), ('warn', '→ 비밀번호 유출 시 전체 장악')],
  [('cmt', '# MFA 활성화'), ('prompt', '$ aws iam enable-mfa-device ...'), ('good', 'AccountMFAEnabled: 1'), ('good', '→ 2차 인증으로 보호')],
  ['루트 계정에 하드웨어/가상 MFA를 등록합니다.', '루트 사용을 최소화하고 일상 작업은 IAM 사용자로 수행합니다.'],
  ['루트 계정 MFA가 활성화됨', '루트 사용이 최소화됨'],
  '클라우드 계정 관리 > 루트 MFA'),

C('C-02', '과도한 IAM 권한(AdministratorAccess)', '👑', '계정/권한', '상',
  '모든 사용자/역할에 관리자 권한을 부여하면 한 자격증명만 탈취돼도 전체가 위험합니다. 최소 권한 원칙으로 필요한 권한만 부여해야 합니다.',
  [('cmt', '# 권한 점검'), ('prompt', '$ aws iam list-attached-user-policies --user-name dev'), ('bad', 'AdministratorAccess (전체 권한)'), ('warn', '→ 한 키 탈취로 전체 장악')],
  [('cmt', '# 최소 권한'), ('prompt', '$ aws iam attach-user-policy --policy S3ReadOnly'), ('good', '필요한 권한만 부여'), ('good', '→ 피해 범위 최소화')],
  ['AdministratorAccess 등 과도 권한을 회수하고 업무에 필요한 정책만 부여합니다.', '권한 분석 도구(Access Analyzer)로 미사용 권한을 정리합니다.'],
  ['과도한 관리자 권한이 회수됨', '최소 권한 정책이 적용됨'],
  '클라우드 계정 관리 > IAM 최소 권한'),

C('C-03', '액세스 키 노출·장기 미교체', '🗝️', '계정/권한', '상',
  '액세스 키가 코드/이미지에 하드코딩되거나 장기간 교체되지 않으면 유출 시 지속적으로 악용됩니다. 키를 안전 보관하고 주기적으로 교체해야 합니다.',
  [('cmt', '# 키 사용 이력'), ('prompt', '$ aws iam list-access-keys'), ('bad', 'AKIA... CreateDate 700일 전 (미교체)'), ('warn', '→ 유출 키 장기 악용')],
  [('cmt', '# 교체/시크릿 관리'), ('prompt', '$ aws iam create-access-key ; rotate'), ('good', 'Secrets Manager + 90일 교체'), ('good', '→ 노출/장기키 위험 감소')],
  ['키를 코드에 하드코딩하지 말고 Secrets Manager/Vault로 관리합니다.', '키를 주기적으로 교체하고 미사용 키를 제거합니다.', '가능하면 키 대신 임시 자격증명(IAM Role)을 사용합니다.'],
  ['액세스 키가 안전하게 보관됨', '키가 주기적으로 교체됨'],
  '클라우드 계정 관리 > 액세스 키'),

C('C-04', '미사용 자격증명 제거', '🧹', '계정/권한', '중',
  '퇴직자·미사용 계정/키/역할이 남아 있으면 비인가 접근 경로가 됩니다. 주기적으로 정리해야 합니다.',
  [('cmt', '# 미사용 자격증명'), ('prompt', '$ aws iam get-credential-report'), ('bad', 'user old-dev: last_used 200일 전'), ('warn', '→ 방치된 접근 경로')],
  [('cmt', '# 비활성/삭제'), ('prompt', '$ aws iam delete-access-key / delete-user'), ('good', '미사용 자격증명 정리'), ('good', '→ 공격면 축소')],
  ['미사용 사용자/키/역할을 비활성화·삭제합니다.', '자격증명 보고서를 주기적으로 검토합니다.'],
  ['미사용 자격증명이 정리됨'],
  '클라우드 계정 관리 > 미사용 자격증명'),

# ===== 스토리지/데이터 =====
C('C-05', '스토리지 버킷 퍼블릭 노출', '🪣', '스토리지', '상',
  '오브젝트 스토리지(S3 등) 버킷이 퍼블릭으로 공개되면 누구나 데이터를 다운로드할 수 있습니다. 퍼블릭 접근을 차단해야 합니다.',
  [('cmt', '# 버킷 공개 여부'), ('prompt', '$ aws s3api get-bucket-acl --bucket data'), ('bad', 'AllUsers: READ (퍼블릭)'), ('warn', '→ 누구나 데이터 열람')],
  [('cmt', '# 퍼블릭 차단'), ('prompt', '$ aws s3api put-public-access-block ...'), ('good', 'BlockPublicAcls: true'), ('good', '→ 외부 접근 차단')],
  ['Block Public Access를 활성화하고 버킷/객체 ACL의 퍼블릭 권한을 제거합니다.', '필요 시 서명 URL/CloudFront로 제한적으로 제공합니다.'],
  ['버킷 퍼블릭 접근이 차단됨', '퍼블릭 ACL이 제거됨'],
  '클라우드 스토리지 > 퍼블릭 노출'),

C('C-06', '저장 데이터 암호화 미적용', '🔐', '스토리지', '상',
  '스토리지/볼륨/DB의 저장 데이터가 암호화되지 않으면 스냅샷·디스크 탈취 시 평문 노출됩니다. 저장 시 암호화(SSE/KMS)를 적용해야 합니다.',
  [('cmt', '# 암호화 여부'), ('prompt', '$ aws s3api get-bucket-encryption --bucket data'), ('bad', 'ServerSideEncryption: none'), ('warn', '→ 스냅샷 탈취 시 평문')],
  [('cmt', '# 암호화 적용'), ('prompt', '$ aws s3api put-bucket-encryption (aws:kms)'), ('good', 'SSE-KMS 적용'), ('good', '→ 저장 데이터 보호')],
  ['스토리지/볼륨/DB에 저장 암호화(SSE-KMS 등)를 적용합니다.', 'KMS 키 접근 권한을 최소화합니다.'],
  ['저장 데이터 암호화가 적용됨', 'KMS 키 권한이 제한됨'],
  '클라우드 스토리지 > 저장 암호화'),

C('C-07', '스냅샷·이미지 공개 노출', '📸', '스토리지', '상',
  'EBS 스냅샷·머신 이미지(AMI)가 퍼블릭으로 공유되면 내부 데이터·자격증명이 외부에 노출됩니다. 공유 범위를 제한해야 합니다.',
  [('cmt', '# 스냅샷 공유 범위'), ('prompt', '$ aws ec2 describe-snapshot-attribute'), ('bad', 'createVolumePermission: all (퍼블릭)'), ('warn', '→ 디스크 내용 외부 노출')],
  [('cmt', '# 비공개 전환'), ('prompt', '$ aws ec2 modify-snapshot-attribute --remove all'), ('good', 'private 전환'), ('good', '→ 외부 노출 차단')],
  ['스냅샷/AMI의 퍼블릭 공유를 해제하고 필요한 계정에만 공유합니다.', '이미지에 자격증명/키가 포함되지 않도록 점검합니다.'],
  ['스냅샷/이미지가 비공개인가', '이미지에 비밀정보가 없는가'],
  '클라우드 스토리지 > 스냅샷 공개'),

# ===== 네트워크 =====
C('C-08', '보안그룹 전체 개방(0.0.0.0/0)', '🌐', '네트워크', '상',
  '보안그룹/방화벽이 0.0.0.0/0으로 전체 개방되면 인터넷 누구나 접근할 수 있습니다. 출발지를 필요한 대역으로 제한해야 합니다.',
  [('cmt', '# 보안그룹 규칙'), ('prompt', '$ aws ec2 describe-security-groups'), ('bad', '0.0.0.0/0 -> ALL ports'), ('warn', '→ 인터넷 전체 개방')],
  [('cmt', '# 출발지 제한'), ('prompt', '$ aws ec2 authorize-... --cidr 10.0.0.0/24'), ('good', '필요 대역/포트만 허용'), ('good', '→ 노출 최소화')],
  ['0.0.0.0/0 전체 허용 규칙을 제거하고 필요한 출발지/포트만 허용합니다.', '관리 포트는 별도 대역/Bastion으로 제한합니다.'],
  ['전체 개방 규칙이 제거됨', '필요 대역/포트만 허용됨'],
  '클라우드 네트워크 > 보안그룹'),

C('C-09', '관리 포트(SSH/RDP) 인터넷 노출', '🚪', '네트워크', '상',
  'SSH(22)·RDP(3389) 관리 포트가 인터넷에 노출되면 무차별 대입·취약점 공격의 표적이 됩니다. 접근을 제한해야 합니다.',
  [('cmt', '# 관리 포트 노출'), ('prompt', '$ aws ec2 describe-security-groups | grep 22'), ('bad', '0.0.0.0/0 -> 22 (SSH 개방)'), ('warn', '→ 무차별 대입 표적')],
  [('cmt', '# Bastion/대역 제한'), ('prompt', '$ ... --cidr 10.0.0.0/24 --port 22'), ('good', 'Bastion/SSM 경유'), ('good', '→ 관리 포트 보호')],
  ['SSH/RDP를 인터넷에서 직접 열지 말고 Bastion/SSM/VPN을 경유합니다.', '허용 출발지를 관리 대역으로 제한합니다.'],
  ['관리 포트가 인터넷에 직접 노출되지 않음', 'Bastion/VPN 경유로 제한됨'],
  '클라우드 네트워크 > 관리 포트'),

C('C-10', '불필요한 퍼블릭 IP 노출', '📡', '네트워크', '중',
  '내부용 인스턴스에 불필요한 퍼블릭 IP가 붙으면 공격면이 커집니다. 퍼블릭 노출을 최소화해야 합니다.',
  [('cmt', '# 퍼블릭 IP 인스턴스'), ('prompt', '$ aws ec2 describe-instances'), ('bad', 'db-server: PublicIp 3.x.x.x'), ('warn', '→ 내부 자원 외부 노출')],
  [('cmt', '# 프라이빗 전환'), ('prompt', '$ ... 프라이빗 서브넷 + NAT'), ('good', 'PublicIp 없음 (프라이빗)'), ('good', '→ 공격면 축소')],
  ['내부용 인스턴스는 프라이빗 서브넷에 두고 퍼블릭 IP를 제거합니다.', '아웃바운드는 NAT 게이트웨이로 처리합니다.'],
  ['불필요한 퍼블릭 IP가 제거됨'],
  '클라우드 네트워크 > 퍼블릭 IP'),

# ===== 로깅/모니터링 =====
C('C-11', '감사 로그(CloudTrail) 미설정', '🧾', '로깅', '상',
  '클라우드 API 호출 감사 로그가 없으면 침해 행위를 추적·분석할 수 없습니다. 전 리전 감사 로깅을 활성화해야 합니다.',
  [('cmt', '# 감사 로깅 상태'), ('prompt', '$ aws cloudtrail describe-trails'), ('bad', 'trail: none (로깅 없음)'), ('warn', '→ 침해 추적 불가')],
  [('cmt', '# 전 리전 로깅'), ('prompt', '$ aws cloudtrail create-trail --is-multi-region'), ('good', 'multi-region trail + S3 저장'), ('good', '→ 행위 추적 가능')],
  ['전 리전 CloudTrail(또는 동등 감사로그)을 활성화합니다.', '로그를 별도 계정/버킷에 보관하고 SIEM과 연계합니다.'],
  ['전 리전 감사 로깅이 활성화됨', '로그가 안전하게 보관됨'],
  '클라우드 로깅 > 감사 로그'),

C('C-12', '로그 무결성·보관 미흡', '📊', '로깅', '중',
  '로그가 위변조 방지 없이 짧게 보관되면 사고 분석·증빙이 어렵습니다. 무결성 검증과 충분한 보관이 필요합니다.',
  [('cmt', '# 로그 무결성/보관'), ('prompt', '$ aws cloudtrail get-trail-status'), ('bad', 'LogFileValidation: false'), ('warn', '→ 로그 위변조/조기 소실')],
  [('cmt', '# 무결성/보관 강화'), ('prompt', '$ ... --enable-log-file-validation'), ('good', 'validation on + 보관 1년'), ('good', '→ 위변조 탐지·증빙')],
  ['로그 파일 무결성 검증을 활성화합니다.', '버킷 객체 잠금(WORM)·충분한 보관 기간을 설정합니다.'],
  ['로그 무결성 검증이 활성화됨', '로그 보관 기간이 충분함'],
  '클라우드 로깅 > 로그 무결성'),

# ===== 컨테이너/K8s =====
C('C-13', '특권(privileged) 컨테이너', '📦', '컨테이너', '상',
  '컨테이너를 privileged로 실행하면 호스트 커널/장치에 접근해 컨테이너 탈출·호스트 장악이 가능합니다. 특권 실행을 금지해야 합니다.',
  [('cmt', '# 컨테이너 권한'), ('prompt', '$ kubectl get pod -o yaml | grep privileged'), ('bad', 'privileged: true'), ('warn', '→ 컨테이너 탈출로 호스트 장악')],
  [('cmt', '# 특권 제거'), ('prompt', '$ securityContext: privileged: false'), ('good', 'runAsNonRoot + drop ALL'), ('good', '→ 권한 격리')],
  ['<code>privileged: false</code>, <code>allowPrivilegeEscalation: false</code>를 설정합니다.', 'Capabilities를 drop하고 비루트로 실행합니다.', 'Pod Security Standards(restricted)를 적용합니다.'],
  ['특권 컨테이너가 없는가', '비루트·권한 최소화로 실행되는가'],
  '컨테이너 보안 > 특권 컨테이너'),

C('C-14', '컨테이너 이미지 취약점 스캔 미적용', '🔍', '컨테이너', '상',
  '이미지의 알려진 취약점(CVE)을 스캔하지 않으면 취약한 라이브러리가 그대로 배포됩니다. 빌드/배포 단계에서 스캔해야 합니다.',
  [('cmt', '# 이미지 취약점'), ('prompt', '$ trivy image myapp:1.0'), ('bad', 'CRITICAL: 14, HIGH: 37 (미패치)'), ('warn', '→ 취약 라이브러리 배포')],
  [('cmt', '# 스캔 게이트'), ('prompt', '$ trivy image --exit-code 1 --severity CRITICAL'), ('good', '취약점 0 → 배포 허용'), ('good', '→ 취약 이미지 차단')],
  ['CI/CD에 이미지 취약점 스캔(Trivy/Grype 등)을 게이트로 적용합니다.', '베이스 이미지를 최신·경량(distroless)으로 유지합니다.'],
  ['이미지 취약점 스캔이 적용됨', '베이스 이미지가 최신으로 유지됨'],
  '컨테이너 보안 > 이미지 스캔'),

C('C-15', '시크릿 평문 노출(환경변수/이미지)', '🔓', '컨테이너', '상',
  '비밀번호/토큰을 환경변수나 이미지 레이어에 평문으로 두면 이미지 추출·프로세스 조회로 유출됩니다. 시크릿 관리도구를 써야 합니다.',
  [('cmt', '# 시크릿 노출'), ('prompt', '$ docker history myapp:1.0 ; printenv'), ('bad', 'ENV DB_PASSWORD=P@ssw0rd! (평문)'), ('warn', '→ 이미지/프로세스에서 추출')],
  [('cmt', '# 시크릿 관리'), ('prompt', '$ kubectl create secret / Vault'), ('good', 'Secret/Vault 마운트'), ('good', '→ 평문 노출 제거')],
  ['시크릿을 환경변수/이미지에 넣지 말고 K8s Secret(암호화)·Vault로 주입합니다.', '이미지 레이어에 비밀이 남지 않도록 빌드합니다.'],
  ['시크릿이 평문으로 노출되지 않음', '시크릿 관리도구를 사용함'],
  '컨테이너 보안 > 시크릿 관리'),

C('C-16', 'K8s RBAC 과도 권한', '🎚️', '컨테이너', '상',
  '서비스 계정/사용자에 cluster-admin 등 과도한 RBAC 권한을 부여하면 한 파드 침해로 클러스터 전체가 장악됩니다. 최소 권한을 부여해야 합니다.',
  [('cmt', '# RBAC 권한'), ('prompt', '$ kubectl get clusterrolebinding'), ('bad', 'default SA -> cluster-admin'), ('warn', '→ 파드 침해로 클러스터 장악')],
  [('cmt', '# 최소 권한'), ('prompt', '$ Role + RoleBinding (네임스페이스 한정)'), ('good', '필요 권한만 부여'), ('good', '→ 권한 격리')],
  ['cluster-admin 등 과도 권한을 회수하고 네임스페이스 한정 Role을 부여합니다.', '기본 서비스계정에 권한을 자동 부여하지 않습니다.'],
  ['과도한 RBAC 권한이 회수됨', '최소 권한 Role이 적용됨'],
  '컨테이너 보안 > K8s RBAC'),

C('C-17', 'K8s API 서버 익명 접근', '🚷', '컨테이너', '상',
  'K8s API 서버가 익명 접근을 허용하거나 인터넷에 노출되면 비인가자가 클러스터를 조작할 수 있습니다. 익명 접근을 차단하고 접근을 제한해야 합니다.',
  [('cmt', '# 익명 접근 테스트'), ('prompt', '$ curl -k https://api:6443/api/v1/pods'), ('bad', '200 OK (익명 조회 성공)'), ('warn', '→ 비인가 클러스터 접근')],
  [('cmt', '# 익명 차단'), ('prompt', '$ --anonymous-auth=false + RBAC'), ('good', '401 Unauthorized'), ('good', '→ 인증 강제')],
  ['<code>--anonymous-auth=false</code>로 익명 접근을 차단합니다.', 'API 서버를 인터넷에 노출하지 않고 접근 IP를 제한합니다.'],
  ['API 서버 익명 접근이 차단됨', 'API 서버 접근이 제한됨'],
  '컨테이너 보안 > K8s API 접근'),

C('C-18', '호스트 경로·네임스페이스 공유', '🔗', '컨테이너', '상',
  'hostPath 마운트나 hostPID/hostNetwork 공유는 컨테이너가 호스트 자원에 접근하게 해 탈출·정보 노출을 유발합니다. 공유를 제한해야 합니다.',
  [('cmt', '# 호스트 공유 설정'), ('prompt', '$ kubectl get pod -o yaml | grep -E "hostPath|hostPID"'), ('bad', 'hostPath: / , hostPID: true'), ('warn', '→ 호스트 파일/프로세스 접근')],
  [('cmt', '# 공유 제거'), ('prompt', '$ hostPath 제거, hostPID: false'), ('good', '호스트 격리'), ('good', '→ 탈출 경로 차단')],
  ['불필요한 <code>hostPath</code>, <code>hostPID</code>, <code>hostNetwork</code> 공유를 제거합니다.', 'Pod Security Standards로 호스트 네임스페이스 사용을 금지합니다.'],
  ['호스트 경로/네임스페이스 공유가 제한됨'],
  '컨테이너 보안 > 호스트 격리'),

C('C-19', '검증 안된 이미지·latest 태그', '🏷️', '컨테이너', '중',
  'latest 태그나 서명 검증 없는 이미지를 사용하면 변조·예측 불가 버전이 배포됩니다. 고정 다이제스트·이미지 서명을 사용해야 합니다.',
  [('cmt', '# 이미지 태그'), ('prompt', '$ kubectl get pod -o yaml | grep image:'), ('bad', 'image: myapp:latest (미고정)'), ('warn', '→ 변조/예측불가 버전 배포')],
  [('cmt', '# 다이제스트/서명'), ('prompt', '$ image: myapp@sha256:... ; cosign verify'), ('good', '고정 digest + 서명 검증'), ('good', '→ 무결성 보장')],
  ['이미지를 <code>@sha256</code> 다이제스트로 고정하고 서명(cosign)을 검증합니다.', '신뢰된 레지스트리만 허용(admission policy)합니다.'],
  ['이미지가 고정 다이제스트로 배포됨', '이미지 서명이 검증됨'],
  '컨테이너 보안 > 이미지 무결성'),

C('C-20', '리소스 제한 미설정', '📈', '컨테이너', '중',
  '컨테이너에 CPU/메모리 제한이 없으면 하나의 파드가 노드 자원을 고갈시켜 서비스 거부(DoS)를 유발합니다. 리소스 제한을 설정해야 합니다.',
  [('cmt', '# 리소스 제한'), ('prompt', '$ kubectl get pod -o yaml | grep -A2 resources'), ('bad', 'resources: {} (제한 없음)'), ('warn', '→ 자원 고갈 DoS 위험')],
  [('cmt', '# limits/requests'), ('prompt', '$ resources.limits cpu/memory 설정'), ('good', 'limits + requests 지정'), ('good', '→ 자원 격리')],
  ['컨테이너에 <code>resources.limits</code>/<code>requests</code>를 설정합니다.', '네임스페이스에 LimitRange/ResourceQuota를 적용합니다.'],
  ['컨테이너 리소스 제한이 설정됨'],
  '컨테이너 보안 > 리소스 제한'),
]
