# check_env.py (TripScheduler 디렉토리에 저장 추천)

import os
from dotenv import load_dotenv
from pathlib import Path

# .env 파일 경로를 명확히 지정
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

# 환경변수 출력
print("🔍 NAVER_API_CLIENT_ID:", os.getenv("NAVER_API_CLIENT_ID"))
print("🔍 NAVER_API_CLIENT_SECRET:", os.getenv("NAVER_API_CLIENT_SECRET"))
print("🔍 OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
000