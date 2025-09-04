#main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.errors import (
    app_error_handler,
    request_validation_error_handler,
    http_exception_handler,
    unhandled_exception_handler,
    AppError,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.schemas.common import ErrorResponse

app = FastAPI(title="Trendy Trip API")

app = FastAPI(
    title="Trendy Trip API",
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        410: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)

# ✅ 전역 예외 핸들러 등록 (순서 중요 X)
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, request_validation_error_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# 반드시 FastAPI 생성 이후에 설정
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",  # 개발용: 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 나머지 import 및 라우터 등록
from app.routers import places, maps, db_checker, schedules
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app.include_router(schedules.router)
app.include_router(places.router)
app.include_router(maps.router)
app.include_router(db_checker.router)


@app.get("/")
def root():
    return {"message": "MainCafe API"}