import os
import json
import time
from typing import List
from google import genai
from .knowledge_base import search_exercises
from .adaptation_agent import agent

# Initialize client using the GEMINI_API_KEY environment variable
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# Models to try in order — fallback to smaller/faster if quota hit
GEMINI_MODELS = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-flash-8b']

def generate_with_fallback(prompt: str) -> str:
    """Try Gemini models in order, handling rate limits gracefully."""
    if not client:
        return None
    for model in GEMINI_MODELS:
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            return response.text
        except Exception as e:
            err = str(e)
            if '429' in err or 'RESOURCE_EXHAUSTED' in err or 'quota' in err.lower():
                print(f"FitAI: {model} quota hit, trying next model...")
                time.sleep(1)
                continue
            elif '404' in err or 'NOT_FOUND' in err:
                print(f"FitAI: {model} not found, trying next model...")
                continue
            else:
                print(f"FitAI: Unexpected error with {model}: {e}")
                raise
    return None  # All models exhausted

from pydantic import BaseModel, Field

class ExercisePlan(BaseModel):
    name: str
    sets: int
    reps: int
    video_url: str
    thumbnail_url: str

class WorkoutPlan(BaseModel):
    focus: str
    duration_mins: int
    calories: int
    exercises: List[ExercisePlan]

async def generate_workout_plan(user_profile: dict, recovery_metrics: dict):
    """
    FitAI Agentic RAG Pipeline:
    1. Agent analyzes history and mobility for 'Adaptation Instructions'.
    2. RAG retrieves relevant exercises based on equipment and goal.
    3. LLM crafts the final plan using these constraints.
    4. Pydantic validates the output for system reliability.
    """
    # 1. Agent Analysis
    adaptation_instructions = agent.get_adaptation_prompt(user_profile)
    
    # 2. RAG Retrieval
    query = f"Workout for {user_profile.get('goal', 'fitness')} using {user_profile.get('equipment_preference', 'gym')}. Focus: {', '.join(user_profile.get('targeted_muscle_groups', []))}"
    relevant_exercises = await search_exercises(query, n_results=5)
    exercises_context = "\n".join([f"- {ex['metadata']['name']}: {ex['document']}" for ex in relevant_exercises])

    if not client:
        # Dynamic fallback logic
        intensity = "High" if recovery_metrics.get("cns_readiness", 100) > 70 else "Low"
        return {
            "focus": f"{intensity} Intensity Routine (FitAI Fallback)",
            "duration_mins": 45 if intensity == "High" else 20,
            "calories": 400 if intensity == "High" else 150,
            "exercises": [
                {
                    "name": ex['metadata']['name'], 
                    "sets": 3, "reps": 10,
                    "video_url": "https://mir-s3-cdn-cf.behance.net/project_modules/max_1200/31a97d100994191.5f154db23999e.gif",
                    "thumbnail_url": "https://img.freepik.com/premium-photo/man-working-out-gym-with-dumbbells-background-gym_481087-1725.jpg"
                } for ex in relevant_exercises[:2]
            ]
        }
    
    try:
        prompt = f"""
        You are FitAI, an elite AI Personal Trainer.
        
        User Profile: {json.dumps(user_profile, default=str)}
        Recovery Data: {json.dumps(recovery_metrics, default=str)}
        
        ADAPTATION INSTRUCTIONS from FitAI Agent:
        {adaptation_instructions}
        
        RELEVANT EXERCISES (Use these to build the plan):
        {exercises_context}
        
        CRITICAL:
        - If user is in 'home' mode, ONLY use exercises that require no equipment or very basics.
        - Follow the ADAPTATION INSTRUCTIONS strictly.
        - Return EXACTLY a JSON object matching the schema below. No conversational text.

        SCHEMA:
        {{
          "focus": "string",
          "duration_mins": int,
          "calories": int,
          "exercises": [
            {{
              "name": "string", 
              "sets": int, 
              "reps": int,
              "video_url": "string (direct link to mp4/gif or youtube link)",
              "thumbnail_url": "string (direct link to image)"
            }}
          ]
        }}
        """

        text = generate_with_fallback(prompt)
        if text is None:
            raise Exception("All Gemini models exhausted or unavailable")

        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
             text = text.split("```")[1].split("```")[0].strip()
             
        # Strict Pydantic Validation
        data_obj = json.loads(text)
        validated_plan = WorkoutPlan(**data_obj)
        return validated_plan.dict()
    except Exception as e:
        print(f"FitAI Generation Error: {e}")
        return {
            "focus": "Standard Regimen (Fallback)",
            "duration_mins": 30,
            "calories": 250,
            "exercises": [{
                "name": relevant_exercises[0]['metadata']['name'] if relevant_exercises else "Pushups", 
                "sets": 3, "reps": 10,
                "video_url": "https://mir-s3-cdn-cf.behance.net/project_modules/max_1200/31a97d100994191.5f154db23999e.gif",
                "thumbnail_url": "https://img.freepik.com/premium-photo/man-working-out-gym-with-dumbbells-background-gym_481087-1725.jpg"
            }]
        }
