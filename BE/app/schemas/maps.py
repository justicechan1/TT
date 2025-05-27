# schemas/maps.py

from pydantic import BaseModel
from typing import List, Optional

# ---------- 해시태그 (Hashtage) ----------

class TagInfo(BaseModel):
    hashtag: str

class Viewport(BaseModel):
    min_x: float
    min_y: float
    max_x: float
    max_y: float

class HashtagInput(BaseModel):
    category: str
    viewport: Viewport

class HashtagOutput(BaseModel):
    tag: List[TagInfo]

# ---------- 지도 새로고침 (select_hashtage) ----------

class MoveInfo(BaseModel):
    name: str
    x_cord: float
    y_cord: float
    similarity: Optional[float] = None

class MoveInput(BaseModel):
    category: str
    tag: List[TagInfo]
    viewport: Viewport

class MoveResponse(BaseModel):
    select_hashtage: List[MoveInfo]
