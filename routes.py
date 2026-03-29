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
        
    # Check API key before sending
    if not os.environ.get("GEMINI_API_KEY"):
         return jsonify({"error": "Gemini API key not configured. Pls update .env file."}), 500
         
    try:
        # Save temp file
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)
        
        # Parse it
        parsed_data = parse_invoice_document(temp_path)
        
        # Cleanup
        try:
            os.remove(temp_path)
        except:
            pass
            
        return jsonify(parsed_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.json
    
    # 1. Parsing Inputs and Safely Handling Empty Strings
    degree_id = data.get('degree', 'non_business')
    residency = data.get('residency', 'Domestic')
    entry_year = data.get('entry_year', 'All Years')
    
    car_model = data.get('car_model', 'Ford F-150')
    distance_km = float(data.get('distance_km') or 0)
    
    custom_costs_array = data.get('custom_costs', [])
    total_custom_costs = sum([float(item.get('cost') or 0) for item in custom_costs_array])
    
    overrides = data.get('overrides', {})
    capital = float(data.get('starting_capital') or 0)
    horizon = data.get('horizon', 'year')

    # Baseline Costs
    base_tuition = data_store.calculate_tuition(degree_id, residency, entry_year)
    base_incidental = data_store.get_annual_incidental_fees()
    base_residence = float(data.get('residence_cost') or 0)
    base_meal = float(data.get('meal_cost') or 0)
    base_transport = data_store.get_transport_cost(car_model, distance_km)

    # Inflow Baselines
    income_val = float(data.get('income_amount') or 0)
    income_freq = data.get('income_freq', 'weekly')

    # HORIZON MATH SCALING
    if horizon == 'year':
        # Living options from Excel natively per-term, so mult by 2
        base_residence *= 2
        base_meal *= 2
        trajectory_steps = 4
        trajectory_label = 'Year'
        
        if income_freq == 'weekly': annual_income = income_val * 32
        elif income_freq == 'bi-weekly': annual_income = income_val * 16
        else: annual_income = income_val * 8
    else: 
        # Term View: Scale Annuals Down
        base_tuition /= 2
        base_incidental /= 2
        base_transport /= 2
        # Residence/Meals natively term-based, maintain 1x
        base_residence *= 1
        base_meal *= 1
        trajectory_steps = 8
        trajectory_label = 'Term'
        
        if income_freq == 'weekly': annual_income = income_val * 16
        elif income_freq == 'bi-weekly': annual_income = income_val * 8
        else: annual_income = income_val * 4
        
    # Apply Manual Overrides
    annual_tuition = float(overrides['tuition']) if overrides.get('tuition') is not None else base_tuition
    annual_incidental = float(overrides['incidental']) if overrides.get('incidental') is not None else base_incidental
    annual_living = float(overrides['living']) if overrides.get('living') is not None else (base_residence + base_meal)
    annual_transport = float(overrides['transport']) if overrides.get('transport') is not None else base_transport
    
    total_annual_cost = annual_tuition + annual_incidental + annual_living + annual_transport + total_custom_costs
    net_annual_burn = total_annual_cost - annual_income
    
    trajectory = []
    current_savings = capital
    for step in range(1, trajectory_steps + 1):
        current_savings -= net_annual_burn
        trajectory.append({
            'year': f'{trajectory_label} {step}',
            'cost': total_annual_cost,
            'income': annual_income,
            'net_burn': net_annual_burn,
            'remaining_balance': current_savings
        })
        
    # Stability Score Engine
    if net_annual_burn <= 0:
        score = 100 # Generating wealth!
    else:
        runway_segments = capital / net_annual_burn
        target_segments = trajectory_steps  # 4 years or 8 terms
        score = min(max(int((runway_segments / target_segments) * 100), 0), 100)
        
    score_label = 'Critical' if score < 25 else 'Low' if score < 50 else 'Moderate' if score < 75 else 'Strong'
        
    return jsonify({
        'annual_tuition': annual_tuition,
        'annual_incidental': annual_incidental,
        'annual_living': annual_living,
        'annual_transport': annual_transport,
        'total_custom_costs': total_custom_costs,
        'gross_annual_cost': total_annual_cost,
        'annual_income': annual_income,
        'net_burn_rate': net_annual_burn,
        'trajectory': trajectory,
        'stability_score': score,
        'stability_label': score_label,
        'runway_years': round(capital / net_annual_burn, 1) if net_annual_burn > 0 else 99
    })
