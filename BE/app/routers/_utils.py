import json
import math
from decimal import Decimal
from typing import Any, Iterable, List, Optional

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


def avg_vec(vectors: Iterable[Iterable[float]]) -> np.ndarray:
    arrs: List[np.ndarray] = []
    for v in vectors:
        a = _clean_vec(v)
        if a is not None:
            arrs.append(a)
    if not arrs:
        return np.array([], dtype=float)

    d = min(a.shape[0] for a in arrs)
    if d == 0:
        return np.array([], dtype=float)

    stacked = np.vstack([a[:d] for a in arrs])  # (N, d)
    return stacked.mean(axis=0)                 # (d,)


def normalize_vectors(v: np.ndarray) -> np.ndarray:
    a = _clean_vec(v)
    if a is None or a.size == 0:
        return np.asarray(v, dtype=float).reshape(-1) if v is not None else np.array([], dtype=float)
    n = np.linalg.norm(a)
    if n == 0.0 or not np.isfinite(n):
        return a
    return a / n
