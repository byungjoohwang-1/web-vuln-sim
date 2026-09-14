# -*- coding: utf-8 -*-
"""금융권 클라우드 관리체계 평가기준(PISM) — AWS 진단 실습 명세 1차 (위험도 5 항목).

출력 JSON 은 실제 AWS CLI 응답 형식을 따른다. 계정 382011749265 / ap-northeast-2 로 통일하고
리소스 ID 도 실제 형식(i-, vol-, snap-, sg-, ami- + 17자리 hex)을 지킨다.
학습자가 현업에서 같은 화면을 만나야 이 실습이 의미가 있다.
"""

SPECS = [

# ── PISM-001 통신구간 암호화 ─────────────────────────────────────────────
{
 'file': '07_fincloud-pism001.html', 'pism': 'PISM-001', 'risk': '5',
 'title': '통신구간 암호화 적용 여부', 'svc': 'S3',
 'area': '5. 운영 관리', 'ctrl': '5.3 정보처리시스템 보호대책',
 'detail': 'HTTP 요청을 허용할 경우 중요정보가 평문으로 노출될 위협이 존재하므로, HTTP 요청 거부 설정을 활성화하여 통신구간 암호화 적용 여부를 점검합니다.',
 'console_path': '<b>S3</b> 진입 → <b>버킷</b> 클릭 → 목록에서 대상 버킷 선택 → <b>권한</b> 클릭 → <b>버킷 정책</b>에서 <code>aws:SecureTransport</code> 조건으로 HTTP 를 거부하는 Deny 문이 있는지 확인',
 'cmds': [
   {'label': '① 버킷 목록 확인', 'cmd': 'aws s3 ls',
    'out': '''2025-11-02 09:14:37 fin-core-txn-archive
2026-01-19 16:40:02 fin-mydata-consent-logs
2026-03-08 11:27:55 fin-cloudtrail-audit'''},
   {'label': '② 버킷 정책에서 암호화 통신 강제 여부 확인', 'cmd': 'aws s3api get-bucket-policy --bucket fin-core-txn-archive --output text --query Policy',
    'out': '''{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowAppRead",
            "Effect": "Allow",
            "Principal": {"AWS": "arn:aws:iam::382011749265:role/fin-core-app"},
            "Action": ["s3:GetObject", "s3:PutObject"],
            "Resource": "arn:aws:s3:::fin-core-txn-archive/*"
        }
    ]
}

<span class="er">※ aws:SecureTransport 조건의 Deny 문이 없습니다.</span>'''},
   {'label': '③ 평가기준 명시 방법 — grep 으로 확인', 'cmd': 'aws s3api get-bucket-policy --bucket fin-core-txn-archive | grep aws:SecureTransport',
    'out': '<span class="dim">(출력 없음 — 일치하는 항목이 없습니다. 종료 코드 1)</span>'},
 ],
 'answer': 'bad',
 'why': '''버킷 정책에 <b>aws:SecureTransport = false 를 Deny 하는 문장이 없습니다.</b> 이 상태에서는 <code>http://</code> 로도 객체를 읽고 쓸 수 있어 전송 구간이 평문입니다.
<div class="ev">흔한 오해: "S3 는 기본이 HTTPS 아닌가?"
→ 아닙니다. S3 엔드포인트는 HTTP 도 함께 받습니다. 기본값이 HTTPS 인 것은 <b>SDK·콘솔의 클라이언트 동작</b>일 뿐,
   서버가 HTTP 를 거부하는 것은 아닙니다. 거부는 <b>버킷 정책으로 명시</b>해야 성립합니다.</div>''',
 'fix_intro': '버킷 정책에 <b>SecureTransport 가 false 이면 모든 S3 작업을 Deny</b> 하는 문장을 추가합니다. Allow 문을 고치는 것이 아니라 Deny 문을 <b>덧붙이는</b> 것이 핵심입니다 — 명시적 Deny 는 어떤 Allow 보다 우선합니다.',
 'fix_cmd': '''$ cat > deny-insecure.json <<'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowAppRead",
            "Effect": "Allow",
            "Principal": {"AWS": "arn:aws:iam::382011749265:role/fin-core-app"},
            "Action": ["s3:GetObject", "s3:PutObject"],
            "Resource": "arn:aws:s3:::fin-core-txn-archive/*"
        },
        {
            "Sid": "DenyInsecureTransport",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::fin-core-txn-archive",
                "arn:aws:s3:::fin-core-txn-archive/*"
            ],
            "Condition": {"Bool": {"aws:SecureTransport": "false"}}
        }
    ]
}
EOF

$ aws s3api put-bucket-policy --bucket fin-core-txn-archive \\
      --policy file://deny-insecure.json''',
 'fix_out': '''$ aws s3api get-bucket-policy --bucket fin-core-txn-archive | grep aws:SecureTransport
            "Condition": {"Bool": {"aws:SecureTransport": "false"}}

$ curl http://fin-core-txn-archive.s3.ap-northeast-2.amazonaws.com/ledger/2026-03.csv
<Error><Code>AccessDenied</Code><Message>Access Denied</Message></Error>

→ HTTP 요청이 거부됩니다. 조치 완료.''',
 'iac': '''# Terraform — 버킷을 새로 만들 때마다 같은 Deny 가 붙도록 모듈에 넣는다
data "aws_iam_policy_document" "deny_insecure" {
  statement {
    sid     = "DenyInsecureTransport"
    effect  = "Deny"
    actions = ["s3:*"]
    resources = [
      aws_s3_bucket.txn_archive.arn,
      "${aws_s3_bucket.txn_archive.arn}/*",
    ]
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}

resource "aws_s3_bucket_policy" "txn_archive" {
  bucket = aws_s3_bucket.txn_archive.id
  policy = data.aws_iam_policy_document.deny_insecure.json
}''',
 'pitfall': '<b>주의</b> — Deny 문의 <code>Resource</code> 에 버킷 ARN 과 <code>/*</code> 을 <b>둘 다</b> 넣어야 합니다. <code>/*</code> 만 넣으면 객체 작업은 막히지만 <code>ListBucket</code> 같은 버킷 수준 작업은 여전히 HTTP 로 가능합니다. 또한 <code>Principal: "*"</code> 이므로 <b>VPC 엔드포인트 경유 내부 트래픽도 HTTPS 여야</b> 합니다 — 사내 배치 스크립트가 HTTP 를 쓰고 있지 않은지 먼저 확인하고 적용하세요.',
 'evidence': [
   '대상 버킷 목록 (<code>aws s3 ls</code> 출력)',
   '버킷별 정책 전문 (<code>get-bucket-policy</code> 출력) — <code>aws:SecureTransport</code> 조건 포함 여부',
   '조치 후 HTTP 요청이 AccessDenied 로 거부되는 것을 보인 <code>curl</code> 결과',
 ],
 'finance': '전자금융감독규정은 이용자 정보와 거래정보를 <b>송·수신 구간에서 암호화</b>하도록 요구합니다. 클라우드에서는 이 요구가 "TLS 를 지원한다"가 아니라 <b>"평문 접근을 거부한다"</b>로 구현되어야 합니다. 거래원장·마이데이터 동의 로그처럼 보존 의무가 있는 객체가 담긴 버킷은 우선순위로 처리하세요.',
},

# ── PISM-005 퍼블릭 액세스 ───────────────────────────────────────────────
{
 'file': '07_fincloud-pism005.html', 'pism': 'PISM-005', 'risk': '5',
 'title': '가상자원에 대한 퍼블릭 액세스 허용', 'svc': 'S3 · EC2 · RDS',
 'area': '5. 운영 관리', 'ctrl': '5.3 정보처리시스템 보호대책',
 'detail': '가상자원에 대한 퍼블릭 액세스를 차단하지 않을 경우 중요정보 노출 등의 위협이 존재하므로 가상자원의 퍼블릭 액세스 차단 설정 활성화 여부를 점검합니다.',
 'console_path': '<b>S3</b> → 버킷 → <b>권한</b> → <b>퍼블릭 액세스 차단</b> 4개 항목 확인 &nbsp;/&nbsp; <b>EC2</b> → 인스턴스 → <b>퍼블릭 IPv4 주소</b> 유무 &nbsp;/&nbsp; <b>Aurora and RDS</b> → 데이터베이스 → <b>연결 및 보안</b> → <b>퍼블릭 액세스 가능</b> 확인',
 'cmds': [
   {'label': '① S3 퍼블릭 액세스 차단 설정 확인', 'cmd': 'aws s3api get-public-access-block --bucket fin-mydata-consent-logs',
    'out': '''{
    "PublicAccessBlockConfiguration": {
        "BlockPublicAcls": true,
        "IgnorePublicAcls": true,
        "BlockPublicPolicy": <span class="er">false</span>,
        "RestrictPublicBuckets": <span class="er">false</span>
    }
}

<span class="dim">4개 중 2개만 활성. 버킷 정책으로 퍼블릭을 열 수 있는 상태입니다.</span>'''},
   {'label': '② EC2 퍼블릭 IP 보유 인스턴스 확인', 'cmd': 'aws ec2 describe-instances --query "Reservations[*].Instances[*].{InstanceId:InstanceId, PublicIp:PublicIpAddress}" --output table',
    'out': '''---------------------------------------------
|             DescribeInstances             |
+----------------------+--------------------+
|      InstanceId      |     PublicIp       |
+----------------------+--------------------+
|  i-0a3f72be91c4d5e80 |  None              |
|  i-0c81d5fa27e93b146 |  <span class="er">3.35.128.77</span>       |
|  i-04e7b9c3d85a1f602 |  None              |
+----------------------+--------------------+

<span class="dim">i-0c81d5fa27e93b146 = fin-batch-worker (배치 서버)</span>'''},
   {'label': '③ RDS 퍼블릭 액세스 설정 확인', 'cmd': 'aws rds describe-db-instances --db-instance-identifier fin-core-db --query "DBInstances[*].PubliclyAccessible"',
    'out': '''[
    <span class="er">true</span>
]'''},
 ],
 'answer': 'bad',
 'why': '''세 자원 모두에서 퍼블릭 노출 요소가 확인됩니다.
<div class="ev">S3  : BlockPublicPolicy / RestrictPublicBuckets 가 false → 버킷 정책 한 줄로 전체 공개가 가능
EC2 : fin-batch-worker 가 퍼블릭 IP 보유 → 배치 서버는 인터넷 인바운드가 필요 없음
RDS : PubliclyAccessible = true → DB 엔드포인트가 인터넷에서 이름 해석됨</div>
특히 RDS 의 <code>PubliclyAccessible=true</code> 는 "보안그룹으로 막고 있으니 괜찮다"고 넘어가기 쉽지만, <b>보안그룹 오설정 한 번이 곧바로 인터넷 노출</b>이 되므로 방어선이 하나뿐인 상태입니다.''',
 'fix_intro': '세 자원을 각각 닫습니다. 순서가 중요합니다 — <b>RDS 는 퍼블릭 해제 시 재시작 없이 적용</b>되지만 엔드포인트 IP 가 바뀌므로, 앱의 연결 풀을 먼저 확인하세요.',
 'fix_cmd': '''# 1) S3 — 퍼블릭 액세스 차단 4개 모두 활성화
$ aws s3api put-public-access-block --bucket fin-mydata-consent-logs \\
      --public-access-block-configuration \\
      "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# 2) EC2 — 퍼블릭 IP 회수 (배치 서버는 NAT 게이트웨이 경유로 전환)
$ aws ec2 describe-addresses --filters "Name=instance-id,Values=i-0c81d5fa27e93b146"
$ aws ec2 disassociate-address --association-id eipassoc-0b17f9c26d43a8e51
$ aws ec2 release-address --allocation-id eipalloc-0f92c7ab35de16704

# 3) RDS — 퍼블릭 액세스 해제
$ aws rds modify-db-instance --db-instance-identifier fin-core-db \\
      --no-publicly-accessible --apply-immediately''',
 'fix_out': '''$ aws s3api get-public-access-block --bucket fin-mydata-consent-logs
{
    "PublicAccessBlockConfiguration": {
        "BlockPublicAcls": true,
        "IgnorePublicAcls": true,
        "BlockPublicPolicy": true,
        "RestrictPublicBuckets": true
    }
}

$ aws rds describe-db-instances --db-instance-identifier fin-core-db --query "DBInstances[*].PubliclyAccessible"
[
    false
]

→ 세 자원 모두 퍼블릭 경로가 제거되었습니다.''',
 'iac': '''# 계정 단위로 한 번에 잠그는 것이 가장 확실하다 (신규 버킷까지 자동 적용)
resource "aws_s3_account_public_access_block" "this" {
  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}

resource "aws_db_instance" "fin_core" {
  identifier          = "fin-core-db"
  publicly_accessible = false          # 기본값이지만 명시해 둔다
  db_subnet_group_name = aws_db_subnet_group.private.name
}

# SCP 로 조직 전체에서 퍼블릭 해제를 금지 (되돌림 방지)
# Effect: Deny / Action: s3:PutBucketPublicAccessBlock / Condition: 값이 false 인 경우''',
 'pitfall': '<b>주의</b> — S3 퍼블릭 차단은 <b>계정 수준</b>과 <b>버킷 수준</b>이 따로 있습니다. 버킷만 잠그면 다음에 만들어지는 버킷은 다시 열린 채로 시작합니다. 계정 수준(<code>put-public-access-block</code> on account)으로 거는 것이 정석입니다. EC2 퍼블릭 IP 는 <b>Elastic IP 와 auto-assign 이 별개</b>라, EIP 를 회수해도 서브넷의 <code>MapPublicIpOnLaunch=true</code> 가 남아 있으면 다음 인스턴스가 또 퍼블릭 IP 를 받습니다.',
 'evidence': [
   '버킷별 <code>get-public-access-block</code> 출력 (4개 항목 모두 true 인지)',
   '퍼블릭 IP 보유 인스턴스 목록 및 업무상 필요성 소명',
   'RDS 인스턴스별 <code>PubliclyAccessible</code> 값',
   '조치 후 재확인 출력 및 서브넷 <code>MapPublicIpOnLaunch</code> 설정',
 ],
 'finance': '금융회사는 <b>중요 정보처리시스템을 인터넷과 분리</b>하도록 요구받습니다. 클라우드에서 이 요구는 물리적 망분리가 아니라 <b>퍼블릭 경로의 부재</b>로 증명됩니다. "보안그룹으로 막았다"는 단일 방어선이며, 평가에서는 <b>자원 자체가 퍼블릭이 아닐 것</b>을 먼저 봅니다.',
},

# ── PISM-007 보안그룹 최소권한 ───────────────────────────────────────────
{
 'file': '07_fincloud-pism007.html', 'pism': 'PISM-007', 'risk': '5',
 'title': '네트워크 접근 제어 설정의 최소 권한 적용', 'svc': 'Security Group',
 'area': '5. 운영 관리', 'ctrl': '5.9 IP주소 관리', 'evaltype': '관리체계, 스크립트',
 'detail': '기본 네트워크 보안 설정(방화벽, 보안그룹 등)이 최소 권한 원칙을 준수하도록 구성되어 있는지, 과도한 접근 권한이 허용되지 않도록 점검합니다.',
 'console_path': '<b>EC2</b> → <b>보안 그룹</b> → 목록에서 대상 보안 그룹 ID 클릭 → <b>인바운드 규칙</b> 확인 → <b>아웃바운드 규칙</b> 확인',
 'cmds': [
   {'label': '① 전체 보안그룹 규칙 확인 (평가기준 명시 명령)', 'cmd': 'aws ec2 describe-security-groups --query \'SecurityGroups[*].{GroupId:GroupId, GroupName:GroupName, Ingress:IpPermissions[*].[FromPort,ToPort,IpProtocol,IpRanges[*].CidrIp]}\' --output json',
    'out': '''[
    {
        "GroupId": "sg-0d41e7b92c85f3a06",
        "GroupName": "fin-web-alb-sg",
        "Ingress": [
            [443, 443, "tcp", ["0.0.0.0/0"]]
        ]
    },
    {
        "GroupId": "sg-07c9a3f18be62d540",
        "GroupName": "fin-core-app-sg",
        "Ingress": [
            [8080, 8080, "tcp", ["10.40.0.0/16"]],
            <span class="er">[22, 22, "tcp", ["0.0.0.0/0"]]</span>
        ]
    },
    {
        "GroupId": "sg-0b58d27e94a1c6f38",
        "GroupName": "fin-core-db-sg",
        "Ingress": [
            <span class="er">[0, 65535, "tcp", ["0.0.0.0/0"]]</span>
        ]
    }
]'''},
   {'label': '② 0.0.0.0/0 이 열린 규칙만 추려 보기', 'cmd': 'aws ec2 describe-security-groups --filters Name=ip-permission.cidr,Values=0.0.0.0/0 --query "SecurityGroups[*].[GroupId,GroupName]" --output table',
    'out': '''-------------------------------------------------
|            DescribeSecurityGroups             |
+-----------------------+-----------------------+
|  sg-0d41e7b92c85f3a06 |  fin-web-alb-sg       |
|  sg-07c9a3f18be62d540 |  fin-core-app-sg      |
|  sg-0b58d27e94a1c6f38 |  fin-core-db-sg       |
+-----------------------+-----------------------+'''},
   {'label': '③ DB 보안그룹을 참조하는 자원 확인', 'cmd': 'aws ec2 describe-network-interfaces --filters Name=group-id,Values=sg-0b58d27e94a1c6f38 --query "NetworkInterfaces[*].[Description,PrivateIpAddress]" --output table',
    'out': '''------------------------------------------------------------
|                DescribeNetworkInterfaces                 |
+------------------------------------+---------------------+
|  RDSNetworkInterface fin-core-db   |  10.40.12.211       |
+------------------------------------+---------------------+

<span class="er">※ 코어뱅킹 DB 가 전 포트 0.0.0.0/0 으로 열려 있습니다.</span>'''},
 ],
 'answer': 'bad',
 'why': '''세 보안그룹 중 <b>두 곳이 최소 권한을 위반</b>합니다.
<div class="ev">sg-0d41e7b92c85f3a06 (ALB)  : 443 ← 0.0.0.0/0  → 공개 웹 진입점이므로 <b>정상</b>
sg-07c9a3f18be62d540 (APP)  : 22  ← 0.0.0.0/0  → SSH 를 인터넷 전체에 개방 <b>위반</b>
sg-0b58d27e94a1c6f38 (DB)   : 0-65535 ← 0.0.0.0/0 → 전 포트 개방 <b>중대 위반</b></div>
판정에서 자주 틀리는 지점: <b>0.0.0.0/0 이 곧 위반은 아닙니다.</b> 인터넷에 서비스하는 ALB 의 443 은 정당합니다. 위반은 <b>업무상 필요 범위를 넘어선 개방</b>이며, 관리 포트(22/3389)와 데이터 계층이 그 대상입니다.''',
 'fix_intro': '관리 포트는 <b>회수</b>하고, DB 는 <b>보안그룹 참조(source security group)</b> 로 바꿉니다. CIDR 대신 SG 를 소스로 쓰면 IP 가 바뀌어도 규칙을 다시 손댈 필요가 없습니다.',
 'fix_cmd': '''# 1) APP 의 전체 개방 SSH 회수 → 세션 관리자(SSM)로 접속 전환
$ aws ec2 revoke-security-group-ingress --group-id sg-07c9a3f18be62d540 \\
      --protocol tcp --port 22 --cidr 0.0.0.0/0

# 2) DB 의 전 포트 개방 회수
$ aws ec2 revoke-security-group-ingress --group-id sg-0b58d27e94a1c6f38 \\
      --protocol tcp --port 0-65535 --cidr 0.0.0.0/0

# 3) DB 는 APP 보안그룹에서 오는 5432 만 허용 (CIDR 아님, SG 참조)
$ aws ec2 authorize-security-group-ingress --group-id sg-0b58d27e94a1c6f38 \\
      --protocol tcp --port 5432 --source-group sg-07c9a3f18be62d540''',
 'fix_out': '''$ aws ec2 describe-security-groups --group-ids sg-0b58d27e94a1c6f38 \\
      --query "SecurityGroups[*].IpPermissions"
[
    [
        {
            "FromPort": 5432,
            "ToPort": 5432,
            "IpProtocol": "tcp",
            "IpRanges": [],
            "UserIdGroupPairs": [
                {"GroupId": "sg-07c9a3f18be62d540", "UserId": "382011749265"}
            ]
        }
    ]
]

$ aws ec2 describe-security-groups --filters Name=ip-permission.cidr,Values=0.0.0.0/0 \\
      --query "SecurityGroups[*].GroupName" --output text
fin-web-alb-sg

→ 남은 0.0.0.0/0 은 ALB 443 뿐입니다. 조치 완료.''',
 'iac': '''resource "aws_security_group_rule" "db_from_app_only" {
  security_group_id        = aws_security_group.db.id
  type                     = "ingress"
  protocol                 = "tcp"
  from_port                = 5432
  to_port                  = 5432
  source_security_group_id = aws_security_group.app.id   # CIDR 대신 SG 참조
}

# 관리 접속은 SG 를 열지 않고 SSM Session Manager 로 — 인바운드 0개 유지
resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.app_instance.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}''',
 'pitfall': '<b>주의</b> — <code>revoke-security-group-ingress</code> 는 규칙이 <b>정확히 일치</b>해야 지워집니다. 포트 범위나 프로토콜이 한 글자라도 다르면 "규칙 없음"으로 조용히 넘어가고 개방이 그대로 남습니다. 지운 뒤 반드시 <code>describe</code> 로 재확인하세요. 또한 <b>아웃바운드 기본값이 전체 허용(0.0.0.0/0)</b>이라는 점도 평가 대상입니다 — 데이터 유출 경로가 되므로 금융권에서는 아웃바운드도 좁히도록 요구받는 경우가 많습니다.',
 'evidence': [
   '전체 보안그룹의 인바운드·아웃바운드 규칙 목록',
   '<code>0.0.0.0/0</code> 개방 규칙별 업무상 필요성 소명 자료',
   '관리 포트(22/3389) 접근 경로 (SSM·踏み台 등) 설명',
   '조치 후 규칙 재확인 출력',
 ],
 'finance': '전자금융감독규정의 <b>내부통신망 분리</b>·<b>접근통제</b> 요구는 클라우드에서 보안그룹으로 구현됩니다. 특히 <b>코어뱅킹 DB 계층</b>은 인터넷 경로가 존재하는 것만으로 중대한 지적 사항이며, 사고 시 "보안그룹 설정 오류"는 가장 흔한 직접 원인입니다.',
},

# ── PISM-013 접근 로그 (CloudTrail) ──────────────────────────────────────
{
 'file': '07_fincloud-pism013.html', 'pism': 'PISM-013', 'risk': '5',
 'title': '접근 로그 수집 기능 활성화 여부', 'svc': 'CloudTrail',
 'area': '5. 운영 관리', 'ctrl': '5.3 정보처리시스템 보호대책', 'evaltype': '관리체계, 스크립트',
 'detail': '시스템 또는 네트워크 경계에서 수집되는 접근 로그 기능이 활성화되어 있으며, 사용자 요청 이력 및 행동 추적이 가능한지 여부를 점검합니다.',
 'console_path': '<b>CloudTrail</b> → <b>추적</b> → 대상 트레일 선택 → <b>일반 세부 정보</b>에서 <b>추적 로깅</b> · <b>다중 리전 추적</b> · <b>로그 파일 검증</b> 설정 확인',
 'cmds': [
   {'label': '① 트레일 설정 확인 (다중 리전·로그 검증)', 'cmd': 'aws cloudtrail describe-trails --query \'trailList[*].{Name:Name, IsMultiRegionTrail:IsMultiRegionTrail, LogFileValidationEnabled:LogFileValidationEnabled}\' --output table',
    'out': '''------------------------------------------------------------------------
|                            DescribeTrails                            |
+-------------------+----------------------+---------------------------+
|       Name        | IsMultiRegionTrail   | LogFileValidationEnabled  |
+-------------------+----------------------+---------------------------+
|  fin-audit-trail  |  <span class="er">False</span>               |  <span class="er">False</span>                    |
+-------------------+----------------------+---------------------------+'''},
   {'label': '② 로깅이 실제로 켜져 있는지 확인', 'cmd': 'aws cloudtrail get-trail-status --name fin-audit-trail',
    'out': '''{
    "IsLogging": true,
    "LatestDeliveryTime": "2026-09-14T02:11:38.000000+09:00",
    "StartLoggingTime": "2026-03-08T11:44:02.000000+09:00",
    "TimeLoggingStarted": "2026-03-08T11:44:02Z"
}'''},
   {'label': '③ 데이터 이벤트(S3 객체 접근) 수집 여부 확인', 'cmd': 'aws cloudtrail get-event-selectors --trail-name fin-audit-trail --query "AdvancedEventSelectors[].FieldSelectors" --output json',
    'out': '''[
    [
        {
            "Field": "eventCategory",
            "Equals": ["Management"]
        }
    ]
]

<span class="er">※ Data 이벤트 선택기가 없습니다 — S3 객체 읽기/쓰기와 Lambda 호출은 기록되지 않습니다.</span>'''},
 ],
 'answer': 'bad',
 'why': '''로깅은 켜져 있지만(<code>IsLogging: true</code>) <b>세 가지가 빠져 있습니다.</b>
<div class="ev">IsMultiRegionTrail       : False → 서울 리전 외의 활동이 기록되지 않음
                                  (공격자가 us-east-1 에서 자원을 만들면 흔적이 없음)
LogFileValidationEnabled : False → 로그 파일 위·변조를 검출할 수단이 없음
Data 이벤트              : 미설정 → <b>개인정보가 든 S3 객체를 누가 읽어 갔는지 알 수 없음</b></div>
"CloudTrail 을 켰다"로 양호 판정을 내리기 쉬운 항목입니다. 평가기준이 묻는 것은 <b>행동 추적이 가능한가</b>이며, 관리 이벤트만으로는 유출 경로를 재구성할 수 없습니다.''',
 'fix_intro': '기존 트레일을 <b>다중 리전 + 로그 파일 검증</b>으로 갱신하고, 개인정보·거래정보가 담긴 버킷에 대해 <b>데이터 이벤트</b>를 추가합니다. 데이터 이벤트는 과금되므로 전체가 아니라 <b>중요 버킷만</b> 지정하는 것이 실무입니다.',
 'fix_cmd': '''# 1) 다중 리전 + 로그 파일 검증 활성화
$ aws cloudtrail update-trail --name fin-audit-trail \\
      --is-multi-region-trail \\
      --enable-log-file-validation

# 2) 중요 버킷에 대한 데이터 이벤트 추가 (관리 이벤트는 유지)
$ aws cloudtrail put-event-selectors --trail-name fin-audit-trail \\
      --advanced-event-selectors '[
        {"Name":"Management","FieldSelectors":[
            {"Field":"eventCategory","Equals":["Management"]}]},
        {"Name":"S3-PII-Objects","FieldSelectors":[
            {"Field":"eventCategory","Equals":["Data"]},
            {"Field":"resources.type","Equals":["AWS::S3::Object"]},
            {"Field":"resources.ARN","StartsWith":[
                "arn:aws:s3:::fin-mydata-consent-logs/"]}]}
      ]'

# 3) 로그 버킷에 객체 잠금(무결성) — PISM-012 와 연계
$ aws s3api put-object-lock-configuration --bucket fin-cloudtrail-audit \\
      --object-lock-configuration '{"ObjectLockEnabled":"Enabled",
          "Rule":{"DefaultRetention":{"Mode":"COMPLIANCE","Years":5}}}\'''',
 'fix_out': '''$ aws cloudtrail describe-trails --query 'trailList[*].{Name:Name, IsMultiRegionTrail:IsMultiRegionTrail, LogFileValidationEnabled:LogFileValidationEnabled}' --output table
------------------------------------------------------------------------
|       Name        | IsMultiRegionTrail   | LogFileValidationEnabled  |
+-------------------+----------------------+---------------------------+
|  fin-audit-trail  |  True                |  True                     |
+-------------------+----------------------+---------------------------+

$ aws cloudtrail validate-logs --trail-arn arn:aws:cloudtrail:ap-northeast-2:382011749265:trail/fin-audit-trail \\
      --start-time 2026-09-01T00:00:00Z
Validating log files for trail ...
Results requested for 2026-09-01T00:00:00Z to 2026-09-14T02:20:00Z
Results found for 2026-09-01T00:00:00Z to 2026-09-14T02:20:00Z:
  312/312 digest files valid
  8,417/8,417 log files valid

→ 다중 리전·무결성 검증·데이터 이벤트가 모두 활성화되었습니다.''',
 'iac': '''resource "aws_cloudtrail" "fin_audit" {
  name                          = "fin-audit-trail"
  s3_bucket_name                = aws_s3_bucket.audit.id
  is_multi_region_trail         = true      # 전 리전
  enable_log_file_validation    = true      # 다이제스트 파일 생성
  include_global_service_events = true      # IAM/STS 등 글로벌 서비스

  advanced_event_selector {
    name = "S3-PII-Objects"
    field_selector { field = "eventCategory" equals = ["Data"] }
    field_selector { field = "resources.type" equals = ["AWS::S3::Object"] }
    field_selector {
      field       = "resources.ARN"
      starts_with = ["${aws_s3_bucket.consent_logs.arn}/"]
    }
  }
}''',
 'pitfall': '<b>주의</b> — <code>put-event-selectors</code> 는 기존 선택기를 <b>덮어씁니다</b>. 데이터 이벤트만 넣으면 <b>관리 이벤트 수집이 사라집니다</b>. 위 명령처럼 관리 이벤트 선택기를 반드시 함께 넣으세요. 그리고 <b>로그를 담는 버킷 자체가 감시 대상</b>이라는 점도 잊기 쉽습니다 — 공격자가 가장 먼저 지우려는 것이 그 버킷이므로 객체 잠금(COMPLIANCE 모드)과 별도 계정 보관을 권장합니다.',
 'evidence': [
   '<code>describe-trails</code> 출력 (다중 리전·로그 파일 검증 설정)',
   '<code>get-trail-status</code> 출력 (IsLogging, 최근 전송 시각)',
   '<code>get-event-selectors</code> 출력 (관리·데이터 이벤트 범위)',
   '<code>validate-logs</code> 결과 (로그 무결성 검증 성공 건수)',
   '로그 보관 버킷의 객체 잠금·보존 기간 설정',
]
 ,
 'finance': '전자금융감독규정은 <b>접속기록을 1년 이상</b> 보존하도록 하고, 개인정보 보호법상 안전성 확보조치 기준은 <b>2년 이상</b>(고유식별정보·5만명 이상 등)을 요구합니다. 클라우드에서는 CloudTrail 이 그 접속기록의 원천이므로, 데이터 이벤트가 빠져 있으면 <b>"누가 개인정보 파일을 내려받았는가"</b>에 답할 수 없습니다 — 유출 사고 조사에서 가장 먼저 막히는 지점입니다.',
},

# ── PISM-017 S3 버전 관리 ────────────────────────────────────────────────
{
 'file': '07_fincloud-pism017.html', 'pism': 'PISM-017', 'risk': '5',
 'title': '삭제된 저장소 내 데이터 복원 기능 활성화 여부', 'svc': 'S3',
 'area': '5. 운영 관리', 'ctrl': '5.3 정보처리시스템 보호대책',
 'detail': '중요 정보가 저장된 저장소가 의도치 않게 삭제된 경우 데이터를 복원할 수 있도록 복원 기능의 활성화 여부를 점검합니다.',
 'console_path': '<b>S3</b> → <b>버킷</b> → 목록에서 대상 버킷 선택 → <b>속성</b> 클릭 → <b>버킷 버전 관리</b> 설정 확인',
 'cmds': [
   {'label': '① 버킷 버전 관리 설정 확인', 'cmd': 'aws s3api get-bucket-versioning --bucket fin-core-txn-archive',
    'out': '<span class="dim">{}</span>\n\n<span class="er">※ 빈 응답입니다. 버전 관리를 한 번도 켠 적이 없으면 Status 키 자체가 없습니다.</span>'},
   {'label': '② 다른 버킷과 비교', 'cmd': 'aws s3api get-bucket-versioning --bucket fin-cloudtrail-audit',
    'out': '''{
    "Status": "Enabled",
    "MFADelete": "Disabled"
}'''},
   {'label': '③ 삭제 상황 재현 — 객체를 지우면?', 'cmd': 'aws s3api delete-object --bucket fin-core-txn-archive --key ledger/2026-03.csv',
    'out': '''<span class="dim">(응답 본문 없음 — 204 No Content)</span>

$ aws s3api list-object-versions --bucket fin-core-txn-archive --prefix ledger/2026-03.csv
<span class="dim">{}</span>

<span class="er">※ 버전도 삭제 마커도 없습니다. 객체가 영구 소실되었습니다.</span>'''},
 ],
 'answer': 'bad',
 'why': '''<code>get-bucket-versioning</code> 응답이 <b>비어 있습니다</b>. 버전 관리가 꺼진 상태이며, 이 버킷에서 <code>delete-object</code> 는 <b>즉시 영구 삭제</b>입니다.
<div class="ev">버전 관리 상태 3가지
  (없음)      : 한 번도 켠 적 없음 — 삭제 = 영구 소실
  Enabled     : 삭제 시 <b>삭제 마커</b>만 붙고 이전 버전은 남음 → 복원 가능
  Suspended   : 켰다가 끈 상태 — 기존 버전은 남지만 신규 삭제는 복원 불가</div>
<b>Suspended 를 양호로 판정하지 마세요.</b> 과거 버전이 조회되니 켜져 있는 것처럼 보이지만, 앞으로의 삭제는 보호되지 않습니다.''',
 'fix_intro': '버전 관리를 활성화하고, 비용 관리를 위해 <b>수명주기 규칙</b>으로 오래된 버전을 정리합니다. 실수 삭제 방지의 마지막 단계는 <b>MFA Delete</b> 이지만, 이는 루트 계정 자격증명이 필요해 운영 부담이 큽니다.',
 'fix_cmd': '''# 1) 버전 관리 활성화
$ aws s3api put-bucket-versioning --bucket fin-core-txn-archive \\
      --versioning-configuration Status=Enabled

# 2) 오래된 버전 정리 규칙 (비용 통제)
$ aws s3api put-bucket-lifecycle-configuration --bucket fin-core-txn-archive \\
      --lifecycle-configuration '{
        "Rules": [{
          "ID": "expire-noncurrent",
          "Status": "Enabled",
          "Filter": {"Prefix": ""},
          "NoncurrentVersionExpiration": {"NoncurrentDays": 365},
          "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 7}
        }]
      }'

# 3) 거래원장처럼 보존 의무가 있는 데이터는 객체 잠금까지
$ aws s3api put-object-lock-configuration --bucket fin-core-txn-archive \\
      --object-lock-configuration '{"ObjectLockEnabled":"Enabled",
          "Rule":{"DefaultRetention":{"Mode":"GOVERNANCE","Years":5}}}\'''',
 'fix_out': '''$ aws s3api get-bucket-versioning --bucket fin-core-txn-archive
{
    "Status": "Enabled"
}

$ aws s3api delete-object --bucket fin-core-txn-archive --key ledger/2026-04.csv
{
    "DeleteMarker": true,
    "VersionId": "3sL9x.QmT7fVnB2kYcR0dHpZa1eWgU4j"
}

$ aws s3api list-object-versions --bucket fin-core-txn-archive --prefix ledger/2026-04.csv \\
      --query "Versions[*].[VersionId,IsLatest,Size]" --output table
--------------------------------------------------------------
|  null                              |  False  |  18437620    |
--------------------------------------------------------------

→ 삭제해도 이전 버전이 남아 복원할 수 있습니다. (삭제 마커 제거 시 원복)''',
 'iac': '''resource "aws_s3_bucket_versioning" "txn_archive" {
  bucket = aws_s3_bucket.txn_archive.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_lifecycle_configuration" "txn_archive" {
  bucket = aws_s3_bucket.txn_archive.id
  rule {
    id     = "expire-noncurrent"
    status = "Enabled"
    noncurrent_version_expiration { noncurrent_days = 365 }
    abort_incomplete_multipart_upload { days_after_initiation = 7 }
  }
}''',
 'pitfall': '<b>주의</b> — 버전 관리는 <b>랜섬웨어 대비책이 아닙니다.</b> 권한을 탈취한 공격자는 <code>s3:DeleteObjectVersion</code> 으로 이전 버전까지 지울 수 있습니다. 진짜 방어선은 <b>객체 잠금(COMPLIANCE 모드)</b> 또는 <b>다른 계정으로의 복제</b>입니다. 또한 버전 관리를 켜면 <b>삭제한 객체도 계속 과금</b>되므로 수명주기 규칙을 함께 넣지 않으면 비용이 조용히 늘어납니다.',
 'evidence': [
   '버킷별 <code>get-bucket-versioning</code> 출력 (Status 값)',
   '수명주기 규칙 설정 (<code>get-bucket-lifecycle-configuration</code>)',
   '보존 의무 데이터의 객체 잠금·보존 기간 설정',
   '복원 테스트 수행 기록 (삭제 → 복원 절차 및 결과)',
 ],
 'finance': '전자금융거래법상 <b>거래기록은 5년</b> 보존 의무가 있습니다. 클라우드 스토리지에서 이 의무는 "지우지 않는다"는 운영 약속이 아니라 <b>지울 수 없게 만든 설정</b>으로 증명해야 합니다. 버전 관리는 그 최소선이고, 보존 의무 대상은 객체 잠금까지 가는 것이 안전합니다.',
},

# ── PISM-031 EBS 볼륨 암호화 ─────────────────────────────────────────────
{
 'file': '07_fincloud-pism031.html', 'pism': 'PISM-031', 'risk': '5',
 'title': '디스크 볼륨 암호화 적용 여부', 'svc': 'EC2 · EBS',
 'area': '5. 운영 관리', 'ctrl': '5.3 정보처리시스템 보호대책',
 'detail': '디스크 볼륨이 암호화되지 않은 경우 비인가자에 의해 복원되어 중요 정보가 유출될 수 있는 위협이 존재하므로, 디스크 볼륨의 암호화 적용 여부를 점검합니다.',
 'console_path': '<b>EC2</b> → <b>볼륨</b> → 볼륨 목록에서 대상 볼륨 ID 클릭 → <b>세부 정보</b>에서 <b>암호화</b> 설정 확인',
 'cmds': [
   {'label': '① 볼륨별 암호화 현황 (평가기준 명시 명령)', 'cmd': 'aws ec2 describe-volumes --query "Volumes[*].{ID:VolumeId,Encrypted:Encrypted}" --output table',
    'out': '''--------------------------------------------
|              DescribeVolumes             |
+--------------------------+---------------+
|            ID            |   Encrypted   |
+--------------------------+---------------+
|  vol-0f27a9c8b3e415d6a   |  True         |
|  vol-08b3e7d1a95c24f70   |  <span class="er">False</span>        |
|  vol-0d94c26f71ab8e503   |  <span class="er">False</span>        |
+--------------------------+---------------+'''},
   {'label': '② 암호화 안 된 볼륨이 붙은 인스턴스 확인', 'cmd': 'aws ec2 describe-volumes --filters Name=encrypted,Values=false --query "Volumes[*].{ID:VolumeId,Size:Size,Attach:Attachments[0].InstanceId}" --output table',
    'out': '''-------------------------------------------------------------------
|                         DescribeVolumes                         |
+--------------------------+--------+-----------------------------+
|            ID            |  Size  |           Attach            |
+--------------------------+--------+-----------------------------+
|  vol-08b3e7d1a95c24f70   |  200   |  i-0a3f72be91c4d5e80        |
|  vol-0d94c26f71ab8e503   |  500   |  i-04e7b9c3d85a1f602        |
+--------------------------+--------+-----------------------------+

<span class="dim">i-0a3f72be91c4d5e80 = fin-core-app-01 / i-04e7b9c3d85a1f602 = fin-batch-worker</span>'''},
   {'label': '③ 계정 기본 암호화 설정 확인 (PISM-030 연계)', 'cmd': 'aws ec2 get-ebs-encryption-by-default',
    'out': '''{
    "EbsEncryptionByDefault": <span class="er">false</span>
}

<span class="er">※ 기본 암호화가 꺼져 있어 앞으로 만드는 볼륨도 평문으로 생성됩니다.</span>'''},
 ],
 'answer': 'bad',
 'why': '''3개 볼륨 중 <b>2개가 평문</b>이고, 더 중요한 것은 <b>계정 기본 암호화가 꺼져 있다</b>는 점입니다.
<div class="ev">vol-08b3e7d1a95c24f70 (200GB) → fin-core-app-01  : 코어뱅킹 앱 서버
vol-0d94c26f71ab8e503 (500GB) → fin-batch-worker : 배치 처리 데이터
EbsEncryptionByDefault = false → <b>지금 고쳐도 내일 만든 볼륨은 다시 평문</b></div>
개별 볼륨만 고치고 기본 설정을 놓치면 다음 평가에서 같은 지적이 반복됩니다. 이 항목은 <b>PISM-030(생성 시 기본 암호화)과 함께</b> 처리해야 끝납니다.''',
 'fix_intro': '<b>운영 중인 볼륨은 그 자리에서 암호화할 수 없습니다.</b> 스냅샷 → 암호화 복사 → 새 볼륨 생성 → 교체 순서를 거쳐야 하며 <b>중단 시간이 발생</b>합니다. 그래서 계정 기본 암호화를 먼저 켜고, 기존 볼륨은 정비 시간에 순차 교체하는 것이 실무 순서입니다.',
 'fix_cmd': '''# 0) 먼저 계정 기본값부터 — 신규 볼륨 재발 방지
$ aws ec2 enable-ebs-encryption-by-default
{
    "EbsEncryptionByDefault": true
}

# 1) 기존 볼륨 스냅샷
$ aws ec2 create-snapshot --volume-id vol-08b3e7d1a95c24f70 \\
      --description "pre-encryption fin-core-app-01"
# → snap-0c73b19e58af2d640

# 2) 스냅샷을 KMS 키로 암호화하여 복사
$ aws ec2 copy-snapshot --source-region ap-northeast-2 \\
      --source-snapshot-id snap-0c73b19e58af2d640 \\
      --encrypted --kms-key-id alias/fin-ebs-cmk \\
      --description "encrypted copy"
# → snap-0e81d47a2cb935f06

# 3) 암호화 스냅샷으로 새 볼륨 생성 후 교체 (인스턴스 중지 필요)
$ aws ec2 create-volume --snapshot-id snap-0e81d47a2cb935f06 \\
      --availability-zone ap-northeast-2a --volume-type gp3
$ aws ec2 stop-instances  --instance-ids i-0a3f72be91c4d5e80
$ aws ec2 detach-volume   --volume-id vol-08b3e7d1a95c24f70
$ aws ec2 attach-volume   --volume-id vol-0a62f3d97e14c8b25 \\
      --instance-id i-0a3f72be91c4d5e80 --device /dev/xvda
$ aws ec2 start-instances --instance-ids i-0a3f72be91c4d5e80''',
 'fix_out': '''$ aws ec2 get-ebs-encryption-by-default
{
    "EbsEncryptionByDefault": true
}

$ aws ec2 describe-volumes --query "Volumes[*].{ID:VolumeId,Encrypted:Encrypted,KmsKeyId:KmsKeyId}" --output table
------------------------------------------------------------------------------------------
|                                     DescribeVolumes                                    |
+--------------------------+-------------+-----------------------------------------------+
|            ID            |  Encrypted  |                   KmsKeyId                    |
+--------------------------+-------------+-----------------------------------------------+
|  vol-0f27a9c8b3e415d6a   |  True       |  arn:aws:kms:ap-northeast-2:...:key/fin-ebs   |
|  vol-0a62f3d97e14c8b25   |  True       |  arn:aws:kms:ap-northeast-2:...:key/fin-ebs   |
|  vol-0b5e81c72a9df4306   |  True       |  arn:aws:kms:ap-northeast-2:...:key/fin-ebs   |
+--------------------------+-------------+-----------------------------------------------+

→ 전 볼륨 암호화 + 기본 암호화 활성. 평문 볼륨은 스냅샷과 함께 폐기합니다.''',
 'iac': '''# 계정·리전 단위 기본 암호화 (가장 먼저 적용)
resource "aws_ebs_encryption_by_default" "this" { enabled = true }

resource "aws_ebs_default_kms_key" "this" {
  key_arn = aws_kms_key.fin_ebs.arn      # 서비스 기본키가 아닌 고객관리형 키(CMK)
}

resource "aws_instance" "core_app" {
  root_block_device {
    encrypted  = true
    kms_key_id = aws_kms_key.fin_ebs.arn
  }
}''',
 'pitfall': '<b>주의</b> — 기본 암호화를 켜도 <b>이미 만들어진 볼륨은 바뀌지 않습니다.</b> 또한 <b>서비스 기본키(aws/ebs)</b> 로 암호화하면 키 정책을 통제할 수 없어 "암호화했다"는 형식만 남습니다 — 금융권은 <b>고객관리형 키(CMK)</b> 로 교체 주기와 접근 권한을 직접 관리해야 합니다(PISM-026 연계). 마지막으로 <b>평문 시절의 스냅샷이 남아 있으면 조치가 무효</b>입니다. 반드시 함께 폐기하세요.',
 'evidence': [
   '<code>describe-volumes</code> 전체 출력 (Encrypted, KmsKeyId)',
   '<code>get-ebs-encryption-by-default</code> 출력',
   '암호화 미적용 볼륨의 교체 계획 및 수행 기록',
   '평문 시절 스냅샷·AMI 폐기 내역',
   '사용 중인 KMS 키가 고객관리형(CMK)임을 보이는 키 정책',
 ],
 'finance': '개인정보 보호법상 <b>고유식별정보·비밀번호는 암호화 저장</b>이 의무이고, 전자금융감독규정도 이용자 정보의 암호화를 요구합니다. 클라우드 EBS 는 스냅샷·AMI 로 손쉽게 복제되므로, <b>평문 볼륨 하나가 곧 복제 가능한 전체 데이터</b>입니다. 평가에서 위험도 5 가 붙는 이유입니다.',
},

# ── PISM-034 RDS 암호화 ──────────────────────────────────────────────────
{
 'file': '07_fincloud-pism034.html', 'pism': 'PISM-034', 'risk': '5',
 'title': 'DB 인스턴스 암호화 적용 여부', 'svc': 'RDS · Aurora',
 'area': '5. 운영 관리', 'ctrl': '5.3 정보처리시스템 보호대책',
 'detail': 'DB 인스턴스에 대한 암호화를 적용하지 않을 경우 스토리지에 직접 접근을 통한 데이터 유출 등의 위협이 있으므로, DB 인스턴스에 대한 암호화 적용 여부를 점검합니다.',
 'console_path': '<b>Aurora and RDS</b> → <b>데이터베이스</b> → 대상 DB 식별자 클릭(Aurora 는 클러스터) → <b>구성</b> 클릭 → <b>스토리지</b>의 <b>암호화</b> 설정 확인',
 'cmds': [
   {'label': '① DB 인스턴스 목록 확인', 'cmd': 'aws rds describe-db-instances --query "DBInstances[*].DBInstanceIdentifier"',
    'out': '''[
    "fin-core-db",
    "fin-mydata-db",
    "fin-report-replica"
]'''},
   {'label': '② 인스턴스별 암호화 적용 여부', 'cmd': 'aws rds describe-db-instances --query "DBInstances[*].{ID:DBInstanceIdentifier,Encrypted:StorageEncrypted,Engine:Engine}" --output table',
    'out': '''----------------------------------------------------------------
|                     DescribeDBInstances                      |
+-----------------------+-------------+------------------------+
|          ID           |  Encrypted  |         Engine         |
+-----------------------+-------------+------------------------+
|  fin-core-db          |  True       |  aurora-postgresql     |
|  fin-mydata-db        |  <span class="er">False</span>      |  postgres              |
|  fin-report-replica   |  <span class="er">False</span>      |  postgres              |
+-----------------------+-------------+------------------------+'''},
   {'label': '③ 자동 백업(스냅샷)도 함께 확인', 'cmd': 'aws rds describe-db-snapshots --db-instance-identifier fin-mydata-db --query "DBSnapshots[*].{ID:DBSnapshotIdentifier,Encrypted:Encrypted}" --output table',
    'out': '''----------------------------------------------------------------------
|                        DescribeDBSnapshots                         |
+-------------------------------------------------+------------------+
|                       ID                        |    Encrypted     |
+-------------------------------------------------+------------------+
|  rds:fin-mydata-db-2026-09-13-18-04             |  <span class="er">False</span>           |
|  rds:fin-mydata-db-2026-09-12-18-04             |  <span class="er">False</span>           |
+-------------------------------------------------+------------------+

<span class="er">※ 평문 DB 의 백업도 당연히 평문입니다 — 복원하면 그대로 노출됩니다.</span>'''},
 ],
 'answer': 'bad',
 'why': '''3개 중 <b>2개가 미암호화</b>이며, 그중 <code>fin-mydata-db</code> 는 <b>마이데이터(본인신용정보) 저장소</b>입니다.
<div class="ev">fin-core-db        : True  → 양호
fin-mydata-db      : <b>False</b> → 개인신용정보 평문 저장
fin-report-replica : <b>False</b> → 리드 리플리카도 별도 대상 (원본과 무관하게 판정)</div>
<b>리플리카를 빠뜨리는 실수</b>가 흔합니다. 원본이 암호화되어 있어도 리플리카·스냅샷·복원 인스턴스는 각각 판정 대상입니다.''',
 'fix_intro': '<b>RDS 는 생성 후 암호화로 전환할 수 없습니다.</b> 스냅샷을 암호화 복사한 뒤 <b>새 인스턴스로 복원</b>하고 엔드포인트를 교체해야 합니다. 서비스 중단이 불가피하므로 금융권에서는 보통 <b>정기 점검 시간에 계획 전환</b>합니다.',
 'fix_cmd': '''# 1) 현재 DB 스냅샷 생성
$ aws rds create-db-snapshot --db-instance-identifier fin-mydata-db \\
      --db-snapshot-identifier fin-mydata-db-preenc

# 2) 스냅샷을 CMK 로 암호화 복사
$ aws rds copy-db-snapshot \\
      --source-db-snapshot-identifier fin-mydata-db-preenc \\
      --target-db-snapshot-identifier fin-mydata-db-enc \\
      --kms-key-id alias/fin-rds-cmk

# 3) 암호화 스냅샷에서 새 인스턴스 복원
$ aws rds restore-db-instance-from-db-snapshot \\
      --db-instance-identifier fin-mydata-db-v2 \\
      --db-snapshot-identifier fin-mydata-db-enc \\
      --db-subnet-group-name fin-private-subnets \\
      --no-publicly-accessible

# 4) 엔드포인트 전환 후 구 인스턴스와 평문 스냅샷 삭제
$ aws rds delete-db-instance --db-instance-identifier fin-mydata-db \\
      --skip-final-snapshot
$ aws rds delete-db-snapshot --db-snapshot-identifier fin-mydata-db-preenc''',
 'fix_out': '''$ aws rds describe-db-instances --query "DBInstances[*].{ID:DBInstanceIdentifier,Encrypted:StorageEncrypted}" --output table
----------------------------------------------
|            DescribeDBInstances             |
+-----------------------+--------------------+
|          ID           |     Encrypted      |
+-----------------------+--------------------+
|  fin-core-db          |  True              |
|  fin-mydata-db-v2     |  True              |
|  fin-report-replica   |  True              |
+-----------------------+--------------------+

$ aws rds describe-db-snapshots --query "DBSnapshots[?Encrypted==\\`false\\`].DBSnapshotIdentifier"
[]

→ 인스턴스·스냅샷 모두 암호화 상태입니다. 평문 잔재 없음.''',
 'iac': '''resource "aws_db_instance" "mydata" {
  identifier        = "fin-mydata-db"
  engine            = "postgres"
  storage_encrypted = true                       # 생성 시에만 지정 가능
  kms_key_id        = aws_kms_key.fin_rds.arn    # 고객관리형 키
  publicly_accessible = false
  backup_retention_period = 35
  deletion_protection     = true
}

# 되돌림 방지 — 미암호화 RDS 생성을 조직 차원에서 금지
# SCP: Deny rds:CreateDBInstance when rds:StorageEncrypted = false''',
 'pitfall': '<b>주의</b> — Aurora 는 <b>클러스터 단위</b>로 암호화되므로 인스턴스가 아니라 <code>describe-db-clusters</code> 의 <code>StorageEncrypted</code> 를 봐야 합니다. 또한 <b>암호화 DB 의 스냅샷을 미암호화로 복사할 수는 없지만, 그 반대(평문 → 암호화)는 가능</b>합니다 — 이 성질을 이용해 전환합니다. 마지막으로 <b>성능 인사이트(Performance Insights)와 CloudWatch Logs 내보내기</b>에도 쿼리 문자열이 남을 수 있으니 별도 확인이 필요합니다.',
 'evidence': [
   'DB 인스턴스 목록 및 <code>StorageEncrypted</code> 값 (리플리카 포함)',
   'Aurora 클러스터의 <code>describe-db-clusters</code> 출력',
   '스냅샷 암호화 여부 목록',
   '전환 계획서 및 평문 인스턴스·스냅샷 폐기 내역',
   '사용 KMS 키 정보(고객관리형 여부)',
 ],
 'finance': '마이데이터(본인신용정보관리업)와 코어뱅킹 DB 는 <b>개인신용정보</b>를 담습니다. 신용정보법과 개인정보 보호법 모두 <b>암호화 저장</b>을 요구하며, 클라우드에서는 스토리지 계층 암호화(RDS 암호화)가 그 최소 구현입니다. 여기에 <b>컬럼 단위 암호화</b>를 더해야 내부자 위협까지 방어됩니다.',
},

# ── PISM-036 Lambda 환경변수 ─────────────────────────────────────────────
{
 'file': '07_fincloud-pism036.html', 'pism': 'PISM-036', 'risk': '5',
 'title': '환경변수 내 중요정보 암호화 적용 여부', 'svc': 'Lambda',
 'area': '5. 운영 관리', 'ctrl': '5.3 정보처리시스템 보호대책',
 'detail': '가상자원의 환경변수 내에 비밀번호, API Key 등 중요정보가 암호화되지 않은 평문 형태로 저장되어 있는 경우, 중요정보가 외부로 유출될 수 있는 위협이 존재하므로 중요정보를 암호화하여 저장하고 있는지 점검합니다.',
 'console_path': '<b>Lambda</b> → <b>함수</b> → 대상 함수 선택 → <b>구성</b> → <b>환경 변수</b>에서 목록과 값 확인',
 'cmds': [
   {'label': '① 함수 목록 확인', 'cmd': 'aws lambda list-functions --output table --query "Functions[*].FunctionName"',
    'out': '''-------------------------------------
|          ListFunctions            |
+-----------------------------------+
|  fin-settlement-batch             |
|  fin-openbanking-token-refresh    |
|  fin-fds-scoring                  |
+-------------------------------------'''},
   {'label': '② 환경변수 확인 (평가기준 명시 명령)', 'cmd': 'aws lambda get-function-configuration --function-name fin-openbanking-token-refresh --query "Environment"',
    'out': '''{
    "Variables": {
        "STAGE": "prod",
        "OPENBANKING_BASE": "https://openapi.openbanking.or.kr",
        <span class="er">"OPENBANKING_CLIENT_SECRET": "b7f3a91c-4e28-4d6a-9f05-c1873ae0d52b"</span>,
        <span class="er">"DB_PASSWORD": "Fin!Core#2026$prod"</span>,
        <span class="er">"SLACK_WEBHOOK": "https://hooks.slack.com/services/T04J/B07K/xQ2mZ9"</span>
    }
}'''},
   {'label': '③ KMS 로 암호화되어 있는지 확인', 'cmd': 'aws lambda get-function-configuration --function-name fin-openbanking-token-refresh --query "{KMSKeyArn:KMSKeyArn,Role:Role}"',
    'out': '''{
    "KMSKeyArn": <span class="er">null</span>,
    "Role": "arn:aws:iam::382011749265:role/fin-lambda-openbanking"
}

<span class="er">※ KMSKeyArn 이 null — 전송 중 암호화 헬퍼가 적용되지 않았습니다.</span>'''},
   {'label': '④ 이 값을 누가 볼 수 있는가', 'cmd': 'aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::382011749265:role/fin-developer --action-names lambda:GetFunctionConfiguration --query "EvaluationResults[*].EvalDecision"',
    'out': '''[
    "allowed"
]

<span class="er">※ 개발자 역할도 GetFunctionConfiguration 으로 평문 값을 그대로 읽을 수 있습니다.</span>'''},
 ],
 'answer': 'bad',
 'why': '''환경변수에 <b>세 개의 비밀값이 평문</b>으로 들어 있습니다.
<div class="ev">OPENBANKING_CLIENT_SECRET → 오픈뱅킹 API 클라이언트 시크릿 (출금이체 권한과 직결)
DB_PASSWORD               → 운영 DB 비밀번호
SLACK_WEBHOOK             → 알림 채널 탈취 가능 (피싱·사회공학 경로)</div>
Lambda 환경변수는 <b>저장 시 AWS 관리 키로 자동 암호화</b>되지만, 그것은 디스크 차원의 이야기입니다. <code>GetFunctionConfiguration</code> 권한이 있으면 <b>콘솔·CLI 에서 평문 그대로 보입니다.</b> "암호화되어 있다"는 설명에 속기 쉬운 항목입니다.''',
 'fix_intro': '환경변수에서 비밀값을 <b>걷어내고</b> Secrets Manager 에 옮긴 뒤, 함수가 <b>실행 시점에 조회</b>하도록 바꿉니다. 환경변수에는 시크릿의 <b>이름(ARN)</b> 만 남깁니다.',
 'fix_cmd': '''# 1) 시크릿 생성 (자동 교체 활성화)
$ aws secretsmanager create-secret --name fin/openbanking/client-secret \\
      --kms-key-id alias/fin-secrets-cmk \\
      --secret-string '{"client_secret":"b7f3a91c-4e28-4d6a-9f05-c1873ae0d52b"}'

$ aws secretsmanager rotate-secret --secret-id fin/openbanking/client-secret \\
      --rotation-lambda-arn arn:aws:lambda:ap-northeast-2:382011749265:function:fin-secret-rotator \\
      --rotation-rules AutomaticallyAfterDays=90

# 2) 환경변수에서 비밀값 제거 — 이름만 남긴다
$ aws lambda update-function-configuration \\
      --function-name fin-openbanking-token-refresh \\
      --environment 'Variables={STAGE=prod,
          OPENBANKING_BASE=https://openapi.openbanking.or.kr,
          SECRET_ID=fin/openbanking/client-secret}'

# 3) 실행 역할에 해당 시크릿만 읽을 권한 부여 (와일드카드 금지)
$ aws iam put-role-policy --role-name fin-lambda-openbanking \\
      --policy-name read-openbanking-secret --policy-document '{
        "Version":"2012-10-17",
        "Statement":[{"Effect":"Allow","Action":"secretsmanager:GetSecretValue",
          "Resource":"arn:aws:secretsmanager:ap-northeast-2:382011749265:secret:fin/openbanking/client-secret-*"}]
      }'

# 4) DB 비밀번호는 IAM 데이터베이스 인증으로 아예 없앨 수도 있다
$ aws rds modify-db-instance --db-instance-identifier fin-core-db \\
      --enable-iam-database-authentication --apply-immediately''',
 'fix_out': '''$ aws lambda get-function-configuration --function-name fin-openbanking-token-refresh --query "Environment"
{
    "Variables": {
        "STAGE": "prod",
        "OPENBANKING_BASE": "https://openapi.openbanking.or.kr",
        "SECRET_ID": "fin/openbanking/client-secret"
    }
}

$ aws secretsmanager describe-secret --secret-id fin/openbanking/client-secret \\
      --query "{Rotation:RotationEnabled,Days:RotationRules.AutomaticallyAfterDays,Kms:KmsKeyId}"
{
    "Rotation": true,
    "Days": 90,
    "Kms": "arn:aws:kms:ap-northeast-2:382011749265:key/fin-secrets-cmk"
}

→ 환경변수에 비밀값이 남아 있지 않고, 90일 자동 교체가 걸렸습니다.''',
 'iac': '''resource "aws_lambda_function" "token_refresh" {
  function_name = "fin-openbanking-token-refresh"
  role          = aws_iam_role.lambda_openbanking.arn

  environment {
    variables = {
      STAGE            = "prod"
      OPENBANKING_BASE = "https://openapi.openbanking.or.kr"
      SECRET_ID        = aws_secretsmanager_secret.openbanking.name
      # 비밀값을 여기 두지 않는다. tfstate 에도 그대로 남기 때문이다.
    }
  }
}

resource "aws_secretsmanager_secret_rotation" "openbanking" {
  secret_id           = aws_secretsmanager_secret.openbanking.id
  rotation_lambda_arn = aws_lambda_function.rotator.arn
  rotation_rules { automatically_after_days = 90 }
}''',
 'pitfall': '<b>주의</b> — 환경변수에서 값을 지워도 <b>과거 버전에는 남아 있습니다.</b> <code>aws lambda list-versions-by-function</code> 으로 이전 버전의 환경변수를 확인하고 필요하면 삭제하세요. 그리고 <b>이미 노출된 시크릿은 교체가 답입니다</b> — 지웠다고 안전해지지 않습니다. Terraform 을 쓴다면 <b>tfstate 파일에도 평문으로 기록</b>되므로 state 백엔드 암호화와 접근 통제가 함께 필요합니다.',
 'evidence': [
   '함수별 <code>get-function-configuration --query Environment</code> 출력',
   '비밀값이 제거되었음을 보이는 조치 후 출력',
   'Secrets Manager 시크릿 목록·KMS 키·자동 교체 주기 설정',
   '실행 역할의 시크릿 접근 정책 (리소스 한정 여부)',
   '노출 이력이 있는 시크릿의 교체 기록',
 ],
 'finance': '오픈뱅킹 클라이언트 시크릿은 <b>출금이체 API 호출 권한</b>과 직결됩니다. 유출 시 곧바로 금전 피해로 이어지므로, 평가에서 위험도 5 가 붙습니다. 자격증명의 <b>주기적 갱신</b>(PISM-028·043)과 <b>코드·이미지·리포지토리에 포함되지 않도록 자동 검출</b>하는 체계까지 함께 갖춰야 합니다.',
},

# ── PISM-037 비밀번호 정책 ───────────────────────────────────────────────
{
 'file': '07_fincloud-pism037.html', 'pism': 'PISM-037', 'risk': '5',
 'title': '비밀번호 정책 수립 및 로그인 제한 설정', 'svc': 'IAM',
 'area': '5. 운영 관리', 'ctrl': '5.3 정보처리시스템 보호대책', 'evaltype': '관리체계, 스크립트',
 'detail': '계정의 비밀번호가 취약하게 설정되어 있거나 복잡도 정책이 미흡한 경우, 비인가자가 비밀번호를 유추하거나 무작위 대입 공격을 통해 계정을 탈취하여 가상자원 또는 관리 시스템에 접근할 수 있는 위협이 존재하므로 비밀번호 설정 상태 및 복잡도 정책이 적절하게 적용되어 있는지 점검합니다.',
 'console_path': '<b>IAM</b> → <b>계정 설정</b> → <b>암호 정책</b>에서 복잡도·만료·재사용 방지 설정 확인',
 'cmds': [
   {'label': '① 계정 암호 정책 확인 (평가기준 명시 명령)', 'cmd': 'aws iam get-account-password-policy',
    'out': '''{
    "PasswordPolicy": {
        "MinimumPasswordLength": <span class="er">8</span>,
        "RequireSymbols": <span class="er">false</span>,
        "RequireNumbers": true,
        "RequireUppercaseCharacters": <span class="er">false</span>,
        "RequireLowercaseCharacters": true,
        "AllowUsersToChangePassword": true,
        "ExpirePasswords": <span class="er">false</span>,
        "HardExpiry": false
    }
}

<span class="er">※ PasswordReusePrevention 키가 없습니다 — 재사용 방지 미설정.</span>'''},
   {'label': '② 자격증명 보고서 생성', 'cmd': 'aws iam generate-credential-report',
    'out': '''{
    "State": "COMPLETE",
    "Description": "No report exists. Starting a new report generation task"
}'''},
   {'label': '③ 콘솔 비밀번호 사용 계정과 마지막 변경일', 'cmd': 'aws iam get-credential-report --query Content --output text | base64 -d | cut -d, -f1,5,6',
    'out': '''user,password_last_used,password_last_changed
&lt;root_account&gt;,2026-09-02T08:41:19+00:00,<span class="er">2024-11-05T02:13:44+00:00</span>
fin-admin-kim,2026-09-13T23:50:07+00:00,<span class="er">2025-01-20T09:31:02+00:00</span>
fin-dev-lee,2026-09-12T10:02:55+00:00,2026-07-02T14:18:30+00:00
fin-audit-readonly,2026-09-14T01:58:12+00:00,2026-06-11T05:44:21+00:00

<span class="er">※ 만료 정책이 없어 root 는 약 2년, fin-admin-kim 은 약 20개월째 같은 비밀번호입니다.</span>'''},
 ],
 'answer': 'bad',
 'why': '''정책이 존재하기는 하지만 <b>금융권 기준으로는 미흡</b>하고, 그 결과가 실제 계정에 나타납니다.
<div class="ev">MinimumPasswordLength      : 8   → 권고 14 자 이상
RequireSymbols             : false → 특수문자 미요구
RequireUppercaseCharacters : false → 대문자 미요구
ExpirePasswords            : false → <b>만료 없음</b>
PasswordReusePrevention    : (없음) → 재사용 무제한

→ root 계정이 2024-11 이후 비밀번호 미변경 (약 2년)</div>
"정책이 설정되어 있다"와 "정책이 충분하다"는 다릅니다. 이 항목은 <b>설정값 자체를 기준과 대조</b>해야 합니다.''',
 'fix_intro': '복잡도·만료·재사용 방지를 한 번에 설정합니다. 다만 <b>비밀번호 정책만으로는 부족</b>합니다 — AWS 는 로그인 실패 잠금(계정 락아웃)을 제공하지 않으므로, 무작위 대입 대응은 <b>MFA 의무화</b>(PISM-039)와 <b>IdP 연동(SSO)</b> 으로 해결해야 합니다.',
 'fix_cmd': '''# 1) 암호 정책 강화
$ aws iam update-account-password-policy \\
      --minimum-password-length 14 \\
      --require-symbols \\
      --require-numbers \\
      --require-uppercase-characters \\
      --require-lowercase-characters \\
      --allow-users-to-change-password \\
      --max-password-age 90 \\
      --password-reuse-prevention 12

# 2) 오래된 비밀번호 강제 교체 (다음 로그인 시)
$ aws iam update-login-profile --user-name fin-admin-kim \\
      --password-reset-required

# 3) 근본 해결 — IAM 사용자 대신 IAM Identity Center(SSO) 로 전환
$ aws sso-admin list-instances
# 사내 IdP 와 SAML 연동 후, 콘솔 로그인은 IdP 정책(잠금·MFA)을 따르게 한다''',
 'fix_out': '''$ aws iam get-account-password-policy
{
    "PasswordPolicy": {
        "MinimumPasswordLength": 14,
        "RequireSymbols": true,
        "RequireNumbers": true,
        "RequireUppercaseCharacters": true,
        "RequireLowercaseCharacters": true,
        "AllowUsersToChangePassword": true,
        "ExpirePasswords": true,
        "MaxPasswordAge": 90,
        "PasswordReusePrevention": 12,
        "HardExpiry": false
    }
}

→ 복잡도·만료(90일)·재사용 방지(12회)가 모두 적용되었습니다.''',
 'iac': '''resource "aws_iam_account_password_policy" "fin" {
  minimum_password_length        = 14
  require_symbols                = true
  require_numbers                = true
  require_uppercase_characters   = true
  require_lowercase_characters   = true
  allow_users_to_change_password = true
  max_password_age               = 90
  password_reuse_prevention      = 12
  hard_expiry                    = false   # true 로 두면 만료 시 관리자 개입 필요
}''',
 'pitfall': '<b>주의</b> — <code>update-account-password-policy</code> 는 <b>전달하지 않은 옵션을 기본값으로 되돌립니다.</b> 일부만 바꾸려고 한두 개 옵션만 주면 나머지가 초기화되므로, 항상 <b>전체 옵션을 함께</b> 전달하세요. 또 <code>hard_expiry = true</code> 는 만료된 사용자가 스스로 비밀번호를 바꿀 수 없게 만들어, <b>전원이 동시에 잠기는 사고</b>로 이어질 수 있습니다.',
 'evidence': [
   '<code>get-account-password-policy</code> 출력 (복잡도·만료·재사용 방지)',
   '자격증명 보고서 (비밀번호 최종 변경일, 미사용 계정)',
   'MFA 적용 현황 (PISM-039 와 함께 제출)',
   'IdP 연동 시 IdP 측 잠금 임계값 정책',
 ],
 'finance': '전자금융감독규정은 <b>비밀번호 복잡도와 주기적 변경</b>을 요구합니다. 다만 클라우드 관리 콘솔은 <b>인터넷에서 바로 접근 가능한 관리 평면</b>이라, 비밀번호만으로는 방어선이 부족합니다. 평가에서도 이 항목은 <b>MFA·SSO 와 묶어서</b> 봅니다 — 비밀번호 정책만 강화하고 MFA 가 없으면 실질적 개선으로 인정받기 어렵습니다.',
},

# ── PISM-039 MFA ─────────────────────────────────────────────────────────
{
 'file': '07_fincloud-pism039.html', 'pism': 'PISM-039', 'risk': '5',
 'title': '클라우드 자원에 접근 가능한 계정에 추가인증수단 적용 여부', 'svc': 'IAM',
 'area': '6. 접근통제', 'ctrl': '6.1 계정 및 권한 관리', 'evaltype': '관리체계, 스크립트',
 'detail': '클라우드 자원에 접근 가능한 계정(관리자 계정 포함)에 대한 추가 인증 수단이 적용되지 않으면 계정이 탈취될 경우 공격자가 클라우드 자원에 접근할 수 있는 위협이 존재하므로, OTP·이메일·바이오 인증 등의 이중 인증이 설정되어 있는지 여부를 점검합니다.',
 'console_path': '<b>IAM</b> → <b>사용자</b> → 사용자 목록의 <b>MFA</b> 컬럼 확인 (안 보이면 우측 상단 설정에서 컬럼 활성화)',
 'cmds': [
   {'label': '① 자격증명 보고서 생성', 'cmd': 'aws iam generate-credential-report',
    'out': '''{
    "State": "COMPLETE"
}'''},
   {'label': '② 계정별 MFA 활성 여부 (평가기준 명시 명령)', 'cmd': 'aws iam get-credential-report --query Content --output text | base64 -d | cut -d, -f1,8',
    'out': '''user,mfa_active
&lt;root_account&gt;,<span class="er">false</span>
fin-admin-kim,<span class="er">false</span>
fin-dev-lee,true
fin-audit-readonly,true
fin-batch-svc,false

<span class="dim">fin-batch-svc 는 프로그래밍 전용 계정(콘솔 비밀번호 없음)</span>'''},
   {'label': '③ 콘솔 로그인이 가능한 계정만 추려 보기', 'cmd': 'aws iam get-credential-report --query Content --output text | base64 -d | cut -d, -f1,4,8',
    'out': '''user,password_enabled,mfa_active
&lt;root_account&gt;,<span class="er">true</span>,<span class="er">false</span>
fin-admin-kim,<span class="er">true</span>,<span class="er">false</span>
fin-dev-lee,true,true
fin-audit-readonly,true,true
fin-batch-svc,false,false

<span class="er">※ 콘솔 접속이 가능하면서 MFA 가 없는 계정: root, fin-admin-kim</span>'''},
   {'label': '④ root 계정 MFA 장치 확인', 'cmd': 'aws iam get-account-summary --query "SummaryMap.AccountMFAEnabled"',
    'out': '<span class="er">0</span>\n\n<span class="er">※ 0 = root 계정에 MFA 장치가 등록되어 있지 않습니다.</span>'},
 ],
 'answer': 'bad',
 'why': '''<b>root 계정과 관리자 계정에 MFA 가 없습니다.</b>
<div class="ev">&lt;root_account&gt; : 콘솔 로그인 가능 + MFA 없음 → <b>최악의 조합</b>
fin-admin-kim   : 콘솔 로그인 가능 + MFA 없음 + 관리자 권한
fin-batch-svc   : MFA 없음이지만 <b>콘솔 비밀번호가 없는</b> 프로그래밍 전용 → 판정 제외</div>
<b>판정 요령</b>: <code>mfa_active=false</code> 만 세면 안 됩니다. <code>password_enabled</code> 와 함께 봐야 합니다 — 서비스 계정은 애초에 콘솔로 로그인하지 않으므로 MFA 대상이 아니고, 대신 <b>액세스 키 관리</b>(PISM-042·043)로 평가합니다.''',
 'fix_intro': 'root 는 <b>하드웨어 또는 가상 MFA 를 즉시 등록</b>하고 이후 일상 업무에서 사용하지 않습니다. IAM 사용자는 <b>MFA 없이는 아무것도 못 하게 하는 정책</b>을 붙이는 것이 개별 등록보다 확실합니다.',
 'fix_cmd': '''# 1) IAM 사용자 MFA 등록 (가상 MFA 예시)
$ aws iam create-virtual-mfa-device --virtual-mfa-device-name fin-admin-kim \\
      --outfile /tmp/qr.png --bootstrap-method QRCodePNG
$ aws iam enable-mfa-device --user-name fin-admin-kim \\
      --serial-number arn:aws:iam::382011749265:mfa/fin-admin-kim \\
      --authentication-code1 492013 --authentication-code2 771648

# 2) MFA 없으면 아무 작업도 못 하게 하는 정책 (핵심)
$ aws iam create-policy --policy-name DenyAllExceptSelfMFA --policy-document '{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyUnlessMFA",
    "Effect": "Deny",
    "NotAction": [
      "iam:CreateVirtualMFADevice", "iam:EnableMFADevice",
      "iam:ListMFADevices", "iam:ListVirtualMFADevices",
      "iam:ResyncMFADevice", "iam:ChangePassword",
      "iam:GetUser", "sts:GetSessionToken"
    ],
    "Resource": "*",
    "Condition": {"BoolIfExists": {"aws:MultiFactorAuthPresent": "false"}}
  }]
}'

# 3) root 는 콘솔에서 직접 등록 (CLI 로 등록 불가)
#    IAM → 보안 자격 증명 → 멀티 팩터 인증(MFA) → 디바이스 할당
#    등록 후 root 자격증명은 봉인하고 비상 절차(PISM-071)로만 사용''',
 'fix_out': '''$ aws iam get-account-summary --query "SummaryMap.AccountMFAEnabled"
1

$ aws iam get-credential-report --query Content --output text | base64 -d | cut -d, -f1,4,8
user,password_enabled,mfa_active
<root_account>,true,true
fin-admin-kim,true,true
fin-dev-lee,true,true
fin-audit-readonly,true,true
fin-batch-svc,false,false

→ 콘솔 접근이 가능한 모든 계정에 MFA 가 적용되었습니다.''',
 'iac': '''# 조직 전체에 강제 — SCP 로 MFA 없는 호출을 차단
data "aws_iam_policy_document" "require_mfa" {
  statement {
    effect    = "Deny"
    not_actions = ["iam:*", "sts:GetSessionToken"]
    resources = ["*"]
    condition {
      test     = "BoolIfExists"
      variable = "aws:MultiFactorAuthPresent"
      values   = ["false"]
    }
  }
}

# root 사용 자체를 감시 — 로그인하면 즉시 알림
resource "aws_cloudwatch_event_rule" "root_login" {
  event_pattern = jsonencode({
    "detail-type" = ["AWS Console Sign In via CloudTrail"],
    "detail"      = { "userIdentity" = { "type" = ["Root"] } }
  })
}''',
 'pitfall': '<b>주의</b> — <code>aws:MultiFactorAuthPresent</code> 는 <b>액세스 키로 호출할 때 아예 존재하지 않는 키</b>입니다. 그래서 <code>Bool</code> 이 아니라 <b><code>BoolIfExists</code></b> 를 써야 합니다. <code>Bool</code> 로 쓰면 액세스 키 호출이 전부 통과해 정책이 무력화됩니다. 또한 이 정책을 붙이기 전에 <b>MFA 등록 경로(NotAction 목록)를 반드시 열어 두세요</b> — 안 그러면 아직 MFA 를 등록하지 않은 사용자가 등록조차 못 하고 잠깁니다.',
 'evidence': [
   '자격증명 보고서 (<code>mfa_active</code>, <code>password_enabled</code> 컬럼)',
   '<code>SummaryMap.AccountMFAEnabled</code> (root MFA 등록 여부)',
   'MFA 강제 정책 또는 SCP 문서',
   'MFA 미대상 계정(서비스 계정)의 소명 및 액세스 키 관리 현황',
   'root 로그인 알림 체계 설정',
 ],
 'finance': '클라우드 관리 콘솔은 <b>인터넷에서 접근 가능한 최고 권한 평면</b>입니다. 계정 하나가 탈취되면 망분리·방화벽이 의미를 잃습니다. 그래서 금융권 평가에서 MFA 는 <b>위험도 5</b> 이며, 특히 <b>root 계정 MFA 미적용</b>은 단일 항목으로 즉시 지적됩니다. root 는 MFA 등록 후 <b>비상 접근용으로만</b> 봉인하는 것이 원칙입니다(PISM-040·071).',
},

# ── PISM-041 root 액세스 키 ──────────────────────────────────────────────
{
 'file': '07_fincloud-pism041.html', 'pism': 'PISM-041', 'risk': '5',
 'title': '관리자 계정의 액세스 키 삭제 여부', 'svc': 'IAM',
 'area': '6. 접근통제', 'ctrl': '6.1 계정 및 권한 관리',
 'detail': '관리자 계정(root)의 액세스 키가 유출될 경우 프로그래밍 방식으로 접근하여 제약 없이 가상자원에 대한 제어가 가능해지는 위협이 존재하므로 관리자 계정의 액세스 키 삭제 여부를 점검합니다.',
 'console_path': '<b>IAM</b> → <b>자격 증명 보고서</b> → <b>보안 인증 보고서</b> 다운로드 → 파일 내 <code>&lt;root_account&gt;</code> 행 확인',
 'cmds': [
   {'label': '① 자격증명 보고서 생성', 'cmd': 'aws iam generate-credential-report',
    'out': '{\n    "State": "COMPLETE"\n}'},
   {'label': '② root 액세스 키 활성 여부 (평가기준 명시 명령)', 'cmd': 'aws iam get-credential-report --output text --query Content | base64 -d | grep "root_account" | awk -F\',\' \'{print "access_key_1_active: "$9", access_key_2_active: "$14}\'',
    'out': 'access_key_1_active: <span class="er">true</span>, access_key_2_active: false'},
   {'label': '③ root 요약 정보로 교차 확인', 'cmd': 'aws iam get-account-summary --query "{RootKeys:SummaryMap.AccountAccessKeysPresent,RootMFA:SummaryMap.AccountMFAEnabled}"',
    'out': '''{
    "RootKeys": <span class="er">1</span>,
    "RootMFA": <span class="er">0</span>
}

<span class="er">※ root 액세스 키 1개 존재 + root MFA 없음 — 키만 있으면 무제한 제어가 가능합니다.</span>'''},
   {'label': '④ 이 키가 최근에 쓰였는가', 'cmd': 'aws iam get-credential-report --output text --query Content | base64 -d | grep "root_account" | awk -F\',\' \'{print "key1_last_used: "$11", region: "$12", service: "$13}\'',
    'out': '''key1_last_used: <span class="er">2026-08-27T14:33:08+00:00</span>, region: ap-northeast-2, service: s3

<span class="er">※ 3주 전까지 실제로 사용된 흔적이 있습니다 — 배치 스크립트가 root 키를 쓰고 있을 가능성.</span>'''},
 ],
 'answer': 'bad',
 'why': '''<b>root 계정에 활성 액세스 키가 존재합니다.</b>
<div class="ev">access_key_1_active : <b>true</b>  → 존재 자체가 지적 사항
AccountMFAEnabled   : 0       → MFA 도 없음
key1_last_used      : 2026-08-27 → <b>실제로 쓰이고 있음</b></div>
root 액세스 키는 <b>권한 축소가 불가능</b>합니다. IAM 정책·SCP 로도 root 를 제한할 수 없어, 키 한 줄이 곧 계정 전체입니다. 게다가 최근 사용 흔적이 있으므로 <b>그냥 지우면 배치가 멈춥니다</b> — 무엇이 쓰고 있는지 먼저 찾아야 합니다.''',
 'fix_intro': '<b>바로 지우지 마세요.</b> 최근 사용 기록이 있으므로 ① 무엇이 쓰는지 CloudTrail 로 특정 → ② 전용 IAM 역할로 대체 → ③ 키 비활성화(관찰) → ④ 삭제 순서로 진행합니다.',
 'fix_cmd': '''# 1) 누가 root 키를 쓰는지 CloudTrail 에서 특정
$ aws cloudtrail lookup-events \\
      --lookup-attributes AttributeKey=Username,AttributeValue=root \\
      --start-time 2026-08-01T00:00:00Z \\
      --query "Events[*].{Time:EventTime,Name:EventName,Src:CloudTrailEvent}" \\
      --max-results 20
# → sourceIPAddress 10.40.7.62 (fin-batch-worker) 에서 s3:PutObject 호출 확인

# 2) 대체 자격증명 마련 — 인스턴스 프로파일(키 없는 역할)
$ aws iam create-role --role-name fin-batch-s3-writer \\
      --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{
          "Effect":"Allow","Principal":{"Service":"ec2.amazonaws.com"},
          "Action":"sts:AssumeRole"}]}'
$ aws iam put-role-policy --role-name fin-batch-s3-writer \\
      --policy-name write-archive --policy-document '{"Version":"2012-10-17","Statement":[{
          "Effect":"Allow","Action":["s3:PutObject"],
          "Resource":"arn:aws:s3:::fin-core-txn-archive/*"}]}'
$ aws ec2 associate-iam-instance-profile \\
      --instance-id i-04e7b9c3d85a1f602 \\
      --iam-instance-profile Name=fin-batch-s3-writer

# 3) root 키 비활성화 — 먼저 끄고 며칠 관찰 (되돌리기 쉬움)
#    ※ root 키 조작은 root 로 콘솔 로그인해야 한다 (IAM 사용자로는 불가)
#    IAM → 보안 자격 증명 → 액세스 키 → 비활성화

# 4) 이상 없으면 삭제 + root MFA 등록 + 사용 알림 설정''',
 'fix_out': '''$ aws iam get-account-summary --query "{RootKeys:SummaryMap.AccountAccessKeysPresent,RootMFA:SummaryMap.AccountMFAEnabled}"
{
    "RootKeys": 0,
    "RootMFA": 1
}

$ aws iam get-credential-report --output text --query Content | base64 -d | grep "root_account" | awk -F',' '{print "key1: "$9", key2: "$14}'
key1: false, key2: false

→ root 액세스 키가 제거되고 MFA 가 등록되었습니다.
   배치는 인스턴스 프로파일(키 없는 역할)로 전환되어 정상 동작합니다.''',
 'iac': '''# root 키는 IaC 로 만들 수도 지울 수도 없다 — 콘솔 수작업이다.
# 대신 "다시 생기면 즉시 안다"를 코드로 만든다.

resource "aws_cloudwatch_event_rule" "root_activity" {
  name = "detect-root-usage"
  event_pattern = jsonencode({
    "detail-type" = ["AWS API Call via CloudTrail"],
    "detail"      = { "userIdentity" = { "type" = ["Root"] } }
  })
}

resource "aws_cloudwatch_event_target" "notify" {
  rule      = aws_cloudwatch_event_rule.root_activity.name
  arn       = aws_sns_topic.security_alert.arn
}

# 배치는 키가 아니라 역할로 (키 자체를 만들지 않는 것이 최선)
resource "aws_iam_instance_profile" "batch" {
  role = aws_iam_role.batch_s3_writer.name
}''',
 'pitfall': '<b>주의</b> — root 액세스 키는 <b>IAM 사용자 권한으로는 지울 수 없습니다.</b> root 자격증명으로 콘솔에 직접 로그인해야 하며, 이때 <b>MFA 부터 등록</b>하는 것이 순서입니다. 그리고 "안 쓰는 것 같으니 바로 지우자"는 위험합니다 — <code>key1_last_used</code> 가 비어 있어도 <b>분기 배치·연말 정산 같은 저빈도 작업</b>이 쓰고 있을 수 있습니다. 최소 한 달은 비활성화 상태로 관찰한 뒤 삭제하세요.',
 'evidence': [
   '자격증명 보고서의 <code>&lt;root_account&gt;</code> 행 (access_key_1/2_active, last_used)',
   '<code>SummaryMap.AccountAccessKeysPresent</code> 값',
   'root 키 사용 주체를 특정한 CloudTrail 조회 결과',
   '대체 자격증명(역할) 전환 내역',
   'root 사용 시 알림 설정 및 비상 사용 절차 문서',
 ],
 'finance': 'root 액세스 키는 <b>권한 분리 원칙의 정면 위반</b>입니다. 금융회사는 시스템 접근 권한을 업무별로 최소화하고 상호 감시가 가능하도록 해야 하는데, root 키는 그 어떤 통제도 적용되지 않습니다. 평가에서 <b>단일 항목으로 즉시 취약 판정</b>되는 대표적인 지적 사항이며, 사고 시 "누가 했는지" 특정이 불가능해 책임 추적성까지 무너집니다.',
},

# ── PISM-064 IMDSv2 ──────────────────────────────────────────────────────
{
 'file': '07_fincloud-pism064.html', 'pism': 'PISM-064', 'risk': '5',
 'title': '컴퓨팅 인스턴스에서 IMDSv1 비활성화 여부', 'svc': 'EC2',
 'area': '5. 운영 관리', 'ctrl': '5.3 정보처리시스템 보호대책',
 'detail': 'IMDSv1 은 별도의 인증을 요구하지 않아 SSRF(Server-Side Request Forgery)를 통해 자격증명 탈취 위협 등이 존재하므로 IMDSv2 활성화 여부를 점검합니다.',
 'console_path': '<b>EC2</b> → <b>인스턴스</b> → 대상 인스턴스 ID 클릭 → <b>작업</b> → <b>인스턴스 메타데이터 옵션 수정</b> → <b>IMDSv2</b> 옵션 확인',
 'cmds': [
   {'label': '① IMDSv2 가 선택(optional)인 인스턴스 목록 — 평가기준 명시 명령', 'cmd': 'aws ec2 describe-instances --output table --filter "Name=metadata-options.http-tokens,Values=optional" --query "Reservations[*].Instances[*].{Instance:InstanceId}"',
    'out': '''-----------------------------
|     DescribeInstances     |
+---------------------------+
|         Instance          |
+---------------------------+
|  <span class="er">i-0a3f72be91c4d5e80</span>      |
|  <span class="er">i-0c81d5fa27e93b146</span>      |
+---------------------------+

<span class="dim">optional = IMDSv1 도 그대로 허용된다는 뜻입니다.</span>'''},
   {'label': '② 전체 인스턴스의 메타데이터 설정 확인', 'cmd': 'aws ec2 describe-instances --query "Reservations[*].Instances[*].{ID:InstanceId,Tokens:MetadataOptions.HttpTokens,Hop:MetadataOptions.HttpPutResponseHopLimit}" --output table',
    'out': '''--------------------------------------------------------------------
|                        DescribeInstances                         |
+--------------------------+---------------+-----------------------+
|            ID            |    Tokens     |          Hop          |
+--------------------------+---------------+-----------------------+
|  i-0a3f72be91c4d5e80     |  <span class="er">optional</span>     |  <span class="er">2</span>                    |
|  i-0c81d5fa27e93b146     |  <span class="er">optional</span>     |  1                    |
|  i-04e7b9c3d85a1f602     |  required     |  1                    |
+--------------------------+---------------+-----------------------+'''},
   {'label': '③ 공격 재현 — 앱의 SSRF 로 메타데이터 호출', 'cmd': 'curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/fin-core-app-role',
    'out': '''{
  "Code" : "Success",
  "Type" : "AWS-HMAC",
  "AccessKeyId" : "<span class="er">ASIA4XQ7N2VZJ8RKPMQD</span>",
  "SecretAccessKey" : "<span class="er">wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY</span>",
  "Token" : "<span class="er">IQoJb3JpZ2luX2VjEJr//////////wEaDmFwLW5vcnRoZWFzdC0yIkcw...</span>",
  "Expiration" : "2026-09-14T08:47:22Z"
}

<span class="er">※ 헤더 하나 없이 임시 자격증명이 그대로 반환되었습니다. IMDSv1 이 살아 있습니다.</span>'''},
 ],
 'answer': 'bad',
 'why': '''3개 중 <b>2개가 <code>HttpTokens=optional</code></b> — IMDSv1 이 그대로 열려 있습니다.
<div class="ev">optional : IMDSv1(토큰 없는 GET)도 허용 → <b>SSRF 한 번으로 자격증명 탈취</b>
required : IMDSv2 강제 (PUT 으로 토큰 발급 후에만 조회 가능) → 양호

추가 지적: i-0a3f72be91c4d5e80 은 HttpPutResponseHopLimit = 2
  → 홉 제한이 2 면 <b>컨테이너 안에서도</b> 메타데이터에 닿습니다.
    EC2 에서 단독 실행이라면 1 이어야 합니다.</div>
Capital One 사고(2019)가 바로 이 경로였습니다 — WAF 의 SSRF → IMDSv1 → 역할 자격증명 → S3 대량 유출.''',
 'fix_intro': 'IMDSv2 를 <b>required</b> 로 바꾸고 홉 제한을 1 로 낮춥니다. 재시작 없이 적용되지만, <b>구형 SDK 나 직접 curl 로 메타데이터를 읽는 스크립트는 깨집니다</b> — 먼저 CloudWatch 지표로 IMDSv1 사용량을 확인하세요.',
 'fix_cmd': '''# 0) 먼저 IMDSv1 을 실제로 쓰고 있는지 확인 (끊기면 서비스 장애)
$ aws cloudwatch get-metric-statistics --namespace AWS/EC2 \\
      --metric-name MetadataNoToken \\
      --dimensions Name=InstanceId,Value=i-0a3f72be91c4d5e80 \\
      --start-time 2026-09-07T00:00:00Z --end-time 2026-09-14T00:00:00Z \\
      --period 86400 --statistics Sum
# → Sum 이 0 이면 안전하게 전환 가능

# 1) IMDSv2 강제 + 홉 제한 1
$ aws ec2 modify-instance-metadata-options \\
      --instance-id i-0a3f72be91c4d5e80 \\
      --http-tokens required \\
      --http-put-response-hop-limit 1 \\
      --http-endpoint enabled

$ aws ec2 modify-instance-metadata-options \\
      --instance-id i-0c81d5fa27e93b146 \\
      --http-tokens required --http-put-response-hop-limit 1

# 2) 신규 인스턴스 기본값도 IMDSv2 로 (리전 단위)
$ aws ec2 modify-instance-metadata-defaults \\
      --http-tokens required --http-put-response-hop-limit 1''',
 'fix_out': '''$ aws ec2 describe-instances --query "Reservations[*].Instances[*].{ID:InstanceId,Tokens:MetadataOptions.HttpTokens,Hop:MetadataOptions.HttpPutResponseHopLimit}" --output table
--------------------------------------------------------------------
|            ID            |    Tokens     |          Hop          |
+--------------------------+---------------+-----------------------+
|  i-0a3f72be91c4d5e80     |  required     |  1                    |
|  i-0c81d5fa27e93b146     |  required     |  1                    |
|  i-04e7b9c3d85a1f602     |  required     |  1                    |
+--------------------------+---------------+-----------------------+

$ curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/fin-core-app-role
<?xml version="1.0" encoding="iso-8859-1"?>
<Error><Code>401 - Unauthorized</Code></Error>

$ TOKEN=$(curl -sX PUT "http://169.254.169.254/latest/api/token" \\
      -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
$ curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \\
      http://169.254.169.254/latest/meta-data/iam/security-credentials/
fin-core-app-role

→ 토큰 없는 IMDSv1 호출은 401 로 차단됩니다. SSRF 경로가 끊겼습니다.''',
 'iac': '''resource "aws_instance" "core_app" {
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"   # IMDSv2 강제
    http_put_response_hop_limit = 1            # 컨테이너에서 접근 차단
    instance_metadata_tags      = "disabled"
  }
}

# 시작 템플릿에도 반드시 — ASG 가 만드는 인스턴스가 새는 경로다
resource "aws_launch_template" "core_app" {
  metadata_options {
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }
}

# SCP 로 optional 인스턴스 생성 자체를 금지
# Deny ec2:RunInstances when ec2:MetadataHttpTokens != "required"''',
 'pitfall': '<b>주의</b> — 인스턴스만 고치고 <b>시작 템플릿(Launch Template)·AMI 를 놓치면</b> 오토스케일링이 만드는 새 인스턴스가 다시 <code>optional</code> 로 태어납니다. 이 항목의 재발률이 높은 이유입니다. 또한 <b>ECS on EC2 나 Kubernetes 파드</b>는 홉이 하나 더 필요해 <code>hop-limit=1</code> 로 바꾸면 태스크 역할이 깨질 수 있습니다 — 컨테이너 환경은 홉 2 를 유지하되 <b>파드 수준 자격증명(IRSA·태스크 역할)</b> 로 분리하는 것이 정석입니다.',
 'evidence': [
   '<code>metadata-options.http-tokens=optional</code> 필터 조회 결과 (대상 인스턴스 목록)',
   '전체 인스턴스의 HttpTokens·HopLimit 값',
   'CloudWatch <code>MetadataNoToken</code> 지표 (IMDSv1 실사용 여부)',
   '시작 템플릿·AMI 의 메타데이터 옵션 설정',
   '조치 후 토큰 없는 호출이 401 로 거부되는 검증 결과',
 ],
 'finance': 'IMDSv1 은 <b>애플리케이션 취약점 하나를 계정 장악으로 증폭</b>시키는 경로입니다. 금융권 웹 애플리케이션에서 SSRF 는 드물지 않고(이미지 프록시·웹훅·PDF 렌더러 등), 그 순간 인스턴스 역할의 모든 권한이 공격자에게 넘어갑니다. 전자금융감독규정의 <b>접근통제·권한 최소화</b> 요구가 애플리케이션 계층 하나로 무력화되는 것을 막는 항목이라, 위험도 5 가 부여됩니다.',
},

]
