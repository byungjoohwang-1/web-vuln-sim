# -*- coding: utf-8 -*-
"""금융권 클라우드 관리체계 평가기준(PISM) — AWS 진단 실습 명세 2차.

1차(specs_fincloud.py)가 위험도 5 의 대표 항목이라면, 이쪽은 암호화 기본값·자격증명 수명주기·
권한 과다·미사용 자원처럼 **운영 중에 조용히 어긋나는** 항목들이다.
계정·리전·리소스 ID 체계는 1차와 동일하게 유지한다(382011749265 / ap-northeast-2).
"""

SPECS = [

# ── PISM-030 EBS 기본 암호화 ─────────────────────────────────────────────
{
 'file': '07_fincloud-pism030.html', 'pism': 'PISM-030', 'risk': '3',
 'title': '디스크 볼륨 생성 시 암호화 설정 여부', 'svc': 'EC2 · EBS',
 'area': '5. 운영 관리', 'ctrl': '5.3 정보처리시스템 보호대책',
 'detail': '디스크 볼륨 암호화 설정이 비활성화되어 있는 경우 새로 생성되는 볼륨이 암호화 미적용 상태로 생성되어 중요 정보가 유출될 위협이 존재하므로, 디스크 볼륨 생성 시 암호화 적용 설정의 활성화 여부를 점검합니다.',
 'console_path': '<b>EC2</b> → <b>설정</b> → <b>EBS 암호화</b> → <b>새 EBS 볼륨을 항상 암호화</b> 설정 확인',
 'cmds': [
   {'label': '① 계정·리전 기본 암호화 설정 (평가기준 명시 명령)', 'cmd': 'aws ec2 get-ebs-encryption-by-default',
    'out': '{\n    "EbsEncryptionByDefault": <span class="er">false</span>\n}'},
   {'label': '② 기본 KMS 키 확인', 'cmd': 'aws ec2 get-ebs-default-kms-key-id',
    'out': '''{
    "KmsKeyId": "<span class="er">alias/aws/ebs</span>"
}

<span class="dim">서비스 기본키입니다 — 키 정책·교체 주기를 우리가 통제할 수 없습니다.</span>'''},
   {'label': '③ 다른 리전도 확인 (설정은 리전별입니다)', 'cmd': 'aws ec2 get-ebs-encryption-by-default --region us-east-1',
    'out': '''{
    "EbsEncryptionByDefault": <span class="er">false</span>
}

<span class="er">※ 기본 암호화는 리전마다 따로 켜야 합니다. 한 리전만 켜고 끝내는 실수가 잦습니다.</span>'''},
 ],
 'answer': 'bad',
 'why': '''<b>기본 암호화가 꺼져 있어 앞으로 만드는 모든 볼륨이 평문으로 생성됩니다.</b>
<div class="ev">EbsEncryptionByDefault = false  → 신규 볼륨·스냅샷 복원·ASG 확장 시 전부 평문
KmsKeyId = alias/aws/ebs        → 켜더라도 서비스 기본키라 키 통제가 불가
us-east-1 도 false              → <b>리전별 설정</b>이라 한 곳만 켜면 나머지가 샌다</div>
PISM-031(볼륨 암호화)을 아무리 고쳐도 <b>이 설정이 꺼져 있으면 재발합니다.</b> 두 항목은 반드시 함께 처리해야 합니다.''',
 'fix_intro': '기본 암호화를 켜고, 기본 키를 <b>고객관리형 키(CMK)</b> 로 바꿉니다. 이 설정은 <b>계정 × 리전</b> 단위이므로 사용하는 모든 리전에 적용해야 합니다.',
 'fix_cmd': '''# 1) 전용 CMK 생성 (자동 교체 활성화)
$ aws kms create-key --description "fin EBS volume encryption" \\
      --key-usage ENCRYPT_DECRYPT --origin AWS_KMS
$ aws kms create-alias --alias-name alias/fin-ebs-cmk \\
      --target-key-id 7c41f9a3-2e58-4b06-91da-3f7b25ce8410
$ aws kms enable-key-rotation --key-id alias/fin-ebs-cmk

# 2) 기본 암호화 활성화 + 기본 키 지정
$ aws ec2 enable-ebs-encryption-by-default
$ aws ec2 modify-ebs-default-kms-key-id --kms-key-id alias/fin-ebs-cmk

# 3) 사용 중인 모든 리전에 반복
$ for R in ap-northeast-2 us-east-1 ap-southeast-1; do
      aws ec2 enable-ebs-encryption-by-default --region $R
  done''',
 'fix_out': '''$ for R in ap-northeast-2 us-east-1 ap-southeast-1; do
      echo -n "$R: "; aws ec2 get-ebs-encryption-by-default --region $R --query EbsEncryptionByDefault
  done
ap-northeast-2: true
us-east-1: true
ap-southeast-1: true

$ aws ec2 get-ebs-default-kms-key-id
{
    "KmsKeyId": "arn:aws:kms:ap-northeast-2:382011749265:key/7c41f9a3-2e58-4b06-91da-3f7b25ce8410"
}

→ 전 리전 기본 암호화 활성 + 고객관리형 키 적용.''',
 'iac': '''# 리전마다 provider alias 를 두고 각각 적용한다
resource "aws_ebs_encryption_by_default" "seoul" { enabled = true }
resource "aws_ebs_default_kms_key" "seoul"       { key_arn = aws_kms_key.fin_ebs.arn }

resource "aws_kms_key" "fin_ebs" {
  description         = "fin EBS volume encryption"
  enable_key_rotation = true          # 연 1회 자동 교체
  deletion_window_in_days = 30
}

# 되돌림 방지 — SCP 로 비활성화 API 자체를 금지
# Deny ec2:DisableEbsEncryptionByDefault''',
 'pitfall': '<b>주의</b> — 기본 암호화를 켜도 <b>기존 볼륨은 그대로</b>이고, <b>미암호화 스냅샷으로부터의 복원</b>은 실패하지 않고 조용히 암호화되어 생성됩니다(의도된 동작). 반대로 <b>다른 계정과 AMI 를 공유</b>할 때 CMK 로 암호화된 스냅샷은 키 공유 설정이 없으면 상대가 못 씁니다 — 재해복구용 크로스계정 복제가 있다면 키 정책에 해당 계정을 먼저 허용해야 합니다.',
 'evidence': [
   '사용 중인 <b>모든 리전</b>의 <code>get-ebs-encryption-by-default</code> 출력',
   '<code>get-ebs-default-kms-key-id</code> 출력 (고객관리형 키 여부)',
   'KMS 키의 자동 교체 활성화 및 키 정책',
   'PISM-031(기존 볼륨) 조치 계획과의 연계 문서',
 ],
 'finance': '금융회사의 클라우드 이용은 <b>중요정보의 암호화 저장</b>을 전제로 승인됩니다. 기본값이 꺼져 있으면 개별 담당자의 실수 한 번이 곧 평문 볼륨이 되므로, 평가에서는 <b>"사람이 기억해야 하는 통제"를 감점 요인</b>으로 봅니다. 기본값으로 강제하는 것이 정석입니다.',
},

# ── PISM-032 스냅샷 암호화 ───────────────────────────────────────────────
{
 'file': '07_fincloud-pism032.html', 'pism': 'PISM-032', 'risk': '5',
 'title': '스냅샷 암호화 적용 여부', 'svc': 'EC2 · EBS',
 'area': '5. 운영 관리', 'ctrl': '5.3 정보처리시스템 보호대책',
 'detail': '스냅샷이 암호화되지 않은 경우 타 계정 또는 비인가자에 의해 복원되어 저장된 데이터가 유출될 수 있는 위협이 존재하므로, 스냅샷의 암호화 적용 여부를 점검합니다.',
 'console_path': '<b>EC2</b> → <b>스냅샷</b> → 대상 스냅샷 ID 클릭 → <b>암호화</b> 항목 확인. 공유 여부는 <b>권한 공유</b> 탭에서 확인',
 'cmds': [
   {'label': '① 스냅샷별 암호화 현황 (평가기준 명시 명령)', 'cmd': 'aws ec2 describe-snapshots --owner-ids self --query "Snapshots[*].{ID:SnapshotId,Encrypted:Encrypted}" --output table',
    'out': '''----------------------------------------------
|              DescribeSnapshots             |
+---------------------------+----------------+
|            ID             |   Encrypted    |
+---------------------------+----------------+
|  snap-0c73b19e58af2d640   |  <span class="er">False</span>         |
|  snap-0e81d47a2cb935f06   |  True          |
|  snap-04f9a7c31b6e28d05   |  <span class="er">False</span>         |
+---------------------------+----------------+'''},
   {'label': '② 스냅샷이 외부에 공유되어 있는지 확인', 'cmd': 'aws ec2 describe-snapshot-attribute --snapshot-id snap-0c73b19e58af2d640 --attribute createVolumePermission',
    'out': '''{
    "SnapshotId": "snap-0c73b19e58af2d640",
    "CreateVolumePermissions": [
        {"Group": "<span class="er">all</span>"}
    ]
}

<span class="er">※ Group: all — 이 스냅샷은 전 세계 모든 AWS 계정에 공개되어 있습니다.</span>'''},
   {'label': '③ 이 스냅샷의 출처 볼륨 확인', 'cmd': 'aws ec2 describe-snapshots --snapshot-ids snap-0c73b19e58af2d640 --query "Snapshots[*].{Vol:VolumeId,Size:VolumeSize,Desc:Description,Time:StartTime}"',
    'out': '''[
    {
        "Vol": "vol-08b3e7d1a95c24f70",
        "Size": 200,
        "Desc": "<span class="er">pre-encryption fin-core-app-01</span>",
        "Time": "2026-06-19T03:22:47+00:00"
    }
]

<span class="er">※ 코어뱅킹 앱 서버의 평문 스냅샷이 퍼블릭으로 열려 있습니다.</span>'''},
 ],
 'answer': 'bad',
 'why': '''평문 스냅샷이 <b>퍼블릭으로 공유</b>되어 있습니다. 이 조합은 사실상 데이터 공개입니다.
<div class="ev">snap-0c73b19e58af2d640 : Encrypted=False + <b>Group: all</b>
   → 아무 AWS 계정에서나 이 스냅샷으로 볼륨을 만들어 내용을 읽을 수 있음
   → 출처가 fin-core-app-01 (코어뱅킹 앱 서버) 의 200GB 루트 볼륨</div>
<b>암호화 스냅샷은 퍼블릭 공유가 불가능</b>합니다(AWS 가 막습니다). 즉 이 사고는 <b>평문이었기 때문에 가능</b>했던 것이고, 암호화가 곧 공유 사고의 방어선이기도 합니다.''',
 'fix_intro': '<b>공유부터 즉시 해제</b>한 뒤 암호화 사본을 만들고 평문 원본을 폐기합니다. 순서를 바꾸면 노출 시간이 길어집니다.',
 'fix_cmd': '''# 1) 즉시 — 퍼블릭 공유 해제
$ aws ec2 modify-snapshot-attribute --snapshot-id snap-0c73b19e58af2d640 \\
      --attribute createVolumePermission --operation-type remove --group-names all

# 2) 암호화 사본 생성
$ aws ec2 copy-snapshot --source-region ap-northeast-2 \\
      --source-snapshot-id snap-0c73b19e58af2d640 \\
      --encrypted --kms-key-id alias/fin-ebs-cmk \\
      --description "encrypted copy of fin-core-app-01"

# 3) 평문 원본 삭제
$ aws ec2 delete-snapshot --snapshot-id snap-0c73b19e58af2d640

# 4) 재발 방지 — 퍼블릭 스냅샷 차단(계정·리전 단위)
$ aws ec2 enable-snapshot-block-public-access --state block-all-sharing''',
 'fix_out': '''$ aws ec2 get-snapshot-block-public-access-state
{
    "State": "block-all-sharing"
}

$ aws ec2 describe-snapshots --owner-ids self --query "Snapshots[?Encrypted==\\`false\\`].SnapshotId"
[]

$ aws ec2 describe-snapshots --owner-ids self --query "Snapshots[*].{ID:SnapshotId,Encrypted:Encrypted}" --output table
+---------------------------+----------------+
|  snap-0e81d47a2cb935f06   |  True          |
|  snap-0b26d38fa71c945e2   |  True          |
+---------------------------+----------------+

→ 평문 스냅샷 0건, 퍼블릭 공유 차단 활성화.''',
 'iac': '''# 계정 차원에서 스냅샷 퍼블릭 공유를 원천 차단
resource "aws_ebs_snapshot_block_public_access" "this" {
  state = "block-all-sharing"
}

# 자동 스냅샷도 암호화되도록 — DLM 수명주기 정책
resource "aws_dlm_lifecycle_policy" "daily" {
  policy_details {
    schedule {
      name = "daily-encrypted"
      create_rule { interval = 24 interval_unit = "HOURS" times = ["18:00"] }
      retain_rule { count = 30 }
      # 원본 볼륨이 암호화면 스냅샷도 자동 암호화된다
    }
    target_tags = { Backup = "true" }
  }
}''',
 'pitfall': '<b>주의</b> — 퍼블릭 스냅샷은 <b>검색이 쉽습니다.</b> <code>describe-snapshots --restorable-by-user-ids all</code> 로 누구나 공개 스냅샷을 훑을 수 있어, 노출 시간이 짧아도 이미 복제되었다고 가정해야 합니다. 공유 해제 후에는 <b>해당 볼륨의 자격증명·키를 모두 교체</b>하세요. 또한 <b>특정 계정에만 공유</b>(<code>--user-ids</code>)한 경우도 점검 대상입니다 — <code>Group: all</code> 만 보면 놓칩니다.',
 'evidence': [
   '<code>describe-snapshots --owner-ids self</code> 전체 출력 (Encrypted)',
   '스냅샷별 <code>createVolumePermission</code> (퍼블릭·특정 계정 공유 여부)',
   '<code>get-snapshot-block-public-access-state</code> 출력',
   '평문·공유 스냅샷의 폐기 내역 및 노출 기간 산정',
 ],
 'finance': '스냅샷은 <b>디스크 전체의 완전한 사본</b>입니다. 접근통제·망분리를 아무리 갖춰도 스냅샷 하나가 공개되면 그 시점의 데이터 전부가 나갑니다. 실제 해외 금융·핀테크 유출 사고 중 상당수가 <b>백업·스냅샷의 잘못된 공유</b>에서 비롯됐고, 그래서 이 항목에 위험도 5 가 부여됩니다.',
},

# ── PISM-033 AMI 암호화 ──────────────────────────────────────────────────
{
 'file': '07_fincloud-pism033.html', 'pism': 'PISM-033', 'risk': '5',
 'title': '이미지 암호화 적용 여부', 'svc': 'EC2 · AMI',
 'area': '5. 운영 관리', 'ctrl': '5.3 정보처리시스템 보호대책',
 'detail': '이미지가 암호화되지 않은 경우 해당 이미지를 기반으로 생성되는 인스턴스 또는 디스크에 포함된 데이터가 비인가자에게 노출될 수 있는 위협이 존재하므로, 이미지의 암호화 적용 여부를 점검합니다.',
 'console_path': '<b>EC2</b> → <b>AMI</b> → 대상 AMI ID 클릭 → <b>스토리지</b> 탭 → 블록 디바이스의 <b>암호화됨</b> 열 확인',
 'cmds': [
   {'label': '① 보유 AMI 목록', 'cmd': 'aws ec2 describe-images --owners self --query "Images[*].{ID:ImageId,Name:Name,Public:Public}" --output table',
    'out': '''----------------------------------------------------------------------------
|                              DescribeImages                              |
+------------------------+--------------------------------+---------------+
|           ID           |              Name              |    Public     |
+------------------------+--------------------------------+---------------+
|  ami-0b41f7d29ca85e630 |  fin-core-app-golden-2026-08   |  <span class="er">True</span>         |
|  ami-07c2a9e51db384f06 |  fin-batch-worker-2026-09      |  False        |
+------------------------+--------------------------------+---------------+'''},
   {'label': '② AMI 에 매핑된 스냅샷 확인 (평가기준 명시 명령)', 'cmd': 'aws ec2 describe-images --image-ids ami-0b41f7d29ca85e630 --query "Images[0].BlockDeviceMappings[*].Ebs.SnapshotId" --output text',
    'out': 'snap-04f9a7c31b6e28d05'},
   {'label': '③ 그 스냅샷의 암호화 여부 확인', 'cmd': 'aws ec2 describe-snapshots --snapshot-ids snap-04f9a7c31b6e28d05 --query "Snapshots[*].Encrypted" --output text',
    'out': '<span class="er">False</span>\n\n<span class="er">※ 퍼블릭 AMI 의 기반 스냅샷이 평문입니다.</span>'},
   {'label': '④ 이미지 안에 무엇이 들어 있었나', 'cmd': 'aws ec2 describe-images --image-ids ami-0b41f7d29ca85e630 --query "Images[0].{Desc:Description,Created:CreationDate}"',
    'out': '''{
    "Desc": "<span class="er">golden image w/ app config, includes /opt/fin/app.properties</span>",
    "Created": "2026-08-14T05:31:09.000Z"
}

<span class="dim">골든 이미지에는 대개 설정 파일·인증서·에이전트 키가 함께 구워져 있습니다.</span>'''},
 ],
 'answer': 'bad',
 'why': '''<b>평문 AMI 가 퍼블릭으로 공개</b>되어 있습니다. AMI 는 스냅샷의 포장지일 뿐이라, 판정은 <b>기반 스냅샷의 암호화 여부</b>로 내립니다.
<div class="ev">ami-0b41f7d29ca85e630 : Public = <b>True</b>
  └ snap-04f9a7c31b6e28d05 : Encrypted = <b>False</b>
     └ 내용: 앱 설정 파일(/opt/fin/app.properties) 포함된 골든 이미지</div>
골든 이미지에는 <b>DB 접속 문자열·API 키·에이전트 인증서</b>가 함께 구워지는 경우가 많습니다. 이미지 공개는 그 전부를 공개하는 것과 같습니다.''',
 'fix_intro': '<b>공개 해제 → 암호화 AMI 재생성 → 평문 AMI/스냅샷 폐기</b> 순서로 처리하고, 이미지에 구워진 <b>비밀값을 전부 교체</b>합니다. 공개된 이미지는 이미 복제되었다고 보아야 합니다.',
 'fix_cmd': '''# 1) 즉시 — AMI 공개 해제
$ aws ec2 modify-image-attribute --image-id ami-0b41f7d29ca85e630 \\
      --launch-permission "Remove=[{Group=all}]"

# 2) 암호화된 AMI 로 재생성 (copy-image 로 한 번에)
$ aws ec2 copy-image --source-region ap-northeast-2 \\
      --source-image-id ami-0b41f7d29ca85e630 \\
      --name "fin-core-app-golden-2026-09-enc" \\
      --encrypted --kms-key-id alias/fin-ebs-cmk

# 3) 평문 AMI 등록 해제 + 스냅샷 삭제
$ aws ec2 deregister-image --image-id ami-0b41f7d29ca85e630
$ aws ec2 delete-snapshot --snapshot-id snap-04f9a7c31b6e28d05

# 4) 이미지에 구워져 있던 비밀값 교체 (필수)
$ aws secretsmanager update-secret --secret-id fin/core/db-password \\
      --secret-string "$(openssl rand -base64 32)"

# 5) 재발 방지 — 퍼블릭 이미지 차단
$ aws ec2 disable-image-block-public-access --dry-run   # 현재 상태 확인용
$ aws ec2 enable-image-block-public-access --image-block-public-access-state block-new-sharing''',
 'fix_out': '''$ aws ec2 get-image-block-public-access-state
{
    "ImageBlockPublicAccessState": "block-new-sharing"
}

$ aws ec2 describe-images --owners self --query "Images[*].{ID:ImageId,Public:Public}" --output table
+------------------------+---------------+
|  ami-0d83f61c74be9a250 |  False        |
|  ami-07c2a9e51db384f06 |  False        |
+------------------------+---------------+

$ aws ec2 describe-images --owners self --query "Images[*].BlockDeviceMappings[*].Ebs.SnapshotId" --output text \\
  | xargs -n1 -I{} aws ec2 describe-snapshots --snapshot-ids {} --query "Snapshots[0].Encrypted" --output text
True
True

→ 공개 AMI 0건, 기반 스냅샷 전부 암호화.''',
 'iac': '''resource "aws_ec2_image_block_public_access" "this" {
  state = "block-new-sharing"
}

# 골든 이미지는 파이프라인에서 암호화로 굽는다
resource "aws_imagebuilder_distribution_configuration" "fin" {
  distribution {
    region = "ap-northeast-2"
    ami_distribution_configuration {
      name       = "fin-core-app-{{ imagebuilder:buildDate }}"
      kms_key_id = aws_kms_key.fin_ebs.arn
      # launch_permission 을 지정하지 않으면 비공개가 기본
    }
  }
}''',
 'pitfall': '<b>주의</b> — <code>deregister-image</code> 만 하면 <b>기반 스냅샷은 그대로 남습니다.</b> AMI 는 사라진 것처럼 보이지만 스냅샷을 통해 데이터는 여전히 접근 가능합니다. 반드시 스냅샷까지 지우세요. 그리고 <b>공개되었던 이미지의 비밀값 교체는 선택이 아니라 필수</b>입니다 — 이미지를 내린다고 이미 복사해 간 사본이 사라지지 않습니다.',
 'evidence': [
   '<code>describe-images --owners self</code> 출력 (Public 여부)',
   'AMI 별 기반 스냅샷 ID 와 그 <code>Encrypted</code> 값',
   '<code>get-image-block-public-access-state</code> 출력',
   '공개 이력이 있는 이미지의 노출 기간 및 비밀값 교체 기록',
   '평문 AMI 등록 해제·스냅샷 삭제 내역',
 ],
 'finance': 'AMI 는 <b>서버 한 대를 통째로 복제</b>할 수 있는 자산입니다. 금융권 골든 이미지에는 보안 에이전트 설정, 내부 CA 인증서, 초기 접속 정보가 포함되는 일이 흔해, 공개 시 <b>내부망 구조가 함께 노출</b>됩니다. 암호화는 그 자체로 퍼블릭 공유를 불가능하게 만들어 이중 방어선이 됩니다.',
},

# ── PISM-025 EoS 런타임 ──────────────────────────────────────────────────
{
 'file': '07_fincloud-pism025.html', 'pism': 'PISM-025', 'risk': '5',
 'title': '서비스 지원이 종료된(EoS) 런타임 교체 여부', 'svc': 'Lambda',
 'area': '5. 운영 관리', 'ctrl': '5.3 정보처리시스템 보호대책',
 'detail': '서비스 지원이 종료된(EoS) 버전을 사용하는 경우, 알려진 취약점 또는 신규로 발견되는 취약점으로부터 발생하는 보안위협에 대처할 수 없는 위협이 존재하므로 서비스 지원이 종료된 버전의 런타임 사용 여부를 점검합니다. ※ 런타임 교체 계획을 수립하고 보고를 마친 경우 취약으로 반영하고 위험수용으로 관리합니다.',
 'console_path': '<b>Lambda</b> → <b>함수</b> → 대상 함수 선택 → <b>코드</b> → <b>런타임 설정</b>에서 런타임 버전 확인',
 'cmds': [
   {'label': '① 함수별 런타임 확인 (평가기준 명시 명령)', 'cmd': 'aws lambda list-functions --query "Functions[*].{Name:FunctionName,Runtime:Runtime,Modified:LastModified}" --output table',
    'out': '''--------------------------------------------------------------------------------------
|                                   ListFunctions                                    |
+---------------------------------+---------------+----------------------------------+
|              Name               |    Runtime    |            Modified              |
+---------------------------------+---------------+----------------------------------+
|  fin-settlement-batch           |  <span class="er">python3.8</span>    |  2024-05-17T08:22:41.000+0000    |
|  fin-openbanking-token-refresh  |  python3.12   |  2026-08-02T11:09:33.000+0000    |
|  fin-fds-scoring                |  <span class="er">nodejs16.x</span>   |  2025-02-28T16:40:12.000+0000    |
+---------------------------------+---------------+----------------------------------+'''},
   {'label': '② 런타임별 지원 상태 조회', 'cmd': 'aws lambda get-function-configuration --function-name fin-settlement-batch --query "{Runtime:Runtime,State:State,LastUpdateStatus:LastUpdateStatus}"',
    'out': '''{
    "Runtime": "python3.8",
    "State": "Active",
    "LastUpdateStatus": "Successful"
}

<span class="dim">CLI 는 EoS 여부를 알려주지 않습니다 — AWS 런타임 지원 정책 문서와 대조해야 합니다.</span>
<span class="er">python3.8  : 지원 종료 (보안 패치 없음)
nodejs16.x : 지원 종료 (보안 패치 없음)</span>'''},
   {'label': '③ 지원 종료 알림이 와 있는지 확인', 'cmd': 'aws support describe-cases --include-resolved-cases --query "cases[?contains(subject, \'runtime\')].[subject,timeCreated]" --output table',
    'out': '''--------------------------------------------------------------------------------
|  [Action Required] AWS Lambda end of support for Python 3.8  |  2025-09-01  |
|  [Action Required] AWS Lambda end of support for Node.js 16  |  2025-04-14  |
--------------------------------------------------------------------------------

<span class="er">※ 1년 이상 전에 통지를 받고도 교체되지 않았습니다.</span>'''},
 ],
 'answer': 'bad',
 'why': '''3개 중 <b>2개가 지원 종료 런타임</b>입니다.
<div class="ev">fin-settlement-batch  : python3.8   → EoS, 마지막 수정 2024-05 (2년 이상 방치)
fin-fds-scoring       : nodejs16.x  → EoS, FDS 점수 산정 = 이상거래탐지 핵심 로직
fin-openbanking-token : python3.12  → 지원 중, 양호</div>
EoS 런타임은 <b>새 취약점이 나와도 패치가 오지 않습니다.</b> 함수가 정상 동작하는 것과 안전한 것은 다릅니다. 평가기준은 교체 계획을 세우고 보고를 마친 경우에도 <b>취약으로 반영하고 위험수용으로 관리</b>하도록 명시합니다 — 즉 계획만으로는 양호가 되지 않습니다.''',
 'fix_intro': '런타임을 올리는 것은 <b>코드 호환성 작업</b>을 동반합니다. 별칭(alias)과 가중치 라우팅으로 <b>점진 전환</b>하는 것이 금융 서비스에서의 안전한 방식입니다.',
 'fix_cmd': '''# 1) 새 버전을 최신 런타임으로 배포 (코드 수정 후)
$ aws lambda update-function-configuration \\
      --function-name fin-settlement-batch --runtime python3.12
$ aws lambda publish-version --function-name fin-settlement-batch
# → Version: 14

# 2) 별칭에 가중치를 줘 10% 만 새 버전으로 흘린다
$ aws lambda update-alias --function-name fin-settlement-batch \\
      --name prod --function-version 13 \\
      --routing-config '{"AdditionalVersionWeights":{"14":0.1}}'

# 3) 오류율 확인 후 100% 전환
$ aws cloudwatch get-metric-statistics --namespace AWS/Lambda \\
      --metric-name Errors --dimensions Name=FunctionName,Value=fin-settlement-batch \\
      --start-time 2026-09-14T00:00:00Z --end-time 2026-09-14T06:00:00Z \\
      --period 3600 --statistics Sum
$ aws lambda update-alias --function-name fin-settlement-batch \\
      --name prod --function-version 14 --routing-config '{}'

# 4) FDS 함수도 동일 절차 (nodejs16.x → nodejs22.x)''',
 'fix_out': '''$ aws lambda list-functions --query "Functions[*].{Name:FunctionName,Runtime:Runtime}" --output table
+---------------------------------+---------------+
|  fin-settlement-batch           |  python3.12   |
|  fin-openbanking-token-refresh  |  python3.12   |
|  fin-fds-scoring                |  nodejs22.x   |
+---------------------------------+---------------+

→ 지원 종료 런타임 0건.''',
 'iac': '''# 런타임을 변수로 빼고 분기마다 갱신 — 코드 리뷰에 걸리게 만든다
variable "python_runtime" { default = "python3.12" }

resource "aws_lambda_function" "settlement" {
  function_name = "fin-settlement-batch"
  runtime       = var.python_runtime
  publish       = true
}

resource "aws_lambda_alias" "prod" {
  name             = "prod"
  function_name    = aws_lambda_function.settlement.function_name
  function_version = aws_lambda_function.settlement.version
}''',
 'pitfall': '<b>주의</b> — AWS 는 EoS 런타임의 <b>함수 생성은 막지만 기존 함수의 호출은 계속 허용</b>합니다. 그래서 "아직 잘 돈다"며 방치되기 쉽습니다. 또한 런타임을 올리면 <b>의존 라이브러리와 Lambda 레이어도 함께</b> 맞춰야 합니다 — 레이어가 구버전 런타임용으로 빌드되어 있으면 배포는 성공하고 <b>런타임에 실패</b>합니다. 반드시 스테이징에서 실행까지 확인하세요.',
 'evidence': [
   '전체 함수의 런타임 목록 (<code>list-functions</code>)',
   'AWS 런타임 지원 정책과 대조한 EoS 판정표',
   '교체 계획서 (대상·일정·담당) 및 경영진 보고 증적',
   '전환 후 런타임 목록 및 오류율 지표',
 ],
 'finance': 'EoS 런타임은 <b>알려진 취약점에 무방비</b>라는 뜻입니다. 특히 정산 배치·FDS 점수 산정처럼 <b>금전과 직결된 로직</b>이 지원 종료 런타임 위에서 돌고 있다면, 취약점 하나가 거래 무결성에 영향을 줄 수 있습니다. 평가기준이 "계획 수립 후에도 취약으로 반영"하도록 한 것은 <b>실제 교체 전까지 위험이 그대로</b>이기 때문입니다.',
},

# ── PISM-060 Lambda 코드 서명 ────────────────────────────────────────────
{
 'file': '07_fincloud-pism060.html', 'pism': 'PISM-060', 'risk': '5',
 'title': '실행 코드 무결성 검증 절차 운용 여부', 'svc': 'Lambda',
 'kind': '기술적 보안',
 'area': '7. IT도입･개발･유지보수 관리', 'ctrl': '7.5 프로그램 통제절차 수립',
 'detail': '인가되지 않은 실행 코드가 포함되지 않도록, 서명 기능을 활용한 가상자원 실행 코드의 무결성 검증 절차를 구축하여 운용하고 있는지 점검합니다.',
 'console_path': '<b>Lambda</b> → <b>함수</b> → 대상 함수 선택 → <b>구성</b> → <b>코드 서명</b>에서 코드 서명 구성 확인',
 'cmds': [
   {'label': '① 함수의 코드 서명 구성 확인 (평가기준 명시 명령)', 'cmd': 'aws lambda get-function-code-signing-config --function-name fin-settlement-batch',
    'out': '''{
    "CodeSigningConfigArn": <span class="er">null</span>,
    "FunctionName": "fin-settlement-batch"
}

<span class="er">※ 코드 서명 구성이 연결되어 있지 않습니다.</span>'''},
   {'label': '② 계정에 서명 프로파일이 있는지 확인', 'cmd': 'aws signer list-signing-profiles --query "profiles[*].{Name:profileName,Status:status,Platform:platformId}" --output table',
    'out': '''<span class="dim">{
    "profiles": []
}</span>

<span class="er">※ AWS Signer 서명 프로파일이 하나도 없습니다 — 서명 체계 자체가 미구축.</span>'''},
   {'label': '③ 누가 코드를 배포할 수 있는가', 'cmd': 'aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::382011749265:role/fin-developer --action-names lambda:UpdateFunctionCode --query "EvaluationResults[*].EvalDecision" --output text',
    'out': '''<span class="er">allowed</span>

<span class="er">※ 개발자 역할이 검증 절차 없이 운영 함수 코드를 직접 교체할 수 있습니다.</span>'''},
 ],
 'answer': 'bad',
 'why': '''<b>코드 서명 체계가 전혀 없습니다.</b>
<div class="ev">CodeSigningConfigArn : null → 함수에 서명 검증이 걸려 있지 않음
Signer 프로파일      : 0개  → 서명할 수단 자체가 없음
fin-developer        : UpdateFunctionCode <b>allowed</b>
   → 코드 리뷰·파이프라인을 우회해 <b>개발자 PC 에서 바로 운영 배포</b>가 가능</div>
이 상태에서는 "누가 무엇을 배포했는가"를 CloudTrail 로 사후에 알 수는 있어도, <b>인가되지 않은 코드가 올라가는 것을 막지는 못합니다.</b> 평가기준이 요구하는 것은 사후 추적이 아니라 <b>사전 검증 절차</b>입니다.''',
 'fix_intro': 'AWS Signer 로 <b>서명 프로파일</b>을 만들고, <b>코드 서명 구성</b>을 함수에 연결해 서명되지 않은 코드의 배포를 <b>거부</b>하도록 합니다. 정책을 <code>Warn</code> 이 아니라 <code>Enforce</code> 로 두는 것이 핵심입니다.',
 'fix_cmd': '''# 1) 서명 프로파일 생성
$ aws signer put-signing-profile --profile-name FinLambdaSigner \\
      --platform-id AWSLambda-SHA384-ECDSA \\
      --signature-validity-period 'value=12,type=MONTHS'

# 2) 코드 서명 구성 — 미서명/만료 시 배포 거부
$ aws lambda create-code-signing-config \\
      --description "fin prod lambda signing" \\
      --allowed-publishers SigningProfileVersionArns=\\
"arn:aws:signer:ap-northeast-2:382011749265:/signing-profiles/FinLambdaSigner/9tKpQ3mZ" \\
      --code-signing-policies UntrustedArtifactOnDeployment=<span class="hl">Enforce</span>
# → CodeSigningConfigArn: arn:aws:lambda:ap-northeast-2:382011749265:code-signing-config:csc-0a71f

# 3) 함수에 연결
$ aws lambda put-function-code-signing-config \\
      --function-name fin-settlement-batch \\
      --code-signing-config-arn arn:aws:lambda:ap-northeast-2:382011749265:code-signing-config:csc-0a71f

# 4) 개발자 역할에서 직접 배포 권한 회수 — 파이프라인 역할만 허용
$ aws iam put-role-policy --role-name fin-developer \\
      --policy-name deny-direct-deploy --policy-document '{
        "Version":"2012-10-17",
        "Statement":[{"Effect":"Deny",
          "Action":["lambda:UpdateFunctionCode","lambda:UpdateFunctionConfiguration"],
          "Resource":"*"}]}\'''',
 'fix_out': '''$ aws lambda get-function-code-signing-config --function-name fin-settlement-batch
{
    "CodeSigningConfigArn": "arn:aws:lambda:ap-northeast-2:382011749265:code-signing-config:csc-0a71f",
    "FunctionName": "fin-settlement-batch"
}

$ aws lambda update-function-code --function-name fin-settlement-batch \\
      --zip-file fileb://unsigned.zip

An error occurred (InvalidParameterValueException) when calling the UpdateFunctionCode operation:
<span class="hl">Lambda cannot deploy the function. The function or layer might be signed using
a signing profile that isn't allowed, or the code signature is missing.</span>

→ 서명되지 않은 코드의 배포가 거부됩니다.''',
 'iac': '''resource "aws_signer_signing_profile" "lambda" {
  platform_id = "AWSLambda-SHA384-ECDSA"
  name_prefix = "FinLambdaSigner"
  signature_validity_period { value = 12 type = "MONTHS" }
}

resource "aws_lambda_code_signing_config" "prod" {
  allowed_publishers {
    signing_profile_version_arns = [aws_signer_signing_profile.lambda.version_arn]
  }
  policies { untrusted_artifact_on_deployment = "Enforce" }   # Warn 아님
}

resource "aws_lambda_function" "settlement" {
  code_signing_config_arn = aws_lambda_code_signing_config.prod.arn
}''',
 'pitfall': '<b>주의</b> — 코드 서명 정책의 기본값은 <code>Warn</code> 입니다. <b>Warn 은 경고만 남기고 배포를 허용</b>하므로 실질적 통제가 아닙니다. 반드시 <code>Enforce</code> 로 두세요. 또한 <b>Lambda 레이어도 서명 대상</b>입니다 — 함수만 서명하고 레이어를 놓치면 레이어 경유로 임의 코드가 들어옵니다. 컨테이너 이미지 기반 Lambda 는 Signer 가 아니라 <b>ECR 이미지 서명(Notation/Cosign)</b> 으로 별도 처리해야 합니다.',
 'evidence': [
   '함수별 <code>get-function-code-signing-config</code> 출력',
   '<code>get-code-signing-config</code> 의 <code>UntrustedArtifactOnDeployment</code> 값 (Enforce 여부)',
   'AWS Signer 서명 프로파일 및 유효기간',
   '미서명 코드 배포가 거부되는 검증 결과',
   '운영 배포 권한 보유 주체 목록 (파이프라인 역할로 한정되었는지)',
 ],
 'finance': '전자금융감독규정은 <b>프로그램 변경 통제</b>를 요구합니다 — 인가된 절차를 거친 코드만 운영에 반영되어야 합니다. 클라우드 서버리스 환경에서는 서버에 접속할 일이 없어 이 통제가 누락되기 쉬운데, <b>코드 서명이 그 자리를 대신</b>합니다. 정산·FDS 처럼 금전에 직접 영향을 주는 함수일수록 Enforce 가 필수입니다.',
},

# ── PISM-042 액세스 키 다중발급 ──────────────────────────────────────────
{
 'file': '07_fincloud-pism042.html', 'pism': 'PISM-042', 'risk': '3',
 'title': 'API 자격 증명 다중 발급 방지 여부', 'svc': 'IAM',
 'area': '6. 접근통제', 'ctrl': '6.1 계정 및 권한 관리',
 'detail': 'API 자격 증명(AWS Access Key 등)을 안전하게 관리하기 위해 API 자격 증명을 다중 보유한 식별자(계정, 애플리케이션 등) 존재 유무를 점검합니다.',
 'console_path': '<b>IAM</b> → <b>사용자</b> → 사용자 목록의 <b>액세스 키 ID</b> 컬럼 확인 (안 보이면 우측 상단 설정에서 활성화)',
 'cmds': [
   {'label': '① 자격증명 보고서 생성', 'cmd': 'aws iam generate-credential-report',
    'out': '{\n    "State": "COMPLETE"\n}'},
   {'label': '② 키 1·2 활성 여부 확인 (평가기준 명시 명령)', 'cmd': 'aws iam get-credential-report --query Content --output text | base64 -d | cut -d, -f1,9,14',
    'out': '''user,access_key_1_active,access_key_2_active
&lt;root_account&gt;,false,false
fin-admin-kim,true,<span class="er">true</span>
fin-dev-lee,true,false
fin-audit-readonly,false,false
fin-batch-svc,true,<span class="er">true</span>

<span class="er">※ fin-admin-kim, fin-batch-svc 가 키 2개를 동시에 보유하고 있습니다.</span>'''},
   {'label': '③ 두 키가 각각 쓰이고 있는지 확인', 'cmd': 'aws iam list-access-keys --user-name fin-batch-svc',
    'out': '''{
    "AccessKeyMetadata": [
        {
            "UserName": "fin-batch-svc",
            "AccessKeyId": "AKIA4XQ7N2VZP3MDQ8RT",
            "Status": "Active",
            "CreateDate": "2024-03-11T02:14:55+00:00"
        },
        {
            "UserName": "fin-batch-svc",
            "AccessKeyId": "AKIA4XQ7N2VZL9WFHC26",
            "Status": "Active",
            "CreateDate": "2026-02-20T09:47:31+00:00"
        }
    ]
}'''},
   {'label': '④ 각 키의 마지막 사용 시각', 'cmd': 'aws iam get-access-key-last-used --access-key-id AKIA4XQ7N2VZP3MDQ8RT --query "AccessKeyLastUsed"',
    'out': '''{
    "LastUsedDate": "<span class="er">2024-06-02T17:20:44+00:00</span>",
    "ServiceName": "s3",
    "Region": "ap-northeast-2"
}

<span class="er">※ 2년 넘게 사용되지 않은 키가 활성 상태로 남아 있습니다 — 교체 후 구 키를 안 지운 전형적 사례.</span>'''},
 ],
 'answer': 'bad',
 'why': '''두 계정이 <b>액세스 키를 2개씩 보유</b>하고 있고, 그중 하나는 <b>2년 넘게 미사용</b>입니다.
<div class="ev">fin-batch-svc
  AKIA...P3MDQ8RT : 2024-03 생성, <b>마지막 사용 2024-06</b> → 사실상 방치된 키
  AKIA...L9WFHC26 : 2026-02 생성, 현재 사용 중</div>
AWS 가 키 2개를 허용하는 이유는 <b>무중단 교체(rotate)</b> 때문입니다. 새 키를 만들고 → 애플리케이션을 전환하고 → <b>구 키를 삭제</b>하는 절차의 중간 상태여야 하는데, 마지막 단계를 빠뜨려 <b>영구히 2개</b>가 된 것입니다. 쓰이지 않는 키는 유출돼도 아무도 눈치채지 못합니다.''',
 'fix_intro': '<b>미사용 키를 비활성화한 뒤 삭제</b>합니다. 곧바로 지우지 않고 비활성화 단계를 두는 이유는, 저빈도 배치가 그 키를 쓰고 있을 가능성 때문입니다.',
 'fix_cmd': '''# 1) 미사용 키 비활성화 (되돌리기 쉬움)
$ aws iam update-access-key --user-name fin-batch-svc \\
      --access-key-id AKIA4XQ7N2VZP3MDQ8RT --status Inactive

# 2) 2~4주 관찰 후 삭제
$ aws iam delete-access-key --user-name fin-batch-svc \\
      --access-key-id AKIA4XQ7N2VZP3MDQ8RT

# 3) 근본 해결 — 서비스 계정의 키를 없앤다
#    EC2 배치라면 인스턴스 프로파일, EKS 라면 IRSA, 외부 CI 라면 OIDC 페더레이션
$ aws iam create-open-id-connect-provider \\
      --url https://token.actions.githubusercontent.com \\
      --client-id-list sts.amazonaws.com \\
      --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
# → GitHub Actions 가 장기 키 없이 역할을 맡는다''',
 'fix_out': '''$ aws iam get-credential-report --query Content --output text | base64 -d | cut -d, -f1,9,14
user,access_key_1_active,access_key_2_active
<root_account>,false,false
fin-admin-kim,true,false
fin-dev-lee,true,false
fin-audit-readonly,false,false
fin-batch-svc,true,false

→ 다중 보유 계정 0건. 각 식별자는 활성 키를 1개만 보유합니다.''',
 'iac': '''# 가장 좋은 조치는 "키를 만들지 않는 것"이다.
resource "aws_iam_role" "github_deploy" {
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Federated = aws_iam_openid_connect_provider.github.arn }
      Action    = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:sub" = "repo:fin-org/core:ref:refs/heads/main"
        }
      }
    }]
  })
}

# 장기 키 생성 자체를 조직에서 금지 — SCP
# Deny iam:CreateAccessKey (예외: 승인된 몇 개 계정만)''',
 'pitfall': '<b>주의</b> — <code>get-access-key-last-used</code> 의 <code>LastUsedDate</code> 가 <b>비어 있다고 해서 안 쓰는 키가 아닙니다.</b> AWS 는 2015년 이후 사용분만 기록하고, 일부 서비스는 기록이 지연됩니다. 그리고 <b>키를 지우기 전에 CloudTrail 로 최근 90일 호출을 교차 확인</b>하세요. 분기·연말 배치가 쓰는 키를 지워 결산이 멈추는 사고가 실제로 자주 납니다.',
 'evidence': [
   '자격증명 보고서의 <code>access_key_1_active</code> · <code>access_key_2_active</code> 컬럼',
   '다중 보유 계정별 <code>list-access-keys</code> 출력 (생성일)',
   '키별 <code>get-access-key-last-used</code> 결과',
   '비활성화·삭제 조치 내역 및 관찰 기간',
   '장기 키를 역할·OIDC 로 대체한 전환 내역',
 ],
 'finance': '액세스 키는 <b>만료되지 않는 자격증명</b>입니다. 금융권의 접근통제 원칙은 "필요한 사람에게, 필요한 기간만"인데 장기 키는 그 반대입니다. 다중 보유는 <b>교체 절차가 완결되지 않았다는 신호</b>이며, 방치된 키가 소스코드·설정 파일에 남아 유출되는 것이 실제 사고의 주된 경로입니다.',
},

# ── PISM-043 액세스 키 정기 갱신 ─────────────────────────────────────────
{
 'file': '07_fincloud-pism043.html', 'pism': 'PISM-043', 'risk': '3',
 'title': 'API 자격 증명의 정기적 갱신 이행 여부', 'svc': 'IAM',
 'area': '6. 접근통제', 'ctrl': '6.1 계정 및 권한 관리',
 'detail': 'API 자격 증명이 유출된 경우 악용될 위험을 줄이기 위해 API 자격 증명의 정기적 갱신 정책을 수립하고 이행 여부를 점검합니다.',
 'console_path': '<b>IAM</b> → <b>사용자</b> → 사용자 목록의 <b>활성 키 수명</b> 컬럼 확인 (안 보이면 우측 상단 설정에서 활성화)',
 'cmds': [
   {'label': '① 키 활성 여부와 마지막 교체일 (평가기준 명시 명령)', 'cmd': 'aws iam get-credential-report --query Content --output text | base64 -d | cut -d, -f1,9,10,14,15',
    'out': '''user,access_key_1_active,access_key_1_last_rotated,access_key_2_active,access_key_2_last_rotated
&lt;root_account&gt;,false,N/A,false,N/A
fin-admin-kim,true,<span class="er">2024-08-19T01:22:07+00:00</span>,false,N/A
fin-dev-lee,true,2026-07-30T05:11:44+00:00,false,N/A
fin-audit-readonly,false,N/A,false,N/A
fin-batch-svc,true,<span class="er">2024-03-11T02:14:55+00:00</span>,false,N/A'''},
   {'label': '② 90일 초과 키만 추려 보기', 'cmd': 'aws iam list-users --query "Users[*].UserName" --output text | tr \'\\t\' \'\\n\' | while read U; do aws iam list-access-keys --user-name $U --query "AccessKeyMetadata[?Status==\'Active\'].[UserName,AccessKeyId,CreateDate]" --output text; done',
    'out': '''fin-admin-kim   AKIA4XQ7N2VZB6TKRN39   <span class="er">2024-08-19T01:22:07+00:00</span>
fin-dev-lee     AKIA4XQ7N2VZQ2HGXD71   2026-07-30T05:11:44+00:00
fin-batch-svc   AKIA4XQ7N2VZL9WFHC26   <span class="er">2024-03-11T02:14:55+00:00</span>

<span class="dim">기준일 2026-09-14 → fin-admin-kim 약 25개월, fin-batch-svc 약 30개월 경과</span>'''},
   {'label': '③ 갱신 정책이 자동화되어 있는지 확인', 'cmd': 'aws configservice describe-config-rules --query "ConfigRules[?contains(ConfigRuleName, \'access-key\')].{Name:ConfigRuleName,State:ConfigRuleState}" --output table',
    'out': '''<span class="dim">{
    "ConfigRules": []
}</span>

<span class="er">※ access-keys-rotated 규칙이 없습니다 — 갱신 여부를 자동 점검하는 체계가 없습니다.</span>'''},
 ],
 'answer': 'bad',
 'why': '''<b>2개 키가 2년 이상 교체되지 않았고, 자동 점검 체계도 없습니다.</b>
<div class="ev">fin-admin-kim  : 2024-08 생성 → 약 <b>25개월</b> 경과 (관리자 권한 계정)
fin-batch-svc  : 2024-03 생성 → 약 <b>30개월</b> 경과
AWS Config 규칙: 없음 → 담당자가 수동으로 확인하지 않으면 아무도 모름</div>
평가기준은 "정책을 수립하고 <b>이행</b>하는지"를 봅니다. 정책 문서가 있어도 실제 키 수명이 2년이면 <b>미이행</b>입니다. 그리고 수동 점검에 의존하는 구조는 다음 평가에서 같은 지적을 반복하게 됩니다.''',
 'fix_intro': '키를 교체하되 <b>무중단 절차</b>를 지킵니다. 그리고 다음부터는 사람이 기억하지 않아도 되도록 <b>AWS Config 규칙으로 자동 탐지</b>합니다.',
 'fix_cmd': '''# 1) 무중단 교체 — 새 키 발급 → 앱 전환 → 구 키 비활성화 → 삭제
$ aws iam create-access-key --user-name fin-batch-svc
# → 새 키를 Secrets Manager 에 저장하고 앱이 참조하도록 전환
$ aws iam update-access-key --user-name fin-batch-svc \\
      --access-key-id AKIA4XQ7N2VZL9WFHC26 --status Inactive
# (관찰 후)
$ aws iam delete-access-key --user-name fin-batch-svc \\
      --access-key-id AKIA4XQ7N2VZL9WFHC26

# 2) 자동 탐지 — 90일 초과 키를 규정 위반으로 표시
$ aws configservice put-config-rule --config-rule '{
    "ConfigRuleName": "access-keys-rotated-90",
    "Source": {"Owner": "AWS", "SourceIdentifier": "ACCESS_KEYS_ROTATED"},
    "InputParameters": "{\\"maxAccessKeyAge\\":\\"90\\"}"
  }'

# 3) 자동 조치 — 위반 시 자동 비활성화 (선택)
$ aws configservice put-remediation-configurations --remediation-configurations '[{
    "ConfigRuleName":"access-keys-rotated-90",
    "TargetType":"SSM_DOCUMENT",
    "TargetId":"AWSConfigRemediation-RevokeUnusedIAMUserCredentials",
    "Automatic": false
  }]\'''',
 'fix_out': '''$ aws configservice describe-compliance-by-config-rule --config-rule-names access-keys-rotated-90
{
    "ComplianceByConfigRules": [
        {
            "ConfigRuleName": "access-keys-rotated-90",
            "Compliance": {"ComplianceType": "COMPLIANT"}
        }
    ]
}

$ aws iam get-credential-report --query Content --output text | base64 -d | cut -d, -f1,10
user,access_key_1_last_rotated
<root_account>,N/A
fin-admin-kim,2026-09-14T04:12:33+00:00
fin-dev-lee,2026-07-30T05:11:44+00:00
fin-batch-svc,2026-09-14T04:15:08+00:00

→ 전 키 90일 이내. Config 규칙이 이후를 자동 감시합니다.''',
 'iac': '''resource "aws_config_config_rule" "access_keys_rotated" {
  name = "access-keys-rotated-90"
  source {
    owner             = "AWS"
    source_identifier = "ACCESS_KEYS_ROTATED"
  }
  input_parameters = jsonencode({ maxAccessKeyAge = "90" })
}

# 더 나은 답 — 키 자체를 없애고 임시 자격증명으로
resource "aws_iam_role" "batch" {
  max_session_duration = 3600      # STS 임시 자격증명은 1시간 후 자동 만료
}''',
 'pitfall': '<b>주의</b> — 자격증명 보고서의 <code>last_rotated</code> 는 <b>키 생성일</b>이지 "교체 이벤트" 기록이 아닙니다. 키를 지우고 새로 만들면 갱신으로 보이지만, <b>구 키를 지우지 않으면</b> PISM-042(다중 보유) 위반이 됩니다 — 두 항목은 세트로 봐야 합니다. 그리고 자동 조치(remediation)를 <code>Automatic: true</code> 로 걸 때는 <b>운영 배치가 한밤중에 죽을 수 있다</b>는 점을 반드시 검토하세요.',
 'evidence': [
   '자격증명 보고서의 <code>last_rotated</code> 컬럼 (전 계정)',
   '갱신 주기 정책 문서 (기준일 수·대상·책임자)',
   'AWS Config <code>ACCESS_KEYS_ROTATED</code> 규칙 및 준수 상태',
   '교체 수행 기록 (신규 발급 → 전환 → 구 키 삭제)',
 ],
 'finance': '전자금융감독규정은 <b>비밀번호 등 인증정보의 주기적 변경</b>을 요구합니다. API 자격증명도 같은 성격이지만 사람이 쓰지 않아 잊히기 쉽습니다. 금융권 클라우드 평가에서는 <b>"정책이 있는가"보다 "실제 키 수명이 얼마인가"</b>를 숫자로 확인하므로, 자동 점검 체계 없이는 통과하기 어렵습니다.',
},

# ── PISM-045 권한 과다 ───────────────────────────────────────────────────
{
 'file': '07_fincloud-pism045.html', 'pism': 'PISM-045', 'risk': '3',
 'title': '그룹 및 속성 기반 권한 부여 및 최소 권한 정책 적용', 'svc': 'IAM · Lambda · EC2',
 'area': '5. 운영 관리', 'ctrl': '5.3 정보처리시스템 보호대책', 'evaltype': '관리체계, 스크립트',
 'detail': '사용자 그룹과 속성을 기반으로 접근 권한을 설정하여 개별 사용자 정책이 아닌 일괄적인 권한 관리가 이루어지며, 그룹 및 속성 기반 정책이 최소 권한 원칙을 효과적으로 구현하도록 설정되어 있는지 점검합니다.',
 'console_path': '<b>IAM</b> → <b>사용자</b> → 대상 사용자 선택 → <b>권한</b> 탭에서 직접 연결 정책 확인 → <b>그룹</b> 탭에서 그룹 멤버십과 연결 정책 확인',
 'cmds': [
   {'label': '① 사용자에게 직접 연결된 정책 (그룹이 아닌)', 'cmd': 'aws iam list-attached-user-policies --user-name fin-dev-lee --query "AttachedPolicies[*].PolicyName" --output text',
    'out': '<span class="er">AdministratorAccess</span>\n\n<span class="er">※ 개발자 계정에 관리자 정책이 직접 붙어 있습니다.</span>'},
   {'label': '② 그룹 멤버십 확인', 'cmd': 'aws iam list-groups-for-user --user-name fin-dev-lee --query "Groups[*].GroupName" --output text',
    'out': '<span class="dim">(출력 없음 — 어떤 그룹에도 속해 있지 않습니다)</span>'},
   {'label': '③ Lambda 실행 역할의 권한 범위', 'cmd': 'aws iam list-attached-role-policies --role-name fin-lambda-openbanking --query "AttachedPolicies[*].[PolicyName,PolicyArn]" --output text',
    'out': '''<span class="er">AmazonS3FullAccess</span>      arn:aws:iam::aws:policy/AmazonS3FullAccess
<span class="er">AWSLambdaBasicExecutionRole</span>  arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

<span class="er">※ 토큰 갱신만 하는 함수에 S3 전체 권한이 부여돼 있습니다.</span>'''},
   {'label': '④ 실제로 쓰인 권한만 확인 (Access Advisor)', 'cmd': 'aws iam generate-service-last-accessed-details --arn arn:aws:iam::382011749265:role/fin-lambda-openbanking',
    'out': '''{
    "JobId": "e1a7c93f-0b24-4d68-95fa-7c31de408b62"
}

$ aws iam get-service-last-accessed-details --job-id e1a7c93f-0b24-4d68-95fa-7c31de408b62 \\
      --query "ServicesLastAccessed[?TotalAuthenticatedEntities>\\`0\\`].[ServiceName,LastAuthenticated]" --output text
Amazon Simple Storage Service    2026-09-13T22:04:11+00:00
Amazon CloudWatch Logs           2026-09-14T01:58:40+00:00
AWS Secrets Manager              2026-09-14T01:58:39+00:00

<span class="dim">S3 는 쓰고 있지만 "전체 권한"이 필요한지는 별개입니다 — 버킷 1개만 씁니다.</span>'''},
 ],
 'answer': 'bad',
 'why': '''<b>그룹 기반 관리가 없고, 역할에 과도한 관리형 정책이 붙어 있습니다.</b>
<div class="ev">fin-dev-lee
  직접 연결 : <b>AdministratorAccess</b>  → 개별 사용자 정책 = 일괄 관리 불가
  그룹      : 없음                      → 평가기준이 요구하는 <b>그룹·속성 기반</b> 미충족

fin-lambda-openbanking
  <b>AmazonS3FullAccess</b> → 전 버킷 읽기·쓰기·삭제 가능
  실제 사용 : S3 1개 버킷 + Logs + Secrets Manager 뿐</div>
이 항목은 <b>두 가지를 함께</b> 봅니다 — ① 권한이 과도한가 ② 권한을 <b>그룹·역할 단위로 일괄 관리</b>하는가. 개별 사용자에게 직접 정책을 붙이는 방식은 사람이 늘수록 통제가 무너집니다.''',
 'fix_intro': '사용자는 <b>그룹으로</b> 묶고, 역할에는 <b>실제 사용 기록에 근거한 인라인 정책</b>을 씁니다. AWS 관리형 <code>*FullAccess</code> 정책은 최소 권한의 반대말입니다.',
 'fix_cmd': '''# 1) 그룹 기반으로 전환
$ aws iam create-group --group-name FinDevelopers
$ aws iam attach-group-policy --group-name FinDevelopers \\
      --policy-arn arn:aws:iam::382011749265:policy/FinDeveloperBaseline
$ aws iam add-user-to-group --group-name FinDevelopers --user-name fin-dev-lee
$ aws iam detach-user-policy --user-name fin-dev-lee \\
      --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# 2) Lambda 역할 — FullAccess 제거 후 실사용 기반 최소 정책
$ aws iam detach-role-policy --role-name fin-lambda-openbanking \\
      --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
$ aws iam put-role-policy --role-name fin-lambda-openbanking \\
      --policy-name least-privilege --policy-document '{
        "Version":"2012-10-17",
        "Statement":[
          {"Effect":"Allow","Action":["s3:GetObject","s3:PutObject"],
           "Resource":"arn:aws:s3:::fin-mydata-consent-logs/*"},
          {"Effect":"Allow","Action":"secretsmanager:GetSecretValue",
           "Resource":"arn:aws:secretsmanager:ap-northeast-2:382011749265:secret:fin/openbanking/*"}
        ]}'

# 3) 권한 경계(Permissions Boundary)로 상한을 건다
$ aws iam put-user-permissions-boundary --user-name fin-dev-lee \\
      --permissions-boundary arn:aws:iam::382011749265:policy/FinDeveloperBoundary''',
 'fix_out': '''$ aws iam list-attached-user-policies --user-name fin-dev-lee --query "AttachedPolicies[*].PolicyName" --output text
(없음)

$ aws iam list-groups-for-user --user-name fin-dev-lee --query "Groups[*].GroupName" --output text
FinDevelopers

$ aws iam list-attached-role-policies --role-name fin-lambda-openbanking --query "AttachedPolicies[*].PolicyName" --output text
AWSLambdaBasicExecutionRole

$ aws iam list-role-policies --role-name fin-lambda-openbanking --query "PolicyNames" --output text
least-privilege

→ 사용자는 그룹으로, 역할은 리소스 한정 인라인 정책으로 전환되었습니다.''',
 'iac': '''resource "aws_iam_group" "developers" { name = "FinDevelopers" }

resource "aws_iam_group_membership" "dev" {
  group = aws_iam_group.developers.name
  users = ["fin-dev-lee", "fin-dev-park"]   # 사람은 여기서만 추가/제거
}

# 역할 정책은 리소스를 명시 — "*" 를 쓰지 않는다
data "aws_iam_policy_document" "lambda_least" {
  statement {
    actions   = ["s3:GetObject", "s3:PutObject"]
    resources = ["${aws_s3_bucket.consent_logs.arn}/*"]
  }
}

# 권한 상한 — 경계를 넘는 정책은 붙여도 효력이 없다
resource "aws_iam_user" "dev" {
  permissions_boundary = aws_iam_policy.developer_boundary.arn
}''',
 'pitfall': '<b>주의</b> — Access Advisor(<code>service-last-accessed-details</code>)는 <b>서비스 단위</b>까지만 알려줍니다. "S3 를 썼다"는 알아도 "어떤 버킷·어떤 액션"인지는 CloudTrail 을 봐야 합니다. 그래서 권한을 좁힐 때는 <b>Access Advisor 로 서비스 후보를 추리고, CloudTrail 로 액션·리소스를 확정</b>하는 2단계를 거칩니다. 그리고 <b>권한을 줄이면 반드시 무언가 깨집니다</b> — 스테이징에서 먼저 적용하고, 운영은 CloudTrail 의 <code>AccessDenied</code> 를 모니터링하며 단계적으로 좁히세요.',
 'evidence': [
   '사용자별 직접 연결 정책 목록 (그룹 미사용 여부)',
   '그룹별 연결 정책 및 멤버십',
   '역할별 연결 정책 (<code>*FullAccess</code> 사용 여부)',
   'Access Advisor / CloudTrail 기반 실사용 권한 분석 자료',
   '권한 경계(Permissions Boundary) 적용 현황',
 ],
 'finance': '금융회사는 <b>직무 분리와 최소 권한</b>을 요구받습니다. 클라우드에서는 IAM 이 그 통제 지점인데, 개별 사용자에게 정책을 직접 붙이면 <b>퇴직·전보 시 회수 누락</b>이 발생합니다. 그룹·역할 기반으로 묶어야 인사 변동이 곧 권한 변동으로 이어집니다 — 평가기준이 "그룹 및 속성 기반"을 명시한 이유입니다.',
},

# ── PISM-046 CloudShell 권한 ─────────────────────────────────────────────
{
 'file': '07_fincloud-pism046.html', 'pism': 'PISM-046', 'risk': '4',
 'title': '웹 기반 쉘 환경 권한 통제 여부', 'svc': 'CloudShell · IAM',
 'area': '6. 접근통제', 'ctrl': '6.1 계정 및 권한 관리',
 'detail': '클라우드에서 제공되는 웹 기반 쉘 환경은 인터넷 접근, 인스턴스에 파일 업로드 및 다운로드 등이 가능하여 사용자 정보가 유출되거나 다른 공격에 활용될 수 있으므로, 웹 기반 쉘 환경에 대한 권한 통제 여부를 점검합니다.',
 'console_path': '<b>IAM</b> → <b>사용자</b> → 대상 사용자 선택 → <b>권한</b> 탭에서 <code>AWSCloudShellFullAccess</code> 연결 여부 또는 인라인 정책의 <code>cloudshell:*</code> 포함 여부 확인',
 'cmds': [
   {'label': '① CloudShell 관련 관리형 정책 연결 확인 (평가기준 명시 명령)', 'cmd': 'aws iam list-attached-user-policies --user-name fin-dev-lee --query "AttachedPolicies[?contains(PolicyName, \'CloudShell\')]"',
    'out': '''[
    {
        "PolicyName": "<span class="er">AWSCloudShellFullAccess</span>",
        "PolicyArn": "arn:aws:iam::aws:policy/AWSCloudShellFullAccess"
    }
]'''},
   {'label': '② 인라인 정책에 cloudshell 권한이 있는지', 'cmd': 'aws iam list-user-policies --user-name fin-dev-lee --output table',
    'out': '''--------------------------
|    ListUserPolicies    |
+------------------------+
|  dev-scratch-access    |
+------------------------+

$ aws iam get-user-policy --user-name fin-dev-lee --policy-name dev-scratch-access --query "PolicyDocument.Statement[*].Action"
[
    [
        "<span class="er">cloudshell:*</span>",
        "s3:GetObject"
    ]
]'''},
   {'label': '③ CloudShell 이 무엇을 할 수 있는가', 'cmd': 'aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::382011749265:user/fin-dev-lee --action-names cloudshell:CreateEnvironment cloudshell:PutFile cloudshell:GetFileDownloadUrls --query "EvaluationResults[*].[EvalActionName,EvalDecision]" --output text',
    'out': '''cloudshell:CreateEnvironment     <span class="er">allowed</span>
cloudshell:PutFile              <span class="er">allowed</span>
cloudshell:GetFileDownloadUrls  <span class="er">allowed</span>

<span class="er">※ 파일 업로드·다운로드가 모두 허용 — 콘솔 브라우저를 통한 데이터 반출 경로입니다.</span>'''},
 ],
 'answer': 'bad',
 'why': '''<b>CloudShell 의 파일 업로드·다운로드가 통제 없이 허용</b>되어 있습니다.
<div class="ev">AWSCloudShellFullAccess  → 관리형 정책으로 전체 권한 부여
cloudshell:* (인라인)     → 중복으로 또 부여
GetFileDownloadUrls      : allowed → <b>S3 에서 받아 브라우저로 내려받기 가능</b>
PutFile                  : allowed → 외부 도구를 CloudShell 로 올려 실행 가능</div>
CloudShell 은 <b>사용자 자신의 권한으로 실행되는 인터넷 연결 쉘</b>입니다. 망분리된 업무망에서 접속하더라도, CloudShell 안은 인터넷이 열려 있어 <b>데이터 반출과 도구 반입의 우회로</b>가 됩니다. 금융권에서 특히 민감한 항목입니다.''',
 'fix_intro': 'CloudShell 자체를 막을지, <b>파일 송수신만 막을지</b> 결정합니다. 운영 편의를 고려하면 <b>쉘은 허용하되 업로드·다운로드를 Deny</b> 하는 방식이 현실적입니다.',
 'fix_cmd': '''# 방안 A) CloudShell 전면 차단 (가장 강함)
$ aws iam detach-user-policy --user-name fin-dev-lee \\
      --policy-arn arn:aws:iam::aws:policy/AWSCloudShellFullAccess
$ aws iam put-user-policy --user-name fin-dev-lee \\
      --policy-name deny-cloudshell --policy-document '{
        "Version":"2012-10-17",
        "Statement":[{"Effect":"Deny","Action":"cloudshell:*","Resource":"*"}]}'

# 방안 B) 쉘은 허용, 파일 반출입만 차단 (권장)
$ aws iam put-user-policy --user-name fin-dev-lee \\
      --policy-name cloudshell-no-filetransfer --policy-document '{
        "Version":"2012-10-17",
        "Statement":[{
          "Effect":"Deny",
          "Action":[
            "cloudshell:GetFileDownloadUrls",
            "cloudshell:GetFileUploadUrls",
            "cloudshell:PutFile"
          ],
          "Resource":"*"}]}'

# 3) 조직 전체 적용 — SCP
$ aws organizations create-policy --type SERVICE_CONTROL_POLICY \\
      --name DenyCloudShellFileTransfer \\
      --content '{"Version":"2012-10-17","Statement":[{"Effect":"Deny",
        "Action":["cloudshell:GetFileDownloadUrls","cloudshell:PutFile"],
        "Resource":"*"}]}\'''',
 'fix_out': '''$ aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::382011749265:user/fin-dev-lee \\
      --action-names cloudshell:CreateEnvironment cloudshell:PutFile cloudshell:GetFileDownloadUrls \\
      --query "EvaluationResults[*].[EvalActionName,EvalDecision]" --output text
cloudshell:CreateEnvironment     allowed
cloudshell:PutFile               explicitDeny
cloudshell:GetFileDownloadUrls   explicitDeny

→ 쉘 사용은 가능하되 파일 반출입 경로가 차단되었습니다.''',
 'iac': '''# 조직 차원 SCP — 계정별 설정 누락을 막는다
resource "aws_organizations_policy" "deny_cloudshell_transfer" {
  name = "DenyCloudShellFileTransfer"
  type = "SERVICE_CONTROL_POLICY"
  content = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Deny"
      Action = [
        "cloudshell:GetFileDownloadUrls",
        "cloudshell:GetFileUploadUrls",
        "cloudshell:PutFile",
      ]
      Resource = "*"
    }]
  })
}''',
 'pitfall': '<b>주의</b> — CloudShell 을 막아도 <b>동등한 우회로가 여럿 남습니다.</b> <code>ssm:StartSession</code>(세션 관리자), <code>ec2-instance-connect</code>, EKS 의 <code>kubectl exec</code> 가 모두 같은 성격의 대화형 쉘입니다. 하나만 막고 "통제했다"고 판단하면 평가에서 지적됩니다. <b>대화형 접근 경로를 전부 목록화</b>하고 각각에 대해 로깅·파일전송 통제를 적용해야 합니다.',
 'evidence': [
   '사용자·역할별 CloudShell 관련 정책 연결 현황',
   '인라인 정책의 <code>cloudshell:*</code> 포함 여부',
   '<code>simulate-principal-policy</code> 결과 (파일 송수신 차단 확인)',
   '동등 경로(SSM 세션·EC2 Instance Connect·kubectl exec) 통제 현황',
   'CloudShell 사용 이력(CloudTrail) 및 검토 기록',
 ],
 'finance': '금융회사는 <b>업무망과 인터넷망의 분리</b>를 요구받습니다. CloudShell 은 브라우저 안에서 인터넷에 연결된 리눅스 쉘을 열어 주므로, 망분리 통제를 논리적으로 우회할 수 있는 지점입니다. 게다가 <b>사용자 권한을 그대로 승계</b>하므로 관리자 계정에서 열면 계정 전체를 조작할 수 있습니다 — 위험도 4 가 부여된 이유입니다.',
},

# ── PISM-023 불필요 가상자원 ─────────────────────────────────────────────
{
 'file': '07_fincloud-pism023.html', 'pism': 'PISM-023', 'risk': '3',
 'title': '업무상 불필요한 가상자원 존재', 'svc': 'EC2 · S3 · RDS · Lambda',
 'area': '5. 운영 관리', 'ctrl': '5.3 정보처리시스템 보호대책', 'evaltype': '관리체계, 스크립트',
 'detail': '업무상 불필요하거나 장기간 사용되지 않은 가상자원이 남아있을 경우, 이를 통해 비인가자가 의도되지 않은 행위를 수행할 위협이 존재하므로 업무상 불필요한 가상자원이 존재하는지 여부를 점검합니다.',
 'console_path': '<b>EC2</b> → 인스턴스 / 네트워크 인터페이스 / 스냅샷 / 볼륨 / AMI / 탄력적 IP / 보안 그룹 목록 확인 &nbsp;·&nbsp; <b>S3</b> → 버킷 목록 &nbsp;·&nbsp; <b>Lambda</b> → 함수 목록 &nbsp;·&nbsp; <b>RDS</b> → 데이터베이스·스냅샷 목록',
 'cmds': [
   {'label': '① 인스턴스 상태 확인 (중지된 채 방치된 자원)', 'cmd': 'aws ec2 describe-instances --query "Reservations[*].Instances[*].[KeyName, InstanceId, State.Name]" --output table',
    'out': '''-------------------------------------------------------------------
|                       DescribeInstances                         |
+------------------+--------------------------+-------------------+
|  fin-prod-key    |  i-0a3f72be91c4d5e80     |  running          |
|  fin-prod-key    |  i-0c81d5fa27e93b146     |  running          |
|  fin-prod-key    |  i-04e7b9c3d85a1f602     |  running          |
|  <span class="er">poc-2024-key</span>    |  <span class="er">i-0e5d8b23a97f1c460</span>     |  <span class="er">stopped</span>           |
+------------------+--------------------------+-------------------+

<span class="dim">poc-2024-key = 2024년 PoC 용 키페어. 중지 상태로 남아 있습니다.</span>'''},
   {'label': '② 미연결 네트워크 인터페이스·볼륨', 'cmd': 'aws ec2 describe-network-interfaces --query "NetworkInterfaces[?Status==\'available\'].{ENI:NetworkInterfaceId,AZ:AvailabilityZone}" --output table',
    'out': '''-------------------------------------------------
|            DescribeNetworkInterfaces          |
+---------------------------+-------------------+
|  <span class="er">eni-0f83cb7a21e4b</span>      |  ap-northeast-2a  |
+---------------------------+-------------------+

$ aws ec2 describe-volumes --query "Volumes[?State=='available'].{ID:VolumeId,Size:Size,Created:CreateTime}" --output table
+--------------------------+--------+----------------------------------+
|  <span class="er">vol-0c19e7f42d86b3a05</span>   |  100   |  <span class="er">2024-07-02T08:15:33+00:00</span>        |
+--------------------------+--------+----------------------------------+

<span class="er">※ 어디에도 붙어 있지 않은 100GB 볼륨이 2년 넘게 과금되고 있습니다.</span>'''},
   {'label': '③ 미연결 탄력적 IP·오래된 스냅샷', 'cmd': 'aws ec2 describe-addresses --query "Addresses[?InstanceId==null].[PublicIp, AllocationId]" --output table',
    'out': '''-------------------------------------------------
|               DescribeAddresses               |
+------------------+----------------------------+
|  <span class="er">13.125.44.201</span>   |  <span class="er">eipalloc-0a37b9de52c14f068</span> |
+------------------+----------------------------+

$ aws ec2 describe-snapshots --owner-ids self --query "Snapshots[?StartTime<=\\`2025-01-01\\`].[SnapshotId,StartTime,VolumeSize]" --output text
snap-0a94c17f3b28de506    2024-04-11T02:33:19+00:00    500'''},
   {'label': '④ 미사용 Lambda·S3 버킷', 'cmd': 'aws lambda list-functions --query "Functions[*].{Name:FunctionName,Modified:LastModified}" --output table',
    'out': '''----------------------------------------------------------------------------
|  fin-settlement-batch           |  2024-05-17T08:22:41.000+0000          |
|  fin-openbanking-token-refresh  |  2026-08-02T11:09:33.000+0000          |
|  fin-fds-scoring                |  2025-02-28T16:40:12.000+0000          |
|  <span class="er">poc-image-resize</span>               |  <span class="er">2024-02-09T13:51:07.000+0000</span>            |
----------------------------------------------------------------------------

<span class="dim">poc-image-resize 는 PoC 종료 후 남은 함수로 보입니다 — 인터뷰로 확인이 필요합니다.</span>'''},
 ],
 'answer': 'bad',
 'why': '''<b>PoC 종료 후 정리되지 않은 자원이 다수 남아 있습니다.</b>
<div class="ev">i-0e5d8b23a97f1c460  : stopped, poc-2024-key 로 기동 — 중지 인스턴스도 <b>볼륨·IP·SG 가 살아 있음</b>
vol-0c19e7f42d86b3a05 : available(미연결) 100GB, 2024-07 생성 → 데이터가 남은 채 방치
eni-0f83c..., eipalloc-0a37b9... : 미연결 상태로 존재
snap-0a94c17f3b28de506 : 2024-04 스냅샷 500GB
poc-image-resize      : 2024-02 이후 미수정 Lambda</div>
이 항목은 <b>스크립트만으로 판정할 수 없습니다.</b> 평가기준도 "목록을 기반으로 <b>인터뷰를 진행</b>하여" 확인하라고 명시합니다. CLI 로 후보를 뽑고, 업무 담당자에게 필요성을 확인하는 2단계가 정석입니다.''',
 'fix_intro': '먼저 <b>태그로 소유자·용도를 붙이고</b>, 확인되지 않은 자원은 <b>중지 → 관찰 → 삭제</b> 순으로 정리합니다. 바로 지우면 분기 배치·재해복구용 자원을 날릴 수 있습니다.',
 'fix_cmd': '''# 1) 전수 태깅 — 소유자 없는 자원부터 찾는다
$ aws resourcegroupstaggingapi get-resources \\
      --tag-filters Key=Owner --query "ResourceTagMappingList[*].ResourceARN" --output text > tagged.txt
$ aws resourcegroupstaggingapi get-resources \\
      --query "ResourceTagMappingList[?length(Tags)==\\`0\\`].ResourceARN" --output text

# 2) 미연결 자원 정리
$ aws ec2 delete-volume          --volume-id vol-0c19e7f42d86b3a05
$ aws ec2 release-address        --allocation-id eipalloc-0a37b9de52c14f068
$ aws ec2 delete-network-interface --network-interface-id eni-0f83cb7a21e4b
$ aws ec2 delete-snapshot        --snapshot-id snap-0a94c17f3b28de506

# 3) PoC 인스턴스 — 종료 전 스냅샷 후 삭제
$ aws ec2 create-snapshot --volume-id vol-0b7d29e13fa85c604 \\
      --description "final backup before poc teardown"
$ aws ec2 terminate-instances --instance-ids i-0e5d8b23a97f1c460

# 4) 재발 방지 — 태그 없으면 생성 거부 (SCP) + 미사용 자원 주기 리포트
$ aws configservice put-config-rule --config-rule '{
    "ConfigRuleName":"required-tags-owner",
    "Source":{"Owner":"AWS","SourceIdentifier":"REQUIRED_TAGS"},
    "InputParameters":"{\\"tag1Key\\":\\"Owner\\",\\"tag2Key\\":\\"CostCenter\\"}"
  }'
$ aws ec2 create-snapshot-schedule --help  # DLM 으로 스냅샷 보존기간 자동화''',
 'fix_out': '''$ aws ec2 describe-volumes --query "Volumes[?State=='available'].VolumeId" --output text
(없음)

$ aws ec2 describe-addresses --query "Addresses[?InstanceId==null].PublicIp" --output text
(없음)

$ aws ec2 describe-network-interfaces --query "NetworkInterfaces[?Status=='available'].NetworkInterfaceId" --output text
(없음)

$ aws configservice describe-compliance-by-config-rule --config-rule-names required-tags-owner \\
      --query "ComplianceByConfigRules[0].Compliance.ComplianceType" --output text
COMPLIANT

→ 미연결 자원 0건. 태그 규칙이 이후 신규 자원을 자동 점검합니다.''',
 'iac': '''# 태그를 기본값으로 강제 — provider 수준에서 모든 자원에 자동 부착
provider "aws" {
  default_tags {
    tags = {
      Owner      = "fin-platform"
      CostCenter = "FIN-CLOUD-01"
      Env        = "prod"
      ManagedBy  = "terraform"
    }
  }
}

resource "aws_config_config_rule" "required_tags" {
  name = "required-tags-owner"
  source { owner = "AWS" source_identifier = "REQUIRED_TAGS" }
  input_parameters = jsonencode({ tag1Key = "Owner", tag2Key = "CostCenter" })
}''',
 'pitfall': '<b>주의</b> — <b>중지된 인스턴스는 "없는 자원"이 아닙니다.</b> EBS 볼륨·보안그룹·IAM 역할이 그대로 살아 있어, 누군가 다시 켜면 옛 취약점을 가진 서버가 그대로 돌아옵니다(패치도 그동안 안 됐습니다). 또한 이 항목은 <b>스크립트 결과만으로 취약 판정을 내리면 안 됩니다</b> — 재해복구용 대기 자원, 분기 배치용 인스턴스처럼 정당한 사유가 있을 수 있으므로 <b>반드시 담당자 인터뷰로 확인</b>하고 그 기록을 증적으로 남기세요.',
 'evidence': [
   '자원 유형별 전체 목록 (인스턴스·볼륨·ENI·EIP·스냅샷·AMI·SG·버킷·함수·DB)',
   '미연결/장기 미사용 후보 목록 및 <b>담당자 인터뷰 결과</b>',
   '정리 대상 판정 근거와 삭제 전 백업 내역',
   '태그 정책(Owner·CostCenter) 준수 현황',
   '주기적 미사용 자원 점검 프로세스 문서',
 ],
 'finance': '방치된 자원은 <b>패치되지 않는 공격 표면</b>입니다. 아무도 보지 않으므로 침해되어도 탐지가 늦고, PoC 시절의 느슨한 보안그룹·구버전 OS 를 그대로 유지합니다. 금융권에서는 여기에 <b>자산 식별·관리 의무</b> 문제가 더해집니다 — 자산 목록에 없는 서버에 고객정보가 남아 있으면 그 자체로 중대한 지적 사항입니다.',
},

]
