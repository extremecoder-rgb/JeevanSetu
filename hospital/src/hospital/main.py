#!/usr/bin/env python
import warnings

# ✅ Suppress both DeprecationWarnings & Pydantic-specific warnings
try:
    from pydantic import PydanticDeprecatedSince20
    warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)
except ImportError:
    pass

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*class-based.*config.*")
warnings.filterwarnings("ignore", message=".*Support for class-based.*")
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

import sys
import os
from datetime import datetime
from dotenv import load_dotenv
from hospital.crew import HospitalSurgePredictionCrew

# Load environment variables
load_dotenv()

def get_inputs():
    """Get inputs from environment variables with validation."""
    inputs = {
        "hospital_name": os.getenv("HOSPITAL_NAME", ""),
        "region": os.getenv("REGION", ""),
        "historical_data_period": os.getenv("HISTORICAL_DATA_PERIOD", "2020-2024"),
        "current_season": os.getenv("CURRENT_SEASON", ""),
        "surveillance_data": os.getenv("SURVEILLANCE_DATA", "Government health bulletins and hospital records"),
        "current_staffing": os.getenv("CURRENT_STAFFING", ""),
        "budget_constraints": os.getenv("BUDGET_CONSTRAINTS", ""),
        "current_inventory": os.getenv("CURRENT_INVENTORY", "Standard hospital inventory levels"),
        "vendor_details": os.getenv("VENDOR_DETAILS", "Approved medical suppliers"),
        "regional_languages": os.getenv("REGIONAL_LANGUAGES", "Hindi,English"),
        "administrator_name": os.getenv("ADMINISTRATOR_NAME", ""),
        "emergency_contacts": os.getenv("EMERGENCY_CONTACTS", ""),
        "current_date": datetime.now().strftime("%Y-%m-%d"),
    }
    
    required_fields = ["hospital_name", "region", "current_staffing", "administrator_name"]
    missing_fields = [f for f in required_fields if not inputs[f]]
    
    if missing_fields:
        print("❌ Error: Missing required environment variables:")
        for f in missing_fields:
            print(f"   - {f.upper()}")
        print("\n📋 Please check your .env file and ensure all required variables are set.")
        print("   Refer to the .env.example file for the complete list of required variables.")
        sys.exit(1)
    
    print("🏥 Hospital Surge Prediction System")
    print("=" * 50)
    print(f"Hospital: {inputs['hospital_name']}")
    print(f"Region: {inputs['region']}")
    print(f"Administrator: {inputs['administrator_name']}")
    print(f"Current Date: {inputs['current_date']}")
    print(f"Season: {inputs['current_season']}")
    print("=" * 50)
    
    return inputs

def run():
    """Run the hospital surge prediction crew."""
    print("🚀 Starting Hospital Surge Prediction Analysis...")
    
    try:
        gemini_api_key_1 = os.getenv("GEMINI_API_KEY_1")
        gemini_api_key_2 = os.getenv("GEMINI_API_KEY_2")
        if not gemini_api_key_1 or not gemini_api_key_2:
            print("\n❌ Error: Both GEMINI_API_KEY_1 and GEMINI_API_KEY_2 must be set in your .env file.")
            sys.exit(1)
            
        inputs = get_inputs()
        crew = HospitalSurgePredictionCrew()
        
        print("\n🔄 Initializing agents and tasks...")
        result = crew.hospital_surge_crew().kickoff(inputs=inputs)
        
        print("\n✅ Hospital surge prediction analysis completed successfully!")
        print(f"📊 Results have been saved to the reports directory.")
        return result
        
    except KeyboardInterrupt:
        print("\n⚠️  Process interrupted by user.")
        sys.exit(1)
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ An error occurred: {error_msg}")
        if "Invalid response from LLM call - None or empty" in error_msg:
            print("\n💡 This usually means an API key or model issue.")
        raise

if __name__ == "__main__":
    run()
