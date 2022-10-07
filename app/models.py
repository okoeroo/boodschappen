# models.py

from sqlalchemy import Column, Integer, Boolean, Text
from database import Base

class Boodschap(Base):
    __tablename__ = 'boodschappen'
    id = Column(Integer, primary_key=True)
    omschrijving = Column(Text)
    aantal = Column(Integer)

    def __repr__(self):
        return '<Boodschap %r>' % (self.id)
