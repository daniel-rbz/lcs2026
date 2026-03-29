import os
import tempfile
from flask import Blueprint, jsonify, render_template, request
from data_store import data_store
from ai_parser import parse_invoice_document

bp = Blueprint('routes', __name__)

@bp.route('/')
def dashboard():
    options = data_store.get_form_options()
    return render_template('dashboard.html', options=options)

@bp.route('/api/upload', methods=['POST'])
def handle_upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if not os.environ.get("GEMINI_API_KEY"):
         return jsonify({"error": "Gemini API key not configured. Pls update .env file."}), 500
         
    try:
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)
        
        parsed_data = parse_invoice_document(temp_path)
        try: os.remove(temp_path)
        except: pass
            
        return jsonify(parsed_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.json
    
    # Timeline Variables
    start_month = int(data.get('start_month', 9))
    start_year = int(data.get('start_year', 2026))
    terms_per_year = int(data.get('terms_per_year', 2))
    years_to_calc = int(data.get('years', 1))
    
    # Core Identity
    campus = data.get('campus', 'Waterloo')
    residency = data.get('residency', 'Ontario')
    degree_id = data.get('degree', 'Bachelor of Business Administration (BBA)')
    credit_load = float(data.get('credit_load') or 2.5)
    
    # Living Situation
    living_mode = data.get('living_mode', 'Residence')
    res_cost = float(data.get('residence_cost') or 0)
    meal_cost = float(data.get('meal_cost') or 0)
    monthly_rent = float(data.get('monthly_rent') or 0)
    monthly_food = float(data.get('monthly_food') or 0)
    
    # Transportation
    transport_mode = data.get('transport_mode', 'Walk')
    car_model = data.get('car_model', 'Ford F-150')
    distance_km = float(data.get('distance_km') or 0)
    manual_gas_price = data.get('manual_gas_price')
    if manual_gas_price is not None:
        manual_gas_price = float(manual_gas_price)
    extra_transit_weekly = float(data.get('extra_transit_weekly') or 0)
    
    # Custom Ledger & Capital
    custom_costs_array = data.get('custom_costs', [])
    total_custom_costs_per_term = sum([float(item.get('cost') or 0) for item in custom_costs_array])
    capital = float(data.get('starting_capital') or 0)
    
    # Inflow
    income_val = float(data.get('income_amount') or 0)
    income_freq = data.get('income_freq', 'weekly')
    if income_freq == 'weekly': income_per_term = income_val * 16 # 4 months * 4 weeks
    elif income_freq == 'bi-weekly': income_per_term = income_val * 8
    else: income_per_term = income_val * 4

    total_terms_to_calc = terms_per_year * years_to_calc
    
    # Loop state
    current_month = start_month
    current_year = start_year
    terms_calc_this_year = 0
    
    all_terms = []
    trajectory = []
    current_savings = capital
    gross_total = 0
    total_income = 0
    
    term_labels = {
        9: "Fall Term (Sep-Dec)",
        1: "Winter Term (Jan-Apr)",
        5: "Spring/Summer Term (May-Aug)"
    }
    
    for i in range(total_terms_to_calc):
        is_first_term_of_year = (i % terms_per_year) == 0
        term_name = f"{term_labels.get(current_month, 'Academic Term')} {current_year}"

        
        # 1. Academia
        tuition = data_store.calculate_tuition(degree_id, campus, residency, credit_load)
        incidental = data_store.calculate_incidental(campus, credit_load, include_annual=is_first_term_of_year)
        
        # 2. Living
        if living_mode == 'Residence':
            rent = res_cost
            food = meal_cost
        elif living_mode == 'Renting':
            rent = monthly_rent * 4
            food = monthly_food * 4
        else: # Home
            rent = 0
            food = monthly_food * 4
            
        # 3. Transport
        if transport_mode == 'Car':
            gas = data_store.get_transport_cost(car_model, distance_km, manual_gas_price, weeks=12)
        elif transport_mode == 'Transit':
            gas = extra_transit_weekly * 12
        else:
            gas = 0
            
        term_total = tuition + incidental + rent + food + gas + total_custom_costs_per_term
        
        # Track Math
        gross_total += term_total
        total_income += income_per_term
        net_term_burn = term_total - income_per_term
        current_savings -= net_term_burn
        
        all_terms.append({
            'name': term_name,
            'tuition': float(tuition + incidental),
            'rent': float(rent),
            'food': float(food),
            'gas': float(gas),
            'total': float(term_total),
            'net_burn': float(net_term_burn)
        })
        
        trajectory.append({
            'year': term_name,
            'remaining_balance': float(current_savings)
        })
        
        # Advance chronological clock
        current_month += 4
        if current_month > 12:
            current_month -= 12
            current_year += 1
            
        terms_calc_this_year += 1
        # If they only study 2 terms per year, skip the gap term (e.g., Summer)
        if terms_per_year == 2 and terms_calc_this_year == 2:
            current_month += 4
            if current_month > 12:
                current_month -= 12
                current_year += 1
            terms_calc_this_year = 0
            
    # Trajectory Health (Score based on ending balance vs starting)
    net_total_burn = gross_total - total_income
    
    if net_total_burn <= 0:
        score = 100
    else:
        runway_segments = capital / net_total_burn
        score = min(max(int(runway_segments * 100), 0), 100)
        
    score_label = 'Critical' if score < 25 else 'Low' if score < 50 else 'Moderate' if score < 75 else 'Strong'

    return jsonify({
        'terms': all_terms,
        'trajectory': trajectory,
        'gross_cost': float(gross_total),
        'total_income': float(total_income),
        'net_burn_rate': float(net_total_burn),
        'stability_score': score,
        'stability_label': score_label,
        'runway_years': round(capital / (net_total_burn / years_to_calc), 1) if net_total_burn > 0 else 99
    })
