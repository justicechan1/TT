from typing import List
from pydantic import BaseModel


# ---------- /api/users/maps /hashtage ----------
# Input
class Viewport(BaseModel):
    min_x: float
    min_y: float
    max_x: float
    max_y: float

class HashtageIn(BaseModel):
    category: str
    viewport: Viewport

# Output
class HashtagOnly(BaseModel):
    hashtag: str

class HashtageOut(BaseModel):
    tag: List[HashtagOnly]


# ---------- /api/users/maps /select_hashtage ----------
# Input
class SelectHashtageIn(BaseModel):
    category: str
    tag: List[HashtagOnly]
    viewport: Viewport

# Output
class SelectHashtageOutItem(BaseModel):
    name: str
    category: str
    x_cord: float
    y_cord: float
    similarity: float

class SelectHashtageOut(BaseModel):
    select_hashtage: List[SelectHashtageOutItem]
