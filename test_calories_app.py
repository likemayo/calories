#!/usr/bin/env python3
"""
Unit tests for the Calorie Deficit Management App
"""

import unittest
import json
import os
import tempfile
from calories_app import CalorieCalculator, FoodDatabase, CalorieTracker


class TestCalorieCalculator(unittest.TestCase):
    """Test the CalorieCalculator class."""
    
    def test_bmr_male(self):
        """Test BMR calculation for males."""
        bmr = CalorieCalculator.calculate_bmr(80, 180, 30, 'male')
        # Expected: 10*80 + 6.25*180 - 5*30 + 5 = 800 + 1125 - 150 + 5 = 1780
        self.assertAlmostEqual(bmr, 1780, delta=1)
    
    def test_bmr_female(self):
        """Test BMR calculation for females."""
        bmr = CalorieCalculator.calculate_bmr(60, 165, 25, 'female')
        # Expected: 10*60 + 6.25*165 - 5*25 - 161 = 600 + 1031.25 - 125 - 161 = 1345.25
        self.assertAlmostEqual(bmr, 1345.25, delta=1)
    
    def test_tdee_sedentary(self):
        """Test TDEE calculation for sedentary activity."""
        bmr = 1500
        tdee = CalorieCalculator.calculate_tdee(bmr, 'sedentary')
        self.assertAlmostEqual(tdee, 1500 * 1.2, delta=1)
    
    def test_tdee_moderate(self):
        """Test TDEE calculation for moderate activity."""
        bmr = 1500
        tdee = CalorieCalculator.calculate_tdee(bmr, 'moderate')
        self.assertAlmostEqual(tdee, 1500 * 1.55, delta=1)
    
    def test_target_calories_moderate_loss(self):
        """Test target calorie calculation for moderate weight loss."""
        tdee = 2000
        target = CalorieCalculator.calculate_target_calories(tdee, 'moderate')
        # Expected deficit: ~550 cal/day
        self.assertAlmostEqual(target, 2000 - 550, delta=50)
    
    def test_target_calories_minimum(self):
        """Test that target calories don't go below minimum safe level."""
        tdee = 1300  # Very low TDEE
        target = CalorieCalculator.calculate_target_calories(tdee, 'fast')
        self.assertGreaterEqual(target, 1200)  # Minimum safe calories


class TestFoodDatabase(unittest.TestCase):
    """Test the FoodDatabase class."""
    
    def test_exact_match(self):
        """Test exact food match."""
        result = FoodDatabase.estimate_calories('chicken breast', 100)
        self.assertIsNotNone(result)
        self.assertEqual(result['match'], 'exact')
        self.assertEqual(result['calories'], 165)
    
    def test_amount_scaling(self):
        """Test calorie scaling with different amounts."""
        result = FoodDatabase.estimate_calories('rice', 200)
        self.assertIsNotNone(result)
        self.assertEqual(result['calories'], 130 * 2)
    
    def test_partial_match(self):
        """Test partial food match."""
        result = FoodDatabase.estimate_calories('grilled chicken breast', 100)
        self.assertIsNotNone(result)
        self.assertEqual(result['match'], 'approximate')
        self.assertIn('matched_to', result)
    
    def test_no_match(self):
        """Test unknown food generic estimate."""
        result = FoodDatabase.estimate_calories('unknown exotic food', 100)
        self.assertIsNotNone(result)
        self.assertEqual(result['match'], 'generic_estimate')
        self.assertEqual(result['calories'], 150)  # Generic estimate
    
    def test_case_insensitive(self):
        """Test that food matching is case insensitive."""
        result1 = FoodDatabase.estimate_calories('BANANA', 100)
        result2 = FoodDatabase.estimate_calories('banana', 100)
        self.assertEqual(result1['calories'], result2['calories'])


class TestCalorieTracker(unittest.TestCase):
    """Test the CalorieTracker class."""
    
    def setUp(self):
        """Set up test fixture."""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.tracker = CalorieTracker(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test fixture."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_initial_data_structure(self):
        """Test initial data structure."""
        self.assertIn('user_profile', self.tracker.data)
        self.assertIn('meals', self.tracker.data)
        self.assertIsNone(self.tracker.data['user_profile'])
        self.assertEqual(self.tracker.data['meals'], {})
    
    def test_save_and_load_data(self):
        """Test saving and loading data."""
        self.tracker.data['user_profile'] = {
            'weight': 70,
            'height': 175,
            'age': 30,
            'daily_target': 1800
        }
        self.tracker.save_data()
        
        # Load data in a new tracker instance
        new_tracker = CalorieTracker(self.temp_file.name)
        self.assertIsNotNone(new_tracker.data['user_profile'])
        self.assertEqual(new_tracker.data['user_profile']['weight'], 70)
    
    def test_profile_calculation(self):
        """Test that profile includes calculated values."""
        self.tracker.data['user_profile'] = {
            'weight': 80,
            'height': 180,
            'age': 30,
            'gender': 'male',
            'activity_level': 'moderate',
            'weight_loss_rate': 'moderate',
            'bmr': 1780,
            'tdee': 2759,
            'daily_target': 2209
        }
        
        profile = self.tracker.data['user_profile']
        self.assertIn('bmr', profile)
        self.assertIn('tdee', profile)
        self.assertIn('daily_target', profile)
        self.assertGreater(profile['tdee'], profile['bmr'])
        self.assertLess(profile['daily_target'], profile['tdee'])


class TestIntegration(unittest.TestCase):
    """Integration tests for the full application."""
    
    def setUp(self):
        """Set up test fixture."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.tracker = CalorieTracker(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test fixture."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_complete_workflow(self):
        """Test a complete workflow from profile setup to meal logging."""
        # Set up profile
        self.tracker.data['user_profile'] = {
            'weight': 80,
            'height': 180,
            'age': 30,
            'gender': 'male',
            'activity_level': 'moderate',
            'weight_loss_rate': 'moderate',
            'bmr': 1780,
            'tdee': 2759,
            'daily_target': 2200
        }
        
        # Log a meal
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        
        meal_entry = {
            'meal_name': 'breakfast',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'items': [
                FoodDatabase.estimate_calories('eggs', 100),
                FoodDatabase.estimate_calories('bread', 50)
            ],
            'total_calories': 155 + 132.5
        }
        
        self.tracker.data['meals'][today] = [meal_entry]
        self.tracker.save_data()
        
        # Verify data persists
        new_tracker = CalorieTracker(self.temp_file.name)
        self.assertIn(today, new_tracker.data['meals'])
        self.assertEqual(len(new_tracker.data['meals'][today]), 1)
        self.assertEqual(new_tracker.data['meals'][today][0]['meal_name'], 'breakfast')


if __name__ == '__main__':
    unittest.main()
