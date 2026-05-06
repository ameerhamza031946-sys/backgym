
import sys
import os
import json
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.ai_trainer import generate_workout_plan

user_profile = {
    "id": 1,
    "name": "Elite Athlete",
    "goal": "build_muscle",
    "level": "intermediate",
    "equipment_preference": "gym",
    "targeted_muscle_groups": ["chest", "back"],
    "mobility_test_results": {},
    "training_frequency": "4 times a week",
    "strength": 85.0,
    "stamina": 62.0
}
recovery_metrics = {"sleep_hours": 8.0, "cns_readiness": 90.0}

print("Starting AI workout generation test...")
try:
    plan = generate_workout_plan(user_profile, recovery_metrics)
    print("Generation successful!")
    print(json.dumps(plan, indent=2))
except Exception as e:
    print(f"Generation failed with error: {e}")
    import traceback
    traceback.print_exc()
