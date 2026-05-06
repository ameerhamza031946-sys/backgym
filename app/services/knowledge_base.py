import json
import os
from app.core.database import database

async def search_exercises(query: str, n_results: int = 3):
    """
    Retrieve exercises directly from MongoDB Atlas.
    Uses keyword matching on name, description, and metadata.
    """
    try:
        # Simple text-based search simulation using regex
        # In a full production setup with Atlas, we'd use 'Search Indexes'
        matches = []
        q_parts = query.lower().split()
        
        # Fetch all exercises (dataset is small enough for this demo)
        cursor = database["exercises"].find()
        exercises = await cursor.to_list(length=200)
        
        for ex in exercises:
            score = 0
            search_text = f"{ex['name']} {ex['description']} {' '.join(ex.get('muscles', []))} {' '.join(ex.get('equipment', []))}".lower()
            
            for word in q_parts:
                if word in search_text:
                    score += 1
            
            if score > 0:
                matches.append((ex, score))
        
        # Sort by score and take top N
        matches.sort(key=lambda x: x[1], reverse=True)
        
        search_results = []
        for ex, score in matches[:n_results]:
            search_results.append({
                "id": str(ex.get('_id', ex.get('id'))),
                "document": f"{ex['name']}: {ex['description']}",
                "metadata": {
                    "name": ex['name'],
                    "difficulty": ex.get('difficulty'),
                    "equipment": json.dumps(ex.get('equipment', [])),
                    "muscles": json.dumps(ex.get('muscles', []))
                }
            })
        return search_results
            
    except Exception as e:
        print(f"MongoDB Search error: {e}")
        return []

# Legacy populate function - now handled by db_migration.py
def populate_knowledge_base():
    pass

if __name__ == "__main__":
    print("This service now uses MongoDB Atlas. Run app/core/db_migration.py to seed data.")
