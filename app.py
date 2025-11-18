#!/usr/bin/env python3
"""
Calorie Deficit Management Web App
Mobile-friendly Flask application for tracking calories and managing weight loss goals.
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from datetime import datetime, timedelta
import os
import json
from calories_app import CalorieCalculator, FoodDatabase, CalorieTracker

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
# Ensure templates auto-reload during development
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Use session-based data file to support multiple users
def get_tracker():
    """Get CalorieTracker instance for current session."""
    user_id = session.get('user_id', 'default')
    data_file = f'data/calorie_data_{user_id}.json'
    os.makedirs('data', exist_ok=True)
    return CalorieTracker(data_file)


@app.route('/')
def index():
    """Home page - redirect to dashboard or setup."""
    tracker = get_tracker()
    if tracker.data.get('user_profile'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('setup_profile'))


@app.route('/setup', methods=['GET', 'POST'])
def setup_profile():
    """User profile setup page."""
    if request.method == 'POST':
        try:
            weight = float(request.form['weight'])
            height = float(request.form['height'])
            age = int(request.form['age'])
            gender = request.form['gender']
            activity_level = request.form['activity_level']
            weight_loss_rate = request.form['weight_loss_rate']
            ideal_weight = float(request.form['ideal_weight'])
            
            # Calculate targets
            bmr = CalorieCalculator.calculate_bmr(weight, height, age, gender)
            tdee = CalorieCalculator.calculate_tdee(bmr, activity_level)
            # Original target (kept for reference) using library function
            target = CalorieCalculator.calculate_target_calories(tdee, weight_loss_rate)
            ideal_tdee = CalorieCalculator.calculate_ideal_weight_tdee(weight, ideal_weight, height, age, gender, activity_level)
            
            # Compute intended vs actual deficit for warning visibility
            intended_daily_deficit = round(CalorieCalculator.daily_deficit_for_rate(weight_loss_rate), 1)
            raw_target = tdee - intended_daily_deficit
            # Gender-aware minimum calorie floor
            min_safe = 1200 if gender.lower() == 'female' else 1500
            actual_target = max(raw_target, min_safe)
            actual_daily_deficit = round(tdee - actual_target, 1)
            safety_floor_applied = actual_target != raw_target

            # Estimate time to goal using actual deficit
            weight_to_lose = max(0.0, weight - ideal_weight)
            calories_needed = weight_to_lose * 7700
            if actual_daily_deficit > 0 and weight_to_lose > 0:
                days_to_goal = int((calories_needed / actual_daily_deficit) + 0.9999)
                weeks_to_goal = round(days_to_goal / 7.0, 1)
                estimated_goal_date = (datetime.now() + timedelta(days=days_to_goal)).strftime('%Y-%m-%d')
            else:
                days_to_goal = None
                weeks_to_goal = None
                estimated_goal_date = None
            
            tracker = get_tracker()
            tracker.data['user_profile'] = {
                'weight': weight,
                'height': height,
                'age': age,
                'gender': gender,
                'activity_level': activity_level,
                'weight_loss_rate': weight_loss_rate,
                'ideal_weight': ideal_weight,
                'bmr': round(bmr, 1),
                'tdee': round(tdee, 1),
                # Store the actual, gender-aware daily target
                'daily_target': round(actual_target, 1),
                'ideal_weight_tdee': round(ideal_tdee, 1),
                'intended_daily_deficit': intended_daily_deficit,
                'actual_daily_deficit': actual_daily_deficit,
                'safety_floor_applied': safety_floor_applied,
                'min_safe_calories': min_safe,
                'estimated_days_to_goal': days_to_goal,
                'estimated_weeks_to_goal': weeks_to_goal,
                'estimated_goal_date': estimated_goal_date
            }
            tracker.save_data()
            
            # Store calculation details in session for results page
            session['calculation_results'] = {
                'weight': weight,
                'ideal_weight': ideal_weight,
                'weight_to_lose': round(weight - ideal_weight, 1),
                'bmr': round(bmr, 1),
                'tdee': round(tdee, 1),
                'ideal_tdee': round(ideal_tdee, 1),
                # Use gender-aware actual values on results page too
                'raw_target': round(raw_target, 1),
                'target': round(actual_target, 1),
                'deficit': round(tdee - actual_target, 1),
                'gender': gender,
                'activity_level': activity_level,
                'weight_loss_rate': weight_loss_rate,
                'intended_daily_deficit': intended_daily_deficit,
                'actual_daily_deficit': actual_daily_deficit,
                'safety_floor_applied': safety_floor_applied,
                'min_safe_calories': min_safe,
                'estimated_days_to_goal': days_to_goal,
                'estimated_weeks_to_goal': weeks_to_goal,
                'estimated_goal_date': estimated_goal_date
            }
            
            return redirect(url_for('calculation_results'))
        except (ValueError, KeyError) as e:
            return render_template('setup.html', error=str(e))
    
    return render_template('setup.html')


@app.route('/dashboard')
def dashboard():
    """Main dashboard showing today's summary."""
    tracker = get_tracker()
    
    if not tracker.data.get('user_profile'):
        return redirect(url_for('setup_profile'))
    
    today = datetime.now().strftime('%Y-%m-%d')
    profile = tracker.data['user_profile']
    target = profile['daily_target']
    
    meals = tracker.data['meals'].get(today, [])
    total_consumed = sum(meal['total_calories'] for meal in meals)
    remaining = target - total_consumed
    progress_percent = min(100, (total_consumed / target) * 100) if target > 0 else 0
    
    return render_template('dashboard.html',
                         profile=profile,
                         meals=meals,
                         total_consumed=round(total_consumed),
                         remaining=round(remaining),
                         target=round(target),
                         progress_percent=round(progress_percent, 1),
                         today=today)


