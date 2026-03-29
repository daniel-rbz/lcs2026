import requests
import json

payload = {
    'start_month': 9, 'start_year': 2026, 'terms_per_year': 2, 'years': 1,
    'campus': 'Waterloo', 'residency': 'Ontario', 'degree': 'Bachelor of Business Administration (BBA)', 'credit_load': 2.5,
    'living_mode': 'Residence', 'residence_cost': 4000, 'meal_cost': 1500,
    'monthly_rent': 0, 'monthly_food': 0,
    'transport_mode': 'Walk', 'car_model': '', 'distance_km': 0,
    'manual_gas_price': 1.5, 'extra_transit_weekly': 0,
    'starting_capital': 0, 'income_amount': 0, 'income_freq': 'weekly'
}

try:
    res = requests.post("http://127.0.0.1:8000/api/calculate", json=payload)
    print("STATUS", res.status_code)
    print("RESPONSE", res.text)
except Exception as e:
    print("CRASH", str(e))
