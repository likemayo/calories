#!/usr/bin/env python3
"""
Example usage of the Calorie Deficit Management App
This demonstrates all the key features programmatically
"""

from calories_app import CalorieCalculator, FoodDatabase, CalorieTracker
from datetime import datetime
import os
import tempfile

def main():
    print("=" * 60)
    print("  CALORIE DEFICIT MANAGEMENT APP - EXAMPLE USAGE")
    print("=" * 60)
    
    # Use a temporary file for this example
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
    temp_file.close()
    
    try:
        # 1. Initialize the tracker
        print("\n1. Initializing Calorie Tracker...")
        tracker = CalorieTracker(temp_file.name)
        
        # 2. Set up a user profile
        print("\n2. Setting Up User Profile:")
        print("   - Weight: 80 kg")
        print("   - Height: 180 cm")
        print("   - Age: 30 years")
        print("   - Gender: Male")
        print("   - Activity: Moderate (exercise 3-5 days/week)")
        print("   - Goal: Moderate weight loss (0.5 kg/week)")
        
        bmr = CalorieCalculator.calculate_bmr(80, 180, 30, 'male')
        tdee = CalorieCalculator.calculate_tdee(bmr, 'moderate')
        target = CalorieCalculator.calculate_target_calories(tdee, 'moderate')
        
        tracker.data['user_profile'] = {
            'weight': 80,
            'height': 180,
            'age': 30,
            'gender': 'male',
            'activity_level': 'moderate',
            'weight_loss_rate': 'moderate',
            'bmr': round(bmr, 1),
            'tdee': round(tdee, 1),
            'daily_target': round(target, 1)
        }
        tracker.save_data()
        
        print(f"\n   ✓ BMR: {round(bmr)} calories/day")
        print(f"   ✓ TDEE: {round(tdee)} calories/day")
        print(f"   ✓ Daily Target: {round(target)} calories/day")
        print(f"   ✓ Daily Deficit: {round(tdee - target)} calories")
        
        # 3. Log breakfast
        print("\n3. Logging Breakfast:")
        today = datetime.now().strftime('%Y-%m-%d')
        breakfast_items = [
            FoodDatabase.estimate_calories('eggs', 100),
            FoodDatabase.estimate_calories('bread', 50),
            FoodDatabase.estimate_calories('banana', 120)
        ]
        
        breakfast_total = sum(item['calories'] for item in breakfast_items)
        tracker.data['meals'][today] = [{
            'meal_name': 'breakfast',
            'timestamp': datetime.now().strftime('%Y-%m-%d 08:00:00'),
            'items': breakfast_items,
            'total_calories': round(breakfast_total, 1)
        }]
        
        for item in breakfast_items:
            print(f"   - {item['food'].title()} ({item['amount_g']}g): {round(item['calories'])} cal")
        print(f"   Total: {round(breakfast_total)} calories")
        
        # 4. Log lunch
        print("\n4. Logging Lunch:")
        lunch_items = [
            FoodDatabase.estimate_calories('chicken breast', 150),
            FoodDatabase.estimate_calories('rice', 200),
            FoodDatabase.estimate_calories('broccoli', 100)
        ]
        
        lunch_total = sum(item['calories'] for item in lunch_items)
        tracker.data['meals'][today].append({
            'meal_name': 'lunch',
            'timestamp': datetime.now().strftime('%Y-%m-%d 13:00:00'),
            'items': lunch_items,
            'total_calories': round(lunch_total, 1)
        })
        
        for item in lunch_items:
            print(f"   - {item['food'].title()} ({item['amount_g']}g): {round(item['calories'])} cal")
        print(f"   Total: {round(lunch_total)} calories")
        
        # 5. Show current status
        print("\n5. Today's Summary:")
        total_consumed = breakfast_total + lunch_total
        remaining = target - total_consumed
        
        print(f"   Daily Target: {round(target)} calories")
        print(f"   Total Consumed: {round(total_consumed)} calories")
        print(f"   Remaining: {round(remaining)} calories")
        print(f"   Progress: {round((total_consumed/target)*100)}% of daily target")
        
        # 6. Check if we can eat a snack
        print("\n6. Checking Potential Snack:")
        snack_options = [
            ('apple', 150),
            ('cookie', 50),
            ('chips', 100),
            ('yogurt', 150)
        ]
        
        for food, amount in snack_options:
            estimate = FoodDatabase.estimate_calories(food, amount)
            fit_status = "✓ Fits" if estimate['calories'] <= remaining else "✗ Too much"
            print(f"   {food.title()} ({amount}g): {round(estimate['calories'])} cal - {fit_status}")
        
        # 7. Log a healthy snack
        print("\n7. Logging Healthy Snack (Apple):")
        snack_items = [FoodDatabase.estimate_calories('apple', 150)]
        snack_total = sum(item['calories'] for item in snack_items)
        
        tracker.data['meals'][today].append({
            'meal_name': 'snack',
            'timestamp': datetime.now().strftime('%Y-%m-%d 16:00:00'),
            'items': snack_items,
            'total_calories': round(snack_total, 1)
        })
        tracker.save_data()
        
        print(f"   - Apple (150g): {round(snack_total)} cal")
        
        # 8. Final summary
        print("\n8. Final Day Summary:")
        total_consumed = breakfast_total + lunch_total + snack_total
        remaining = target - total_consumed
        
        print(f"   Breakfast: {round(breakfast_total)} cal")
        print(f"   Lunch: {round(lunch_total)} cal")
        print(f"   Snack: {round(snack_total)} cal")
        print(f"   ---")
        print(f"   Total Consumed: {round(total_consumed)} cal")
        print(f"   Daily Target: {round(target)} cal")
        print(f"   Remaining: {round(remaining)} cal")
        
        if remaining < 0:
            print(f"   ⚠ Over budget by {round(abs(remaining))} calories")
        elif remaining < 200:
            print(f"   ✓ Very close to target!")
        else:
            print(f"   ✓ {round((remaining/target)*100)}% budget remaining")
        
        print("\n" + "=" * 60)
        print("  Example complete! The app is ready to use.")
        print("  Run: python3 calories_app.py")
        print("=" * 60)
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

if __name__ == '__main__':
    main()
