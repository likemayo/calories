# Calories - Calorie Deficit Management App

A simple, easy-to-use command-line application that helps you manage your calorie deficit for weight loss. Track your daily calorie intake, log meals, and estimate food calories to help you make informed decisions about what to eat.

## Features

- **Daily Calorie Target Calculation**: Calculates your personalized daily calorie target based on:
  - Weight, height, age, and gender
  - Activity level (sedentary to very active)
  - Weight loss goals (slow, moderate, or fast)
  
- **Meal Logging**: Log your meals throughout the day with:
  - Multiple food items per meal
  - Automatic calorie calculations
  - Meal timestamps
  
- **Daily Tracking**: View your daily summary showing:
  - Total calories consumed
  - Remaining calories for the day
  - Progress toward your goal
  
- **Food Calorie Estimator**: Look up any food item to see:
  - Estimated calories
  - Whether it fits in your remaining daily budget
  - Helping you decide if you should eat it

## Installation

No external dependencies required! Just Python 3.6 or higher.

```bash
# Clone the repository
git clone https://github.com/likemayo/calories.git
cd calories

# Run the app
python3 calories_app.py
```

## Usage

### Starting the App

```bash
python3 calories_app.py
```

You'll see the main menu with 5 options:

```
==================================================
   Calorie Deficit Management App
==================================================

Menu:
1. Set up profile
2. Log meal
3. View today's summary
4. Estimate food calories
5. Exit
```

### 1. Setting Up Your Profile

First time using the app? Set up your profile to calculate your daily calorie target:

```
Enter your weight (kg): 80
Enter your height (cm): 180
Enter your age: 30
Enter your gender (male/female): male

Activity levels:
1. Sedentary (little to no exercise)
2. Light (exercise 1-3 days/week)
3. Moderate (exercise 3-5 days/week)
4. Active (exercise 6-7 days/week)
5. Very Active (intense exercise daily)
Choose activity level (1-5): 3

Weight loss rate:
1. Slow (0.25 kg/week)
2. Moderate (0.5 kg/week)
3. Fast (0.75 kg/week)
Choose weight loss rate (1-3): 2
```

The app will calculate and display your:
- **BMR** (Basal Metabolic Rate): Calories you burn at rest
- **TDEE** (Total Daily Energy Expenditure): Calories you burn daily
- **Daily Target**: Your calorie goal for weight loss

### 2. Logging Meals

Track what you eat throughout the day:

```
Meal name (e.g., breakfast, lunch, snack): breakfast

Enter food items (press Enter with empty food name to finish):
  Food: eggs
  Amount (grams): 100
  ✓ 155 calories
  
  Food: bread
  Amount (grams): 50
  ~ 132.5 calories (matched to bread)
  
  Food: [press Enter to finish]

✓ Logged breakfast: 288 calories
```

### 3. Viewing Today's Summary

Check your progress at any time:

```
=== Today's Summary (2024-11-17) ===
Daily Target: 2200 calories

Meals:
  breakfast (09:30:00): 288 cal
    - eggs (100g): 155 cal
    - bread (50g): 133 cal
  lunch (13:45:00): 650 cal
    - chicken breast (150g): 248 cal
    - rice (200g): 260 cal
    - broccoli (100g): 34 cal

Total Consumed: 938 calories
Remaining: 1262 calories
✓ 57% of daily budget remaining
```

### 4. Estimating Food Calories

Not sure if you should eat something? Check the calories first:

```
Enter food name: pizza
Amount (grams, default 100): 150

Food: pizza
Amount: 150g
Estimated Calories: 399.0
Match: Exact match in database

Your remaining calories today: 1262
✓ This fits within your remaining budget
```

## How It Works

### Calorie Calculations

The app uses scientifically-backed formulas:

1. **BMR (Basal Metabolic Rate)** - Mifflin-St Jeor Equation:
   - Male: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age + 5
   - Female: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age - 161

2. **TDEE (Total Daily Energy Expenditure)**:
   - BMR × Activity Multiplier (1.2 to 1.9)

3. **Daily Target**:
   - TDEE - Calorie Deficit (based on weight loss goal)
   - Minimum: 1200 calories (safety threshold)

### Food Database

The app includes a built-in database of common foods with calorie information per 100g. It can:
- **Exact match**: Find foods in the database
- **Approximate match**: Find similar foods (e.g., "grilled chicken" → "chicken breast")
- **Generic estimate**: Provide a reasonable estimate for unknown foods

### Data Persistence

Your profile and meal logs are saved in `calorie_data.json` in the same directory as the app. This file is created automatically and updated whenever you make changes.

## Running Tests

The app includes comprehensive unit tests:

```bash
python3 test_calories_app.py -v
```

All tests should pass, covering:
- Calorie calculations (BMR, TDEE, targets)
- Food database lookups
- Data persistence
- Integration workflows

## Tips for Success

1. **Be Consistent**: Log all your meals, even small snacks
2. **Estimate Accurately**: Use a kitchen scale for better accuracy
3. **Stay Patient**: Slow and steady weight loss is healthier
4. **Check Before Eating**: Use the estimator to make informed decisions
5. **Review Daily**: Check your summary regularly to stay on track

## Weight Loss Guidelines

- **Slow (0.25 kg/week)**: Easiest to maintain, minimal hunger
- **Moderate (0.5 kg/week)**: Good balance of results and sustainability
- **Fast (0.75 kg/week)**: More challenging, requires discipline

**Note**: Always consult with a healthcare provider before starting any weight loss program.

## License

MIT License - Feel free to use and modify!

## Contributing

Found a bug or want to add a feature? Contributions are welcome!

