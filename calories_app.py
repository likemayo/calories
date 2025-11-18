#!/usr/bin/env python3
"""
Calorie Deficit Management App
Helps users track their daily calorie intake and manage weight loss goals.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class CalorieCalculator:
    """Calculate daily calorie targets based on user data."""
    
    @staticmethod
    def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
        """
        Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation.
        
        Args:
            weight_kg: Weight in kilograms
            height_cm: Height in centimeters
            age: Age in years
            gender: 'male' or 'female'
        
        Returns:
            BMR in calories per day
        """
        if gender.lower() == 'male':
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        return bmr
    
    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str) -> float:
        """
        Calculate Total Daily Energy Expenditure.
        
        Args:
            bmr: Basal Metabolic Rate
            activity_level: Activity level (sedentary, light, moderate, active, very_active)
        
        Returns:
            TDEE in calories per day
        """
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        multiplier = activity_multipliers.get(activity_level.lower(), 1.2)
        return bmr * multiplier
    
    @staticmethod
    def calculate_target_calories(tdee: float, weight_loss_rate: str) -> float:
        """
        Calculate target daily calories for weight loss.
        
        Args:
            tdee: Total Daily Energy Expenditure
            weight_loss_rate: 'slow' (0.25kg/week), 'moderate' (0.5kg/week), 'fast' (0.75kg/week)
        
        Returns:
            Target daily calories
        """
        # 1 kg of fat ≈ 7700 calories
        deficit_per_week = {
            'slow': 7700 * 0.25,      # ~275 cal/day
            'moderate': 7700 * 0.5,   # ~550 cal/day
            'fast': 7700 * 0.75       # ~825 cal/day
        }
        deficit = deficit_per_week.get(weight_loss_rate.lower(), 550) / 7
        target = tdee - deficit
        # Ensure minimum safe calorie intake
        return max(target, 1200 if True else 1500)  # 1200 for female, 1500 for male

    @staticmethod
    def daily_deficit_for_rate(weight_loss_rate: str) -> float:
        """
        Return the intended daily calorie deficit for the given weight loss rate.
        slow -> ~275/day, moderate -> ~550/day, fast -> ~825/day
        """
        mapping = {
            'slow': 7700 * 0.25 / 7,
            'moderate': 7700 * 0.5 / 7,
            'fast': 7700 * 0.75 / 7,
        }
        return mapping.get(weight_loss_rate.lower(), 7700 * 0.5 / 7)
    
    @staticmethod
    def calculate_ideal_weight_tdee(current_weight: float, ideal_weight: float, height_cm: float, age: int, gender: str, activity_level: str) -> float:
        """
        Calculate TDEE at ideal weight (maintenance calories at goal).
        
        Args:
            current_weight: Current weight in kg
            ideal_weight: Target weight in kg
            height_cm: Height in centimeters
            age: Age in years
            gender: 'male' or 'female'
            activity_level: Activity level string
        
        Returns:
            TDEE at ideal weight
        """
        ideal_bmr = CalorieCalculator.calculate_bmr(ideal_weight, height_cm, age, gender)
        ideal_tdee = CalorieCalculator.calculate_tdee(ideal_bmr, activity_level)
        return ideal_tdee


class FoodDatabase:
    """Simple food calorie database with estimation capability."""
    
    # Serving size multipliers (converts to grams)
    SERVING_SIZES = {
        'small': 80,
        'medium': 150,
        'large': 250,
        'serving': 100,
        'piece': 50,
        'slice': 30,
        'cup': 240,  # ml/g for liquids
        'bowl': 300,
        'handful': 30,
        'tbsp': 15,
        'tsp': 5,
    }
    
    # Common foods with approximate calories per 100g or per serving
    FOOD_CALORIES = {
        # Proteins
        'chicken breast': 165,
        'salmon': 208,
        'eggs': 155,
        'tofu': 76,
        'beef': 250,
        'pork': 242,
        'turkey': 135,
        'tuna': 130,
        
        # Carbohydrates
        'rice': 130,
        'pasta': 131,
        'bread': 265,
        'potato': 77,
        'oats': 389,
        'quinoa': 120,
        
        # Vegetables
        'broccoli': 34,
        'spinach': 23,
        'carrot': 41,
        'tomato': 18,
        'lettuce': 15,
        'cucumber': 16,
        
        # Fruits
        'apple': 52,
        'banana': 89,
        'orange': 47,
        'strawberry': 32,
        'grape': 69,
        
        # Dairy
        'milk': 42,
        'cheese': 402,
        'yogurt': 59,
        'butter': 717,
        
        # Snacks/Others
        'pizza': 266,
        'burger': 295,
        'chocolate': 546,
        'ice cream': 207,
        'cookie': 488,
        'chips': 536,
        'soda': 41,
        'coffee': 2,
        'tea': 1,
    }
    
    @staticmethod
    def parse_amount(amount_str: str, unit: str = 'g') -> float:
        """
        Parse amount and unit to convert to grams.
        
        Args:
            amount_str: Amount as string or number
            unit: Unit type (g, ml, serving, piece, small, medium, large, etc.)
        
        Returns:
            Amount in grams
        """
        try:
            amount = float(amount_str)
        except (ValueError, TypeError):
            amount = 1
        
        unit_lower = unit.lower().strip()
        
        # Direct gram or ml input
        if unit_lower in ['g', 'gram', 'grams', 'ml', 'milliliter', 'milliliters']:
            return amount
        
        # Serving size multipliers
        if unit_lower in FoodDatabase.SERVING_SIZES:
            return amount * FoodDatabase.SERVING_SIZES[unit_lower]
        
        # Default to 100g per unit if unknown
        return amount * 100
    
    @staticmethod
    def estimate_calories(food_name: str, amount_g: float = 100, amount_display: str = None) -> Optional[Dict]:
        """
        Estimate calories for a given food.
        
        Args:
            food_name: Name of the food
            amount_g: Amount in grams (default 100g)
        
        Returns:
            Dictionary with food info and estimated calories, or None if not found
        """
        food_lower = food_name.lower().strip()
        display = amount_display if amount_display else f"{amount_g}g"
        
        # Direct match
        if food_lower in FoodDatabase.FOOD_CALORIES:
            cal_per_100g = FoodDatabase.FOOD_CALORIES[food_lower]
            return {
                'food': food_name,
                'calories': round(cal_per_100g * amount_g / 100, 1),
                'amount_g': amount_g,
                'amount_display': display,
                'match': 'exact'
            }
        
        # Partial match
        for key, cal_per_100g in FoodDatabase.FOOD_CALORIES.items():
            if key in food_lower or food_lower in key:
                return {
                    'food': food_name,
                    'calories': round(cal_per_100g * amount_g / 100, 1),
                    'amount_g': amount_g,
                    'amount_display': display,
                    'match': 'approximate',
                    'matched_to': key
                }
        
        # No match - provide general estimate
        return {
            'food': food_name,
            'calories': round(150 * amount_g / 100, 1),
            'amount_g': amount_g,
            'amount_display': display,
            'match': 'generic_estimate'
        }


class CalorieTracker:
    """Main calorie tracking application."""
    
    def __init__(self, data_file: str = 'calorie_data.json'):
        self.data_file = data_file
        self.data = self.load_data()
    
    def load_data(self) -> Dict:
        """Load user data from file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        return json.loads(content)
            except (json.JSONDecodeError, IOError):
                pass
        return {
            'user_profile': None,
            'meals': {}  # Date -> list of meals
        }
    
    def save_data(self):
        """Save user data to file."""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def setup_profile(self):
        """Set up user profile and calculate daily calorie target."""
        print("\n=== User Profile Setup ===")
        
        try:
            weight = float(input("Enter your weight (kg): "))
            height = float(input("Enter your height (cm): "))
            age = int(input("Enter your age: "))
            gender = input("Enter your gender (male/female): ").strip().lower()
            
            print("\nActivity levels:")
            print("1. Sedentary (little to no exercise)")
            print("2. Light (exercise 1-3 days/week)")
            print("3. Moderate (exercise 3-5 days/week)")
            print("4. Active (exercise 6-7 days/week)")
            print("5. Very Active (intense exercise daily)")
            
            activity_map = {
                '1': 'sedentary',
                '2': 'light',
                '3': 'moderate',
                '4': 'active',
                '5': 'very_active'
            }
            activity_choice = input("Choose activity level (1-5): ").strip()
            activity_level = activity_map.get(activity_choice, 'sedentary')
            
            print("\nWeight loss rate:")
            print("1. Slow (0.25 kg/week)")
            print("2. Moderate (0.5 kg/week)")
            print("3. Fast (0.75 kg/week)")
            
            rate_map = {
                '1': 'slow',
                '2': 'moderate',
                '3': 'fast'
            }
            rate_choice = input("Choose weight loss rate (1-3): ").strip()
            weight_loss_rate = rate_map.get(rate_choice, 'moderate')
            
            ideal_weight = float(input("\nEnter your ideal/goal weight (kg): "))
            
            # Calculate targets
            bmr = CalorieCalculator.calculate_bmr(weight, height, age, gender)
            tdee = CalorieCalculator.calculate_tdee(bmr, activity_level)
            target = CalorieCalculator.calculate_target_calories(tdee, weight_loss_rate)
            ideal_tdee = CalorieCalculator.calculate_ideal_weight_tdee(weight, ideal_weight, height, age, gender, activity_level)
            
            weight_to_lose = weight - ideal_weight
            
            self.data['user_profile'] = {
                'weight': weight,
                'height': height,
                'age': age,
                'gender': gender,
                'activity_level': activity_level,
                'weight_loss_rate': weight_loss_rate,
                'ideal_weight': ideal_weight,
                'bmr': round(bmr, 1),
                'tdee': round(tdee, 1),
                'daily_target': round(target, 1),
                'ideal_weight_tdee': round(ideal_tdee, 1)
            }
            
            self.save_data()
            
            print("\n✓ Profile saved!")
            print(f"  Current Weight: {weight} kg")
            print(f"  Goal Weight: {ideal_weight} kg")
            print(f"  Weight to Lose: {round(weight_to_lose, 1)} kg")
            print(f"\n  BMR (Current): {round(bmr)} calories/day")
            print(f"  Maintenance (Current): {round(tdee)} calories/day")
            print(f"  Maintenance (At Goal): {round(ideal_tdee)} calories/day")
            print(f"  Daily Target (Deficit): {round(target)} calories/day")
            print(f"  Daily Deficit: {round(tdee - target)} calories")
            
        except ValueError:
            print("✗ Invalid input. Please try again.")
    
    def log_meal(self):
        """Log a meal for today."""
        if not self.data.get('user_profile'):
            print("\n✗ Please set up your profile first!")
            return
        
        print("\n=== Log Meal ===")
        meal_name = input("Meal name (e.g., breakfast, lunch, snack): ").strip()
        food_items = []
        
        print("Enter food items (press Enter with empty food name to finish):")
        while True:
            food = input("  Food: ").strip()
            if not food:
                break
            
            try:
                amount = float(input("  Amount (grams): "))
                estimate = FoodDatabase.estimate_calories(food, amount)
                food_items.append(estimate)
                
                match_type = estimate['match']
                if match_type == 'exact':
                    print(f"  ✓ {estimate['calories']} calories")
                elif match_type == 'approximate':
                    print(f"  ~ {estimate['calories']} calories (matched to {estimate['matched_to']})")
                else:
                    print(f"  ? {estimate['calories']} calories (generic estimate)")
            except ValueError:
                print("  ✗ Invalid amount")
        
        if not food_items:
            print("✗ No food items entered")
            return
        
        total_calories = sum(item['calories'] for item in food_items)
        
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.data['meals']:
            self.data['meals'][today] = []
        
        meal_entry = {
            'meal_name': meal_name,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'items': food_items,
            'total_calories': round(total_calories, 1)
        }
        
        self.data['meals'][today].append(meal_entry)
        self.save_data()
        
        print(f"\n✓ Logged {meal_name}: {round(total_calories)} calories")
    
    def show_today(self):
        """Show today's calorie summary."""
        if not self.data.get('user_profile'):
            print("\n✗ Please set up your profile first!")
            return
        
        today = datetime.now().strftime('%Y-%m-%d')
        target = self.data['user_profile']['daily_target']
        
        print(f"\n=== Today's Summary ({today}) ===")
        print(f"Daily Target: {round(target)} calories")
        
        if today not in self.data['meals'] or not self.data['meals'][today]:
            print("No meals logged yet")
            print(f"Remaining: {round(target)} calories")
            return
        
        print("\nMeals:")
        total_consumed = 0
        for meal in self.data['meals'][today]:
            print(f"  {meal['meal_name']} ({meal['timestamp'].split()[1]}): {round(meal['total_calories'])} cal")
            for item in meal['items']:
                print(f"    - {item['food']} ({item['amount_g']}g): {round(item['calories'])} cal")
            total_consumed += meal['total_calories']
        
        remaining = target - total_consumed
        print(f"\nTotal Consumed: {round(total_consumed)} calories")
        print(f"Remaining: {round(remaining)} calories")
        
        if remaining < 0:
            print(f"⚠ Over target by {round(abs(remaining))} calories")
        elif remaining < target * 0.2:
            print(f"✓ Close to target!")
        else:
            print(f"✓ {round((remaining/target)*100)}% of daily budget remaining")
    
    def estimate_food(self):
        """Estimate calories for a food item."""
        print("\n=== Food Calorie Estimator ===")
        food = input("Enter food name: ").strip()
        
        if not food:
            return
        
        try:
            amount = float(input("Amount (grams, default 100): ") or "100")
        except ValueError:
            amount = 100
        
        estimate = FoodDatabase.estimate_calories(food, amount)
        
        print(f"\nFood: {estimate['food']}")
        print(f"Amount: {estimate['amount_g']}g")
        print(f"Estimated Calories: {estimate['calories']}")
        
        match_type = estimate['match']
        if match_type == 'exact':
            print("Match: Exact match in database")
        elif match_type == 'approximate':
            print(f"Match: Approximate (similar to {estimate['matched_to']})")
        else:
            print("Match: Generic estimate (food not in database)")
        
        # Show decision help
        if self.data.get('user_profile'):
            today = datetime.now().strftime('%Y-%m-%d')
            target = self.data['user_profile']['daily_target']
            total_consumed = 0
            
            if today in self.data['meals']:
                for meal in self.data['meals'][today]:
                    total_consumed += meal['total_calories']
            
            remaining = target - total_consumed
            print(f"\nYour remaining calories today: {round(remaining)}")
            
            if estimate['calories'] <= remaining:
                print(f"✓ This fits within your remaining budget")
            else:
                print(f"⚠ This would exceed your remaining budget by {round(estimate['calories'] - remaining)} calories")
    
    def run(self):
        """Main application loop."""
        print("=" * 50)
        print("   Calorie Deficit Management App")
        print("=" * 50)
        
        while True:
            print("\nMenu:")
            print("1. Set up profile")
            print("2. Log meal")
            print("3. View today's summary")
            print("4. Estimate food calories")
            print("5. Exit")
            
            choice = input("\nChoose an option (1-5): ").strip()
            
            if choice == '1':
                self.setup_profile()
            elif choice == '2':
                self.log_meal()
            elif choice == '3':
                self.show_today()
            elif choice == '4':
                self.estimate_food()
            elif choice == '5':
                print("\nGoodbye! Keep tracking your calories! 💪")
                break
            else:
                print("\n✗ Invalid option")


def main():
    """Entry point for the application."""
    tracker = CalorieTracker()
    tracker.run()


if __name__ == '__main__':
    main()
