from sqlalchemy.orm import Session
from src.models.exercise import Exercise

def list_exercises(session: Session):
    return session.query(Exercise).all()

def find_exercises_by_name(session: Session, query: str):
    return session.query(Exercise).filter(
        Exercise.name.ilike(f"%{query}%")
    ).all()
