
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_personalized_workout():
    print("\n--- Testing Personalized Workout ---")
    # Test for User 1 (Elite Athlete - build_muscle)
    try:
        res = requests.get(f"{BASE_URL}/trainer/today/1")
        print(f"Status: {res.status_code}")
        print(f"Focus: {res.json().get('focus')}")
        print(f"Exercises: {len(res.json().get('exercises', []))}")
    except Exception as e:
        print(f"Error: {e}")

def test_personalized_nutrition():
    print("\n--- Testing Personalized Nutrition Chat ---")
    try:
        res = requests.post(f"{BASE_URL}/nutrition/chat", json={
            "user_id": 1,
            "message": "What should I eat for breakfast to build muscle?"
        })
        print(f"Status: {res.status_code}")
        print(f"Reply: {res.json().get('reply')[:100]}...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_personalized_workout()
    test_personalized_nutrition()
