# 1. Python 3.11 기반 슬림 이미지 사용
FROM python:3.11-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 필수 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    default-libmysqlclient-dev \
    build-essential \
    && apt-get clean

# 4. 파이썬 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. 소스 코드 복사
COPY . .

# 6. 포트 오픈
EXPOSE 8000

# 7. FastAPI 앱 실행 명령 (main.py 내부에 app 객체가 있다고 가정)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
