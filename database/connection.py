from typing import Optional
from pydantic_settings import BaseSettings
from sshtunnel import SSHTunnelForwarder
from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    SECRET_KEY: Optional[str] = None
    
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_S3_BUCKET: str
    AWS_REGION: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    
    CLOVA_API_KEY: str

    ROLE_ARN : str

    BASTION_HOST : str
    BASTION_USER : str
    BASTION_KEY_PATH : str
    RDS_HOST : str
    RDS_PORT : int
    LOCAL_PORT : int
    
    class Config:
        env_file = ".env"

settings = Settings()
    
#database_connection_string = "mysql+pymysql://fastapiuser:p%40ssw0rd@localhost:3306/fastapidb"

BASE_DIR = Path(__file__).resolve().parent.parent  # 프로젝트 루트 (Vagrantfile 위치)
KEY_PATH = "/app/keys/MyKeyPair.pem" 
def start_ssh_tunnel_and_connect():
    global ssh_server, engine_url

    ssh_server = SSHTunnelForwarder(
        (settings.BASTION_HOST, 22),
        ssh_username=settings.BASTION_USER,
        ssh_pkey=KEY_PATH,
        remote_bind_address=(settings.RDS_HOST, settings.RDS_PORT),
        local_bind_address=("127.0.0.1", settings.LOCAL_PORT),
        set_keepalive=30,
    )
    ssh_server.start()

    # SSH 터널된 로컬 포트로 DB 연결
    engine_url = create_engine(
        settings.DATABASE_URL,  # ← 이미 LOCAL_PORT 기반임
        echo=True,
        pool_pre_ping=True,
        connect_args={"coonect_timeout":10},
    )

    # 테이블 생성
    SQLModel.metadata.create_all(engine_url)

def stop_ssh_tunnel():
    global ssh_server
    if ssh_server:
        ssh_server.stop()

def get_session():
    with Session(engine_url) as session:
        yield session
