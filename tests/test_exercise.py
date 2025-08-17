import pytest
from src.models.exercise import Exercise
from src.data.seed_exercises import seed_exercises, INITIAL_EXERCISES
from src.services.exercise_service import list_exercises, find_exercises_by_name

def test_exercise_model_creation(test_db):
    exercise = Exercise(name="Bench Press", category="Chest", primary_muscle="Pectorals")
    test_db.add(exercise)
    test_db.commit()

    saved = test_db.query(Exercise).first()
    assert saved.name == "Bench Press"
    assert saved.category == "Chest"

def test_seed_exercises(test_db):
    seed_exercises(test_db)
    exercises = list_exercises(test_db)
    assert len(exercises) == len(INITIAL_EXERCISES)

def test_find_exercises_by_name(test_db):
    seed_exercises(test_db)
    results = find_exercises_by_name(test_db, "squat")
    assert any("Squat" in e.name for e in results)
