import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# We configure the API from the Environment Variable
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))

def parse_invoice_document(file_path):
    """
    Uploads a file to Gemini Vision API and extracts structured financial JSON.
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = """
        You are an expert financial document extractor for a student financial dashboard.
        Review the attached document (invoice, receipt, or lease). Extract the following values if they exist, and return ONLY a valid JSON object. Do not wrap in markdown tags like ```json.
        
        {
            "tuition_base": 0.00,
            "incidental_fees": 0.00,
            "books_and_supplies": 0.00,
            "residence_cost": 0.00,
            "meal_plan_cost": 0.00,
            "other_custom_costs": [
                {"name": "Expense Name", "cost": 0.00}
            ]
        }
        
        If a specific category is not found in the document, return 0.00 for it.
        Merge any random uncategorized costs into the "other_custom_costs" array.
        """
        
        # Upload using the File API, better for PDFs and Images
        uploaded_file = genai.upload_file(path=file_path)
        
        response = model.generate_content(
            [prompt, uploaded_file],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        raw_text = response.text.strip()
        
        # Clean markdown if AI accidentally includes it
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        return json.loads(raw_text.strip())
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return {"error": str(e)}