@app.route('/log-meal', methods=['GET', 'POST'])
def log_meal():
    """Log a new meal."""
    tracker = get_tracker()
    
    if not tracker.data.get('user_profile'):
        return redirect(url_for('setup_profile'))
    
    if request.method == 'POST':
        meal_name = request.form['meal_name']
        foods = request.form.getlist('food[]')
        amounts = request.form.getlist('amount[]')
        units = request.form.getlist('unit[]')
        
        food_items = []
        for food, amount, unit in zip(foods, amounts, units):
            if food.strip() and amount.strip():
                try:
                    amount_g = FoodDatabase.parse_amount(amount, unit)
                    amount_display = f"{amount} {unit}"
                    estimate = FoodDatabase.estimate_calories(food, amount_g, amount_display)
                    food_items.append(estimate)
                except ValueError:
                    continue
        
        if food_items:
            total_calories = sum(item['calories'] for item in food_items)
            today = datetime.now().strftime('%Y-%m-%d')
            
            if today not in tracker.data['meals']:
                tracker.data['meals'][today] = []
            
            meal_entry = {
                'meal_name': meal_name,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'items': food_items,
                'total_calories': round(total_calories, 1)
            }
            
            tracker.data['meals'][today].append(meal_entry)
            tracker.save_data()
        
        return redirect(url_for('dashboard'))
    
    return render_template('log_meal.html')


@app.route('/estimate', methods=['GET', 'POST'])
def estimate():
    """Estimate food calories."""
    tracker = get_tracker()
    result = None
    remaining = None
    
    if not tracker.data.get('user_profile'):
        return redirect(url_for('setup_profile'))
    
    if request.method == 'POST':
        food = request.form.get('food', '')
        amount = request.form.get('amount', '1')
        unit = request.form.get('unit', 'serving')
        
        if food:
            amount_g = FoodDatabase.parse_amount(amount, unit)
            amount_display = f"{amount} {unit}"
            result = FoodDatabase.estimate_calories(food, amount_g, amount_display)
            
            # Calculate remaining calories
            today = datetime.now().strftime('%Y-%m-%d')
            target = tracker.data['user_profile']['daily_target']
            total_consumed = sum(
                meal['total_calories'] 
                for meal in tracker.data['meals'].get(today, [])
            )
            remaining = target - total_consumed
    
    return render_template('estimate.html', result=result, remaining=remaining)


@app.route('/api/food-estimate')
def api_food_estimate():
    """API endpoint for food calorie estimation."""
    food = request.args.get('food', '')
    amount = float(request.args.get('amount', 100))
    
    if not food:
        return jsonify({'error': 'Food name required'}), 400
    
    estimate = FoodDatabase.estimate_calories(food, amount)
    return jsonify(estimate)


@app.route('/calculation-results')
def calculation_results():
    """Show calculation results after profile setup."""
    results = session.get('calculation_results')
    
    if not results:
        return redirect(url_for('dashboard'))
    
    return render_template('calculation_results.html', results=results)


@app.route('/profile')
def profile():
    """View and edit profile."""
    tracker = get_tracker()
    
    if not tracker.data.get('user_profile'):
        return redirect(url_for('setup_profile'))
    
    return render_template('profile.html', profile=tracker.data['user_profile'])


@app.route('/delete-meal/<int:meal_index>')
def delete_meal(meal_index):
    """Delete a meal from today."""
    tracker = get_tracker()
    today = datetime.now().strftime('%Y-%m-%d')
    
    if today in tracker.data['meals'] and 0 <= meal_index < len(tracker.data['meals'][today]):
        del tracker.data['meals'][today][meal_index]
        tracker.save_data()
    
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    # For development - use debug mode
    app.run(host='0.0.0.0', port=5000, debug=True)
