import json
from datetime import datetime, timedelta
from typing import List, Dict

class AdaptationAgent:
    def __init__(self, db_session=None):
        self.db = db_session

    def analyze_performance(self, user_id: int):
        """
        Analyze the user's recent workout history to determine if a plan 
        should be made harder, easier, or keep the same.
        """
        # For the hackathon demo, we simulate fetching from DB if session is not active
        # In a real app, we'd query: Session.query(WorkoutSession).filter_by(user_id=user_id).order_by(date.desc()).limit(3)
        
        # Simulated recent history
        # status: 'COMPLETED' | 'PARTIAL' | 'SKIPPED'
        recent_sessions = [
            {"date": "2026-03-01", "completion": 1.0, "intensity_score": 0.8},
            {"date": "2026-02-28", "completion": 1.0, "intensity_score": 0.85},
            {"date": "2026-02-27", "completion": 0.9, "intensity_score": 0.8},
        ]
        
        avg_completion = sum(s['completion'] for s in recent_sessions) / len(recent_sessions)
        
        if avg_completion > 0.95:
            return "INCREASE_INTENSITY"  # User is crushing it
        elif avg_completion < 0.6:
            return "DECREASE_INTENSITY"  # User is struggling
        else:
            return "MAINTAIN"

    def check_injury_risk(self, mobility_results: Dict):
        """
        Check if the last mobility test indicates a high risk of injury.
        """
        if not mobility_results:
            return "NORMAL"
            
        # Example logic for the "Hip Adduction" test implemented earlier
        # If the angle is very restricted, suggest a 'Recovery' day
        score = mobility_results.get("score", 100)
        if score < 60:
            return "HIGH_RISK"
        return "NORMAL"

    def get_adaptation_prompt(self, user_profile: Dict):
        """
        Returns a prompt snippet for the LLM based on the agent's analysis.
        """
        perf = self.analyze_performance(user_profile.get("id"))
        risk = self.check_injury_risk(user_profile.get("mobility_test_results"))
        
        instructions = []
        if risk == "HIGH_RISK":
            instructions.append("The user has restricted mobility today. Focus on active recovery and stretching. Avoid heavy compound movements.")
        
        if perf == "INCREASE_INTENSITY":
            instructions.append("The user has been performing exceptionally well. Apply progressive overload: increase weight by 5% or add 2 more reps per set compared to previous sessions.")
        elif perf == "DECREASE_INTENSITY":
            instructions.append("The user has missed some targets recently. Reduce volume by 10% and focus on form perfection.")
            
        return " ".join(instructions)

# Singleton for easy access
agent = AdaptationAgent()
