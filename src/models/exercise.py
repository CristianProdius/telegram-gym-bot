from sqlalchemy import Column, Integer, String, Text
from src.database.connection import Base

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)  # chest, back, legs, etc.
    muscle_group = Column(String, nullable=False)
    equipment = Column(String, nullable=True)  # barbell, dumbbell, machine, bodyweight
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Exercise(name={self.name}, category={self.category})>"
