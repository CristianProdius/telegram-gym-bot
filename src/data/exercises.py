"""Initial exercise dataset for the gym bot"""

INITIAL_EXERCISES = [
    # Chest exercises
    {"name": "Bench Press", "category": "Chest", "muscle_group": "Pectorals", "equipment": "Barbell"},
    {"name": "Dumbbell Press", "category": "Chest", "muscle_group": "Pectorals", "equipment": "Dumbbell"},
    {"name": "Incline Bench Press", "category": "Chest", "muscle_group": "Upper Pectorals", "equipment": "Barbell"},
    {"name": "Dips", "category": "Chest", "muscle_group": "Lower Pectorals", "equipment": "Bodyweight"},
    {"name": "Push-ups", "category": "Chest", "muscle_group": "Pectorals", "equipment": "Bodyweight"},
    {"name": "Cable Flyes", "category": "Chest", "muscle_group": "Pectorals", "equipment": "Cable"},

    # Back exercises
    {"name": "Deadlift", "category": "Back", "muscle_group": "Erector Spinae", "equipment": "Barbell"},
    {"name": "Pull-ups", "category": "Back", "muscle_group": "Latissimus Dorsi", "equipment": "Bodyweight"},
    {"name": "Barbell Row", "category": "Back", "muscle_group": "Middle Back", "equipment": "Barbell"},
    {"name": "Lat Pulldown", "category": "Back", "muscle_group": "Latissimus Dorsi", "equipment": "Cable"},
    {"name": "T-Bar Row", "category": "Back", "muscle_group": "Middle Back", "equipment": "Barbell"},
    {"name": "Face Pulls", "category": "Back", "muscle_group": "Rear Delts", "equipment": "Cable"},

    # Legs exercises
    {"name": "Squat", "category": "Legs", "muscle_group": "Quadriceps", "equipment": "Barbell"},
    {"name": "Leg Press", "category": "Legs", "muscle_group": "Quadriceps", "equipment": "Machine"},
    {"name": "Romanian Deadlift", "category": "Legs", "muscle_group": "Hamstrings", "equipment": "Barbell"},
    {"name": "Leg Curl", "category": "Legs", "muscle_group": "Hamstrings", "equipment": "Machine"},
    {"name": "Leg Extension", "category": "Legs", "muscle_group": "Quadriceps", "equipment": "Machine"},
    {"name": "Calf Raises", "category": "Legs", "muscle_group": "Calves", "equipment": "Machine"},
    {"name": "Lunges", "category": "Legs", "muscle_group": "Quadriceps", "equipment": "Dumbbell"},

    # Shoulders exercises
    {"name": "Overhead Press", "category": "Shoulders", "muscle_group": "Deltoids", "equipment": "Barbell"},
    {"name": "Dumbbell Shoulder Press", "category": "Shoulders", "muscle_group": "Deltoids", "equipment": "Dumbbell"},
    {"name": "Lateral Raises", "category": "Shoulders", "muscle_group": "Side Delts", "equipment": "Dumbbell"},
    {"name": "Front Raises", "category": "Shoulders", "muscle_group": "Front Delts", "equipment": "Dumbbell"},
    {"name": "Arnold Press", "category": "Shoulders", "muscle_group": "Deltoids", "equipment": "Dumbbell"},
    {"name": "Upright Row", "category": "Shoulders", "muscle_group": "Deltoids", "equipment": "Barbell"},

    # Arms exercises
    {"name": "Barbell Curl", "category": "Arms", "muscle_group": "Biceps", "equipment": "Barbell"},
    {"name": "Dumbbell Curl", "category": "Arms", "muscle_group": "Biceps", "equipment": "Dumbbell"},
    {"name": "Hammer Curl", "category": "Arms", "muscle_group": "Biceps", "equipment": "Dumbbell"},
    {"name": "Preacher Curl", "category": "Arms", "muscle_group": "Biceps", "equipment": "Barbell"},
    {"name": "Tricep Pushdown", "category": "Arms", "muscle_group": "Triceps", "equipment": "Cable"},
    {"name": "Overhead Tricep Extension", "category": "Arms", "muscle_group": "Triceps", "equipment": "Dumbbell"},
    {"name": "Close-Grip Bench Press", "category": "Arms", "muscle_group": "Triceps", "equipment": "Barbell"},
    {"name": "Skull Crushers", "category": "Arms", "muscle_group": "Triceps", "equipment": "Barbell"},

    # Core exercises
    {"name": "Plank", "category": "Core", "muscle_group": "Abs", "equipment": "Bodyweight"},
    {"name": "Crunches", "category": "Core", "muscle_group": "Abs", "equipment": "Bodyweight"},
    {"name": "Russian Twists", "category": "Core", "muscle_group": "Obliques", "equipment": "Bodyweight"},
    {"name": "Leg Raises", "category": "Core", "muscle_group": "Lower Abs", "equipment": "Bodyweight"},
    {"name": "Cable Crunches", "category": "Core", "muscle_group": "Abs", "equipment": "Cable"},
    {"name": "Ab Wheel", "category": "Core", "muscle_group": "Abs", "equipment": "Equipment"},
]

async def seed_exercises(session):
    """Seed the database with initial exercises"""
    from src.models.exercise import Exercise
    from sqlalchemy import select

    for exercise_data in INITIAL_EXERCISES:
        # Check if exercise already exists
        stmt = select(Exercise).where(Exercise.name == exercise_data["name"])
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        if not existing:
            exercise = Exercise(**exercise_data)
            session.add(exercise)

    await session.commit()
    return len(INITIAL_EXERCISES)