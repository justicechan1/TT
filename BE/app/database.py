#database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


#SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:tt123@127.0.0.1:3306/tt_test" #캡실컴
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:1234@127.0.0.1:3306/tt" #의찬main
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:1234@127.0.0.1:3306/tt_test" #의찬test
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:tt123@192.168.0.129:3306/tt_test"  #DB URL입력
#SQLALCHEMY_DATABASE_URL = "mysql+pymysql://justice:tt123@192.168.0.129:3306/tt"  #캡실 네트워크 연결

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

# DB 세션 DI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()