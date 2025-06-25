import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

from sqlmodel import SQLModel
# ──────────────────────────────────────────────
# 1) .env 로부터 DATABASE_URL 주입
# ──────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
dotenv_path = os.path.join(BASE_DIR, ".env")

load_dotenv()                                         # .env 읽기
config = context.config
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))
load_dotenv(dotenv_path)
print("★ DATABASE_URL =", os.getenv("DATABASE_URL"))


# ──────────────────────────────────────────────
# 2) Alembic 로깅 설정
# ──────────────────────────────────────────────
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ──────────────────────────────────────────────
# 3) 모델 import (반드시! – 메타데이터 등록 목적)
#    경로는 프로젝트 구조에 맞게 조정하세요
# ──────────────────────────────────────────────
from models import users_model, diarys_model  # ← 실제 모듈 경로

# 4) 메타데이터 연결
target_metadata = SQLModel.metadata

# ──────────────────────────────────────────────
def run_migrations_offline() -> None:
    """offline 모드: DB 연결 없이 스크립트만 생성"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """online 모드: 실제로 DB에 접속해 마이그레이션"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

# 선택적으로 context.is_offline_mode() 분기
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
