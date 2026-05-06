import os
import json
from app.core.database import database

# Unified data loader for Nutrition Knowledge Base - now using MongoDB Atlas
# In a full production setup, this would use Atlas Search Indexes.

async def search_nutrition_kb(query: str, limit: int = 2):
    """
    Retrieves meal data directly from MongoDB Atlas.
    """
    try:
        q_lower = query.lower()
        q_parts = q_lower.split()
        matches = []
        
        # Fetch all meals
        cursor = database["nutrition_kb"].find()
        meals = await cursor.to_list(length=200)
        
        for item in meals:
            score = 0
            search_text = f"{item['meal_name']} {item['goal']} {' '.join(item.get('tags', []))} {item['description']}".lower()
            
            # Simple keyword scoring
            for word in q_parts:
                if word in search_text:
                    score += 1
            
            if score > 0:
                matches.append((item, score))
        
        # Sort by score and return top results
        matches.sort(key=lambda x: x[1], reverse=True)
        return [m[0] for m in matches[:limit]]
    except Exception as e:
        print(f"Nutrition MongoDB Search Error: {e}")
        return []

async def get_context_for_prompt(query: str):
    """Formats retrieved data for LLM inclusion."""
    results = await search_nutrition_kb(query)
    if not results:
        return "RELEVANT MEALS FROM KNOWLEDGE BASE: No specific meal data found for this query. Suggest general healthy alternatives."
    
    context = "RELEVANT MEALS FROM KNOWLEDGE BASE:\n"
    for item in results:
        context += f"- {item['meal_name']}: {item['description']} (Goal: {item['goal']})\n"
    return context
