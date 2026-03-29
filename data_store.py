import pandas as pd
import numpy as np
import os

class DataStore:
    def __init__(self, excel_path="data/Laurier Financial OS Data.xlsx"):
        self.excel_path = excel_path
        
        if not os.path.exists(self.excel_path):
            print(f"Dataset not found at {self.excel_path}")
            return
            
        xl = pd.ExcelFile(self.excel_path)
        self.df_tuition = xl.parse('Undergraduate')
        self.df_fees = xl.parse('Incidental Fees Undergraduate')
        self.df_residence = xl.parse('Residence')
        self.df_meals = xl.parse('Meal Plans')
        self.df_gas = xl.parse('Gas Prices Canada')
        self.df_car = xl.parse('Average Car L100')

    def get_form_options(self):
        opts = {
            'campuses': ['Waterloo', 'Brantford'],
            'residencies': ['Ontario', 'Non-Ontario', 'International'],
            'degrees_by_campus': {'Waterloo': [], 'Brantford': []},
            'residences_by_campus': {'Waterloo': [], 'Brantford': []},
            'meals_by_campus': {'Waterloo': [], 'Brantford': []},
            'cars': self.df_car['Model'].unique().tolist()
        }
        
        # Populate Degrees
        for _, row in self.df_tuition[['campus', 'degree_id']].drop_duplicates().iterrows():
            c, deg = row['campus'], row['degree_id']
            if c == 'Waterloo' or c == 'Both':
                if deg not in opts['degrees_by_campus']['Waterloo']:
                    opts['degrees_by_campus']['Waterloo'].append(deg)
            if c == 'Brantford' or c == 'Both':
                if deg not in opts['degrees_by_campus']['Brantford']:
                    opts['degrees_by_campus']['Brantford'].append(deg)
                    
        # Populate Residences
        for _, row in self.df_residence.iterrows():
            c = row['campus']
            label = f"{row['style']} - {row['room_type']}"
            cost = row['total_per_term']
            entry = {'label': label, 'cost': cost}
            if c in opts['residences_by_campus']:
                opts['residences_by_campus'][c].append(entry)

        # Populate Meals
        for _, row in self.df_meals.iterrows():
            c = row['campus']
            entry = {'label': row['plan_name'], 'cost': row['total_cost_cad']}
            if c in opts['meals_by_campus']:
                opts['meals_by_campus'][c].append(entry)

        # Populate Gas Prices
        opts['gas_prices'] = []
        for _, row in self.df_gas.iterrows():
            if pd.isna(row['Date']): continue
            date_obj = pd.to_datetime(row['Date'])
            label = date_obj.strftime('%B %Y')
            price = float(row['Toronto']) / 100.0 # Convert cents to CAD
            opts['gas_prices'].append({'label': label, 'val': price})
            
        opts['gas_prices'].reverse() # Newest first

        return opts

    def calculate_tuition(self, degree_id, campus, residency, credit_load):
        # Filter down by degree and residency
        df_target = self.df_tuition[
            (self.df_tuition['degree_id'] == degree_id) &
            (self.df_tuition['residency'] == residency)
        ]
        
        if df_target.empty:
            return 0.0 # safety fallback

        courses_taken = float(credit_load) / 0.5
        
        # Check for precise credit load row match
        match = df_target[df_target['credit_amount'] == credit_load]
        if match.empty:
            match = df_target[df_target['credit_amount'] == str(credit_load)]

        if not match.empty:
            return float(match.iloc[0]['fee_cad'])

        # Double Degree Exceptions
        is_double = 'Double Degree' in degree_id and 'Computer Science' in degree_id
        if is_double and residency in ['Ontario', 'Non-Ontario']:
            match_5 = df_target[df_target['credit_amount'] == 0.5]
            match_max = df_target[df_target['credit_amount'] == 'Max']
            
            if not match_5.empty and not match_max.empty:
                cost_5 = float(match_5.iloc[0]['fee_cad'])
                max_fee = float(match_max.iloc[0]['fee_cad'])
                calc_fee = cost_5 * courses_taken
                return min(calc_fee, max_fee)

        # Basic 0.5 baseline multiplier rule (Applies to International, or missing exact rows)
        match_5 = df_target[df_target['credit_amount'] == 0.5]
        if not match_5.empty:
            cost_5 = float(match_5.iloc[0]['fee_cad'])
            return cost_5 * courses_taken

        return 0.0

    def calculate_incidental(self, campus, credit_load, include_annual=True):
        result = self.calculate_incidental_breakdown(campus, credit_load, include_annual)
        return result['total']

    def calculate_incidental_breakdown(self, campus, credit_load, include_annual=True):
        total_incidental = 0.0
        courses = float(credit_load) / 0.5
        line_items = []
        
        df_target = self.df_fees[self.df_fees['campus'].isin([campus, 'Both'])]
        
        for _, row in df_target.iterrows():
            per_course = float(row['per_05_credit']) if not pd.isna(row['per_05_credit']) else 0.0
            max_term = float(row['max_per_term']) if not pd.isna(row['max_per_term']) else 0.0
            freq = str(row['frequency']).strip().lower()
            fee_name = str(row['fee_name']) if 'fee_name' in row.index else 'Unnamed Fee'
            
            term_cost = per_course * courses
            if max_term > 0 and term_cost > max_term:
                term_cost = max_term
            elif per_course == 0 and max_term > 0:
                term_cost = max_term

            if freq == 'annual':
                if include_annual:
                    total_incidental += term_cost
                    line_items.append({'name': fee_name, 'amount': term_cost, 'frequency': 'Annual'})
            else:
                total_incidental += term_cost
                line_items.append({'name': fee_name, 'amount': term_cost, 'frequency': 'Per Term'})

        return {'total': total_incidental, 'items': line_items}

    def get_transport_cost(self, car_model, distance_km_per_week, manual_gas_price=None, weeks=12):
        if distance_km_per_week <= 0:
            return 0.0
        row = self.df_car[self.df_car['Model'] == car_model]
        if row.empty:
            return 0.0
        eff = row.iloc[0]['Combined_L_100km']
        
        gas_price = manual_gas_price if manual_gas_price is not None else float(self.df_gas.iloc[-1]['Toronto']) / 100.0
        
        weekly_cost = (distance_km_per_week / 100.0) * eff * gas_price
        return weekly_cost * weeks

data_store = DataStore()
