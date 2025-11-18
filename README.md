# Calories - Calorie Deficit Management App

A mobile-friendly web application that helps you manage your calorie deficit for weight loss. Track your daily calorie intake, log meals, and estimate food calories to help you make informed decisions about what to eat - all from your phone!

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

You'll need Python 3.6 or higher.

```bash
# Clone the repository
git clone https://github.com/likemayo/calories.git
cd calories

# Install dependencies
pip3 install -r requirements.txt

# Run the app
python3 app.py
```

The app will start on `http://localhost:5000` (or `http://0.0.0.0:5000`).

## Usage

### Starting the App

```bash
python3 app.py
```

Then open your browser (or phone browser) to:
- **On your computer:** `http://localhost:5000`
- **On your phone (same WiFi):** `http://YOUR_COMPUTER_IP:5000`

To find your computer's IP:
```bash
# macOS/Linux
ifconfig | grep "inet "

# Windows
ipconfig
```

The app features a mobile-optimized interface with bottom navigation that makes it easy to:
- 📊 View your daily dashboard
- ➕ Log meals with multiple food items
- 🔍 Estimate calories before eating
- 👤 View and update your profile

### 1. Setting Up Your Profile

First time using the app? You'll be guided to set up your profile with:

- Weight, height, age, and gender
- Activity level (sedentary to very active)
- Weight loss goal (slow, moderate, or fast)

The app will calculate and display your:
- **BMR** (Basal Metabolic Rate): Calories you burn at rest
- **TDEE** (Total Daily Energy Expenditure): Calories you burn daily
- **Daily Target**: Your calorie goal for weight loss

### 2. Dashboard

Your main screen shows:
- Today's calorie target and consumption
- Progress bar showing how close you are to your goal
- All meals logged today with timestamps
- Real-time remaining calories

### 3. Logging Meals

Tap "Log Meal" to add what you eat:
- Enter meal name (breakfast, lunch, snack, etc.)
- Add multiple food items with **flexible portion sizes**:
  - **Serving** - typical restaurant portion (~100g)
  - **Piece** - one item (sandwich, fruit, burger, etc.)
  - **Small/Medium/Large** - relative portion sizes
  - **Cup** - 240ml for drinks (latte, juice, etc.)
  - **Bowl** - for rice, soup, cereal (~300g)
  - **Slice** - for pizza, bread, cake
  - **Grams/ML** - when you know exact measurements
- Get instant calorie calculations
- See match confidence (exact, approximate, or estimated)

**Examples:**
- "1 cup" of iced matcha latte
- "1 piece" of bulgogi egg cheese sandwich  
- "1 serving" of chicken breast
- "2 slices" of pizza

### 4. Estimating Food Calories

Before eating, check calories:
- Enter any food name and amount with **practical units**
- See if it fits your remaining budget
- Quick buttons for common foods
- Get approximate matches for similar foods

**No need to weigh everything!** Just use everyday portions like "1 cup", "1 piece", or "medium".

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

### Portion Sizes

The app uses practical, everyday portion sizes so you don't need to weigh everything:

| Unit | Equivalent | Best For |
|------|------------|----------|
| **Serving** | ~100g | Restaurant portions, protein servings |
| **Piece** | ~50g | Individual items (sandwich, fruit, burger) |
| **Small** | ~80g | Small portions |
| **Medium** | ~150g | Average portions |
| **Large** | ~250g | Large portions |
| **Cup** | 240ml | Drinks (coffee, juice, smoothies) |
| **Bowl** | ~300g | Rice, pasta, soup, cereal |
| **Slice** | ~30g | Pizza, bread, cake |
| **Handful** | ~30g | Snacks, nuts |
| **Grams/ML** | Exact | When you know precise measurements |

**Examples in Practice:**
- Iced matcha latte → "1 cup"
- Bulgogi sandwich → "1 piece"  
- Chicken breast → "1 serving" or "medium"
- Bowl of rice → "1 bowl"
- Handful of chips → "1 handful"

### Data Persistence

Your profile and meal logs are saved in the `data/` directory as JSON files. This allows multiple users to track separately if needed.

## Running Tests

The app includes comprehensive unit tests for the core calorie calculation logic:

```bash
python3 -m unittest test_calories_app.py -v
```

All tests should pass, covering:
- Calorie calculations (BMR, TDEE, targets)
- Food database lookups
- Data persistence
- Integration workflows

## Accessing from Your Phone

### Option 1: Same WiFi Network (Easiest)

1. Make sure your phone and computer are on the same WiFi
2. Start the app on your computer: `python3 app.py`
3. Find your computer's local IP address (e.g., `192.168.1.100`)
4. On your phone, open browser and go to `http://YOUR_IP:5000`

### Option 2: ngrok (Internet Access)

For access from anywhere:

```bash
# Install ngrok: https://ngrok.com/download
# Start your app
python3 app.py

# In another terminal
ngrok http 5000
```

Use the provided ngrok URL on your phone.

### Option 3: Deploy to Cloud

Deploy to free services like:
- **Railway** - `railway up`
- **Render** - Connect your GitHub repo
- **PythonAnywhere** - Free tier available

## Mobile Features

- ✅ Responsive design optimized for phones
- ✅ Touch-friendly buttons and inputs
- ✅ Bottom navigation for easy one-handed use
- ✅ No app installation needed - just use your browser
- ✅ Works offline after first load (with browser caching)
- ✅ Add to home screen for app-like experience

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

