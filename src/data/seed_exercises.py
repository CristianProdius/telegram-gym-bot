from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100))
    primary_muscle = Column(String(100))

    def __repr__(self):
        return f"<Exercise(name={self.name}, category={self.category}, muscle={self.primary_muscle})>"
        