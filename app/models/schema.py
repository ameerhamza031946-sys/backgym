from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, EmailStr

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, *args, **kwargs):
        if not isinstance(v, str):
            raise ValueError("Invalid ObjectId string")
        return v

class BaseDocument(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={datetime: lambda dt: dt.isoformat()}
    )

    def __init__(self, **data: Any):
        # Convert ObjectId to str if present
        if "_id" in data and not isinstance(data["_id"], str):
            data["_id"] = str(data["_id"])
        super().__init__(**data)

class User(BaseDocument):
    name: str = "Athlete"
    email: str
    password: str
    strength_score: float = 85.0
    stamina_score: float = 62.0
    recovery_score: float = 34.0
    equipment_preference: str = "gym" # 'gym' or 'home'
    fitness_goal: Optional[str] = None
    gender: Optional[str] = None
    age_range: Optional[str] = None
    fitness_level: Optional[str] = None
    training_frequency: Optional[str] = None
    nutrition_goal: Optional[str] = None
    onboarding_completed: bool = False
    targeted_muscle_groups: List[str] = Field(default_factory=list)
    mobility_test_results: Dict[str, Any] = Field(default_factory=dict)
    available_equipment: List[str] = Field(default_factory=list)

class Workout(BaseDocument):
    user_id: str
    date: datetime = Field(default_factory=datetime.utcnow)
    title: str
    focus: Optional[str] = None
    duration_mins: int
    calories: int
    completed: bool = False
    exercises: List[Dict[str, Any]] = Field(default_factory=list)

class RecoveryData(BaseDocument):
    user_id: str
    date: datetime = Field(default_factory=datetime.utcnow)
    sleep_hours: float
    soreness_level: str
    cns_readiness: float

class MealPlan(BaseDocument):
    user_id: str
    date: datetime = Field(default_factory=datetime.utcnow)
    daily_calories_target: int
    macros: Dict[str, Any]
    meals: List[Dict[str, Any]]

class LoggedMeal(BaseDocument):
    user_id: str
    name: str
    calories: int
    protein: int
    carbs: int
    fats: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ActivityLog(BaseDocument):
    user_id: Optional[str] = None
    endpoint: str
    method: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
