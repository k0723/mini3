import os
from uuid import uuid4
from pathlib import Path

import boto3
from dotenv import load_dotenv

# ───────────────────────────────────────
# 0) 환경 변수 로드
# ───────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)

AWS_REGION   = os.getenv("AWS_REGION")
BUCKET_NAME  = os.getenv("AWS_S3_BUCKET")
ROLE_ARN     = os.getenv("ROLE_ARN")

# ───────────────────────────────────────
# 1) STS AssumeRole → 임시 자격증명 획득
# ───────────────────────────────────────
def get_s3_client():
    sts = boto3.client("sts", region_name=AWS_REGION)
    creds = sts.assume_role(
    RoleArn=ROLE_ARN,
    RoleSessionName="presigner"
    )["Credentials"]

    return boto3.client(
        "s3",
        region_name = AWS_REGION,
        aws_access_key_id = creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"]
    )


# ───────────────────────────────────────
# 2) Role 자격증명으로 S3 클라이언트 단일 생성
# ───────────────────────────────────────

print("✅ [DEBUG] BUCKET_NAME =", BUCKET_NAME)
print("✅ [DEBUG] REGION      =", AWS_REGION)

# ───────────────────────────────────────
# 3) 파일 직접 업로드 (옵션)
# ───────────────────────────────────────
def upload_file_to_s3(file, filename: str | None = None) -> str:
    """FastAPI UploadFile 같은 file 객체를 바로 S3로 업로드"""
    s3 = get_s3_client()
    ext      = file.filename.split('.')[-1]
    filename = filename or f"{uuid4()}.{ext}"

    s3.upload_fileobj(
        Fileobj=file.file,
        Bucket=BUCKET_NAME,
        Key=filename,
        ExtraArgs={"ContentType": file.content_type}
    )

    return f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{filename}"


# ───────────────────────────────────────
# 4) PUT presigned-URL 발급
# ───────────────────────────────────────
def get_presigned_url(file_type: str) -> dict:
    """
    클라이언트(프론트엔드)가 직접 S3에 PUT 업로드할 수 있는 presigned-URL 반환
    :param file_type: 'png', 'jpg' 등 파일 확장자
    """
    s3 = get_s3_client()
    key = f"{uuid4()}.{file_type}"

    url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": key,
            "ContentType": f"image/{file_type}"       # curl/axios 쪽도 동일 헤더 필요
        },
        ExpiresIn=900                                 # 15분 권장
    )
    return {"url": url, "key": key}


# utils/s3.py 내부
def generate_presigned_download_url(file_key: str) -> str:
    s3 = get_s3_client()
    return s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': file_key},
        ExpiresIn=3600
    )
