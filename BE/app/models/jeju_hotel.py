#models/jeju_hotel.py
from sqlalchemy import Column, Integer, String, Float, Text, DECIMAL
from app.database import Base

class JejuHotel(Base):
    __tablename__ = "hotel"

    hotel_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    category = Column(String(255))
    page_url = Column(Text)
    score = Column(Float)
    address = Column(Text)
    phone = Column(String(100))
    convenience = Column(Text)
    website = Column(Text)
    y_cord = Column(DECIMAL(10, 7))
    x_cord = Column(DECIMAL(10, 7))
    open_time = Column(String(255))
    close_time = Column(String(255))
    break_time = Column(String(255))
    service_time = Column(String(255))
    closed_days = Column(String(255))
    image_url = Column(Text)

    @property
    def id(self):
        return self.hotel_id

class JejuhotelHashtag(Base):
    __tablename__ = "hotel_hashtag"  

    hashtag_id = Column(Integer, primary_key=True)  
    hotel_id = Column(Integer)
    hashtag = Column(String(100))  
    embeddings = Column(Text)

    class Config:
        from_attributes = True