# models.py

from sqlalchemy import Column, Integer, Boolean, Text, Numeric
from database import Base

class Boodschap(Base):
    __tablename__ = 'boodschappen'
    id = Column(Integer, primary_key=True)
    barcode = Column(Text)
    omschrijving = Column(Text)
    prijs = Column(Text)
    aantal = Column(Integer)

    def __repr__(self):
        return f"<Boodschap::{self.barcode}>"
