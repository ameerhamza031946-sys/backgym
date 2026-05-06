import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"
USER_ID = 1

def test_health():
    print("Testing Health Check...")
    res = requests.get(f"{BASE_URL.replace('/api', '')}/health")
    print(f"Status: {res.status_code}, Body: {res.json()}")

def test_user_profile():
    print("\nTesting User Profile Update...")
    payload = {
        "fitness_goal": "build_muscle",
        "nutrition_goal": "high_protein",
        "onboarding_completed": True
    }
    res = requests.put(f"{BASE_URL}/users/{USER_ID}", json=payload)
    print(f"Status: {res.status_code}, Body: {res.json()}")

def test_nutrition_logging():
    print("\nTesting Nutrition Logging...")
    # 1. Log a meal
    meal = {
        "user_id": USER_ID,
        "name": "Chicken Breast",
        "calories": 400,
        "protein": 50,
        "carbs": 0,
        "fats": 5
    }
    log_res = requests.post(f"{BASE_URL}/nutrition/log", json=meal)
    print(f"Log Meal Status: {log_res.status_code}")
    
    # 2. Check summary
    sum_res = requests.get(f"{BASE_URL}/nutrition/summary/{USER_ID}")
    data = sum_res.json()
    print(f"Summary Current Calories: {data['calories']['current']}")
    print(f"Summary Current Protein: {data['macros']['protein']['current']}")

def test_risk_alerts():
    print("\nTesting Risk Alerts...")
    res = requests.get(f"{BASE_URL}/risk/alerts/{USER_ID}")
    print(f"Status: {res.status_code}, Body: {res.json()}")

if __name__ == "__main__":
    try:
        test_health()
        test_user_profile()
        test_nutrition_logging()
        test_risk_alerts()
        print("\nAll Backend API verifications completed successfully!")
    except Exception as e:
        print(f"\nVerification failed: {e}")
        print("Make sure the backend is running at http://127.0.0.1:8000")
