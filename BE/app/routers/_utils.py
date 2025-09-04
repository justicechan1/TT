import json
from decimal import Decimal
from typing import Any, Iterable, List, Optional

def to_float(v: Any) -> Optional[float]:
    if v is None:
        return None
    if isinstance(v, Decimal):
        return float(v)
    try:
        return float(v)
    except Exception:
        return None

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
        # 콤마구분 등 느슨 파서
        return [s.strip() for s in str(text).split(",") if s.strip()]
    return None

def cos_sim(a: List[float], b: List[float]) -> float:
    import math
    if not a or not b:
        return 0.0
    n = min(len(a), len(b))
    aa = a[:n]; bb = b[:n]
    dot = sum(x*y for x, y in zip(aa, bb))
    na = math.sqrt(sum(x*x for x in aa)) or 1e-9
    nb = math.sqrt(sum(y*y for y in bb)) or 1e-9
    return dot / (na * nb)

def avg_vec(vectors: Iterable[List[float]]) -> List[float]:
    vs = [v for v in vectors if v]
    if not vs:
        return []
    n = max(len(v) for v in vs)
    sums = [0.0]*n; cnt = [0]*n
    for v in vs:
        for i, x in enumerate(v):
            sums[i] += float(x); cnt[i] += 1
    return [ (s / c if c else 0.0) for s, c in zip(sums, cnt) ]
