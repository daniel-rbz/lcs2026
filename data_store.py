import pandas as pd
import json

EXCEL_FILE = 'data/Laurier Financial OS Data.xlsx'

class DataStore:
    def __init__(self):
        self.xl = pd.ExcelFile(EXCEL_FILE)
        
        self.ug_domestic = self.xl.parse('Undergraduate Domestic')
        self.ug_intl = self.xl.parse('Undergraduate International')
        
        # Fill NaN with empty string to avoid JSON serialization issues
        self.incidental_fees = self.xl.parse('Incidental Fees Undergraduate').fillna('')
        self.residence = self.xl.parse('Residence').fillna('')
        self.meal_plans = self.xl.parse('Meal Plans').fillna('')
        
        self.gas_prices = self.xl.parse('Gas Prices Canada')
        self.car_efficiency = self.xl.parse('Average Car L100').fillna('')
        
        # Precompute latest gas price
        # Taking the mean of the last 12 months for Toronto as an estimation
        self.current_gas_price = self.gas_prices['Toronto'].tail(12).mean() / 100 # converting cents to dollars
        
    def get_form_options(self):
        """Returns the lists of options for the frontend selectors."""
        degrees = self.ug_domestic['degree_id'].unique().tolist()
        entry_years = self.ug_domestic['entering_year'].unique().tolist()
        
        # Residence
        residences = []
        for _, row in self.residence.iterrows():
            name = f"{row['campus']} - {row['style']} ({row['room_type']})"
            residences.append({
                'id': f"{row['residence_names']}_{row['room_type']}",
                'label': name,
                'cost': float(row['total_per_term'])
            })
            
        # Meal Plans
        meals = []
        for _, row in self.meal_plans.iterrows():
            meals.append({
                'id': row['plan_name'],
                'label': f"{row['campus']} - {row['plan_name']}",
                'cost': float(row['total_cost_cad'])
            })
            
        # Cars
        cars = self.car_efficiency['Model'].unique().tolist()
        
        return {
            'degrees': degrees,
            'entry_years': entry_years,
            'residences': residences,
            'meals': meals,
            'cars': cars,
        }
        
    def calculate_tuition(self, degree_id, residency, entering_year, credits=0.5):
        """Calculates tuition based on standard parameters."""
        # For simplicity in MVP, we look up Domestic
        if residency == 'International':
            df = self.ug_intl
        else:
            df = self.ug_domestic
            
        # We find the matching tuition
        match = df[(df['degree_id'] == degree_id) & (df['entering_year'] == entering_year)]
        # If no strict match on year, fallback to 'All Years' 
        if match.empty:
            match = df[(df['degree_id'] == degree_id) & (df['entering_year'] == 'All Years')]
        
        if not match.empty:
            # Taking the base fee for 0.5 credits and extrapolating to 5.0 credits (full year)
            base_fee = match.iloc[0]['fee_cad']
            return float(base_fee * (5.0 / 0.5)) # annual
        
        return 8000.0 # Fallback estimate

    def get_annual_incidental_fees(self):
        """Estimate the annual incidental fees"""
        # A simple sum of all max_per_term multiplied by 2 terms
        try:
            total = self.incidental_fees['max_per_term'].sum() * 2
            return float(total)
        except:
            return 1000.0
            
    def get_transport_cost(self, car_model, distance_km_per_week):
        """Calculates annual transport cost based on efficiency and distance."""
        match = self.car_efficiency[self.car_efficiency['Model'] == car_model]
        if not match.empty:
            efficiency = match.iloc[0]['Combined_L_100km']
        else:
            efficiency = 8.5 # fallback avg
            
        # Annual distance
        annual_distance = distance_km_per_week * 52
        
        # cost = (distance / 100) * efficiency * gas_price
        annual_gas_cost = (annual_distance / 100.0) * float(efficiency) * float(self.current_gas_price)
        return annual_gas_cost

data_store = DataStore()
