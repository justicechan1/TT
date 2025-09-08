import json
from decimal import Decimal
from typing import Any, List, Optional
from sqlalchemy import and_
import numpy as np


# 주어진 값을 float로 변환(문자열/Decimal 허용)
def to_float(v: Any) -> Optional[float]:
    if v is None:
        return None
    if isinstance(v, Decimal):
        return float(v)
    try:
        return float(v)
    except Exception:
        return None


# 이미지 URL 문자열을 리스트로 변환
def parse_image_url(text: Optional[str]) -> Optional[List[str]]:
    if not text:
        return None
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return [str(x) for x in data]
        if isinstance(data, str):
            return [data]
    except Exception:
        # 콤마 구분 등 느슨 파서
        return [s.strip() for s in str(text).split(",") if s.strip()]
    return None

# 벡터 유틸 (안전한 평균/정규화/코사인 계산을 위해 NumPy 사용)
def _clean_vec(v) -> Optional[np.ndarray]:
    """입력(JSON list/ndarray)을 1D np.ndarray[float]로 안전 변환."""
    if v is None:
        return None
    try:
        a = np.asarray(v, dtype=float).reshape(-1)
    except Exception:
        return None
    if a.size == 0 or not np.isfinite(a).all():
        return None
    return a

# convenience 컬럼을 List[str]로 변환
def parse_convenience(val: Optional[str]) -> List[str]:
    if not val:
        return []
    s = val.strip()
    if (s.startswith("[") and s.endswith("]")) or (s.startswith("{") and s.endswith("}")):
        try:
            data = json.loads(s)
            if isinstance(data, list):
                return [str(x).strip() for x in data if str(x).strip()]
            if isinstance(data, dict):
                return [str(v).strip() for v in data.values() if str(v).strip()]
        except Exception:
            pass
    for sep in [",", "/", ";", "|"]:
        if sep in s:
            return [x.strip() for x in s.split(sep) if x.strip()]
    return [s]  

# DB의 JSON/TEXT 벡터를 np.ndarray(D,)로 변환.
def _json_vec(val):
    # MySQL JSON 컬럼이 파이썬에서 list로 올 수도, str로 올 수도 있음
    if isinstance(val, (list, tuple)):
        return np.asarray(val, dtype=np.float32).reshape(-1)
    if isinstance(val, str):
        return np.asarray(json.loads(val), dtype=np.float32).reshape(-1)
    return None

def _viewport_filter(x_col, y_col, vp):
    min_x = to_float(vp.min_x); max_x = to_float(vp.max_x)
    min_y = to_float(vp.min_y); max_y = to_float(vp.max_y)
    return and_(x_col >= min_x, x_col <= max_x, y_col >= min_y, y_col <= max_y)