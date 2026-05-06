from pydantic import BaseModel
from datetime import datetime

class WorkoutPlanResponse(BaseModel):
    id: str
    focus: str
    duration_mins: int
    calories: int
    completed: bool
    exercises: list[dict] # Each dict: {name, sets, reps, video_url, thumbnail_url}

class StartWorkoutRequest(BaseModel):
    user_id: str

class CompleteWorkoutRequest(BaseModel):
    workout_id: str

class RecoveryAlertResponse(BaseModel):
    has_warning: bool
    message: str | None

class PerformanceStats(BaseModel):
    strength: int
    stamina: int
    recovery: int
    weekly_progress: list[dict]

class UserProfileUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    equipment_preference: str | None = None
    fitness_goal: str | None = None
    gender: str | None = None
    age_range: str | None = None
    fitness_level: str | None = None
    training_frequency: str | None = None
    nutrition_goal: str | None = None
    onboarding_completed: bool | None = None
    targeted_muscle_groups: list[str] | None = None
    mobility_test_results: dict | None = None
    available_equipment: list[str] | None = None

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class MealLogBase(BaseModel):
    name: str
    calories: int
    protein: int
    carbs: int
    fats: int

class MealLogCreate(MealLogBase):
    user_id: str

class MealLogResponse(MealLogBase):
    id: str
    timestamp: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: str | None = None

class UserInDBBase(BaseModel):
    id: str
    name: str
    email: str
    onboarding_completed: bool

    class Config:
        from_attributes = True

class UserResponse(UserInDBBase):
    pass
