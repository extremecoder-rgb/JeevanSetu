import streamlit as st
import os
import json
import traceback
import warnings
import itertools
import random
from datetime import datetime
from dotenv import load_dotenv
import markdown
import pdfkit

# Filter out Pydantic deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic")

# Load environment variables
load_dotenv()

# === Rotating Gemini Key Manager ===
class GeminiKeyRotator:
    def __init__(self):
        self.keys = [
            os.getenv("GEMINI_API_KEY"),
            os.getenv("GEMINI_API_KEY_1"),
            os.getenv("GEMINI_API_KEY_2"),
            os.getenv("GEMINI_API_KEY_3"),
            os.getenv("GEMINI_API_KEY_4"),
            os.getenv("GEMINI_API_KEY_5"),
            os.getenv("GEMINI_API_KEY_6"),
            os.getenv("GEMINI_API_KEY_7"),
        ]
        self.keys = [k for k in self.keys if k]
        if not self.keys:
            raise ValueError("No valid Gemini API keys found in .env!")
        self._cycle = itertools.cycle(self.keys)

    def next_key(self):
        return next(self._cycle)

rotator = GeminiKeyRotator()

# === Helper: Select random model from MODEL_POOL ===
def get_random_model():
    models = os.getenv("MODEL_POOL", "gemini-1.5-flash").split(",")
    return f"gemini/{random.choice(models).strip()}"

# Validate at least one key exists
try:
    gemini_api_key = rotator.next_key()
except ValueError as e:
    st.error(f"❌ {str(e)}")
    st.stop()

# Import Crew
try:
    from hospital.crew import HospitalSurgePredictionCrew
except ImportError:
    try:
        from .crew import HospitalSurgePredictionCrew
    except ImportError:
        st.error("❌ Could not import HospitalSurgePredictionCrew. Please ensure the crew module is properly installed.")
        st.stop()

# Streamlit config
st.set_page_config(page_title="🏥 Hospital Surge Prediction System", layout="wide", initial_sidebar_state="expanded")

# Custom CSS
st.markdown("""
<style>
.main-header { background: linear-gradient(90deg, #1f77b4, #ff7f0e); padding: 1rem; border-radius: 10px; margin-bottom: 2rem; }
.prediction-card { background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #1f77b4; margin: 1rem 0; }
.error-card { background: #ffeaa7; padding: 1rem; border-radius: 8px; border-left: 4px solid #e17055; margin: 1rem 0; }
.success-card { background: #d1f2eb; padding: 1rem; border-radius: 8px; border-left: 4px solid #00b894; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("🏥 Hospital Surge Prediction System")
st.markdown("**AI-Powered Hospital Preparedness & Resource Optimization**")
st.markdown("Forecast patient surges, optimize staffing, manage inventory, and prepare communication strategies.")
st.markdown('</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("ℹ️ System Information")
    st.info("""
    **Features:**
    - 🎪 Festival surge prediction
    - 🌫️ Pollution health risk assessment
    - 🦠 Epidemic surveillance
    - 👥 Staff optimization
    - 📦 Supply chain management
    - 📢 Patient communication
    """)
    
    st.header("🔧 Settings")
    debug_mode = st.checkbox("Debug Mode", value=False)
    save_results = st.checkbox("Save Results to File", value=True)
    
    if st.button("🔍 Check Environment"):
        st.subheader("Environment Status")
        required_vars = ["SERPER_API_KEY", "GEMINI_API_KEY_1"]
        for var in required_vars:
            if os.getenv(var):
                st.success(f"✅ {var}")
            else:
                st.error(f"❌ {var} missing")

# Main layout
col1, col2 = st.columns([2,1])

with col1:
    with st.form("hospital_inputs"):
        st.subheader("🏥 Hospital & Regional Information")
        hospital_name = st.text_input("Hospital Name *", value=os.getenv("HOSPITAL_NAME",""))
        region = st.text_input("Region *", value=os.getenv("REGION",""))
        hospital_type = st.selectbox("Hospital Type", ["Government", "Private", "Semi-Government", "Trust/NGO"])
        hospital_capacity = st.number_input("Total Bed Capacity", min_value=10, max_value=5000, value=int(os.getenv("HOSPITAL_CAPACITY",200)))
        
        st.subheader("📅 Temporal Information")
        historical_data_period = st.text_input("Historical Data Period", value=os.getenv("HISTORICAL_DATA_PERIOD","2020-2024"))
        current_season = st.selectbox("Current Season", ["Winter", "Summer", "Monsoon", "Post-Monsoon"], index=0)
        
        st.subheader("🦠 Disease Surveillance & Monitoring")
        surveillance_data = st.text_area("Current Disease Surveillance Data", value=os.getenv("SURVEILLANCE_DATA",""), height=100)
        
        st.subheader("👥 Staffing & Human Resources")
        current_staffing = st.text_area("Current Staffing Levels *", value=os.getenv("CURRENT_STAFFING",""), height=80)
        budget_constraints = st.text_input("Budget Constraints", value=os.getenv("BUDGET_CONSTRAINTS",""))
        
        st.subheader("📦 Inventory & Supply Chain")
        current_inventory = st.text_area("Current Inventory Levels", value=os.getenv("CURRENT_INVENTORY",""), height=100)
        vendor_details = st.text_area("Vendor & Supplier Information", value=os.getenv("VENDOR_DETAILS",""), height=80)
        
        st.subheader("📢 Communication & Administration")
        regional_languages = st.text_input("Regional Languages", value=os.getenv("REGIONAL_LANGUAGES","English"))
        administrator_name = st.text_input("Administrator Name *", value=os.getenv("ADMINISTRATOR_NAME",""))
        emergency_contacts = st.text_area("Emergency Contacts", value=os.getenv("EMERGENCY_CONTACTS",""), height=100)
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        st.info(f"📅 Analysis Date: {current_date}")
        
        st.markdown("---")
        submitted = st.form_submit_button("🚀 Start Hospital Surge Prediction Analysis")

with col2:
    st.subheader("📋 Quick Guidelines")
    with st.expander("🎯 Required Fields"):
        st.markdown("""
        **Mandatory Information:**
        - Hospital Name
        - Region 
        - Current Staffing Levels
        - Administrator Name
        """)
    with st.expander("💡 Input Tips"):
        st.markdown("""
        **Staffing Format:** 25 ICU doctors, 60 nurses
        **Inventory Format:** PPE kits: 500, Ventilators: 25
        """)

# Run analysis
if submitted:
    missing_fields = []
    for field_name, value in [("Hospital Name", hospital_name), ("Region", region), ("Current Staffing", current_staffing), ("Administrator Name", administrator_name)]:
        if not value:
            missing_fields.append(field_name)
    if missing_fields:
        st.error(f"⚠️ Missing Required Fields: {', '.join(missing_fields)}")
    else:
        inputs = {
            "hospital_name": hospital_name,
            "region": region,
            "historical_data_period": historical_data_period,
            "current_season": current_season,
            "surveillance_data": surveillance_data,
            "current_staffing": current_staffing,
            "budget_constraints": budget_constraints,
            "current_inventory": current_inventory,
            "vendor_details": vendor_details,
            "regional_languages": regional_languages,
            "administrator_name": administrator_name,
            "emergency_contacts": emergency_contacts,
            "current_date": current_date,
            "api_keys": {"gemini": gemini_api_key, "serper": os.getenv("SERPER_API_KEY","")},
        }
        
        if debug_mode:
            st.json(inputs)
        
        with st.spinner("🤖 Running AI-powered hospital surge prediction analysis..."):
            try:
                crew = HospitalSurgePredictionCrew()
                result = crew.hospital_surge_crew().kickoff(inputs=inputs)
                st.success("✅ Analysis completed successfully!")
                
                st.subheader("📊 Prediction Results")
                if hasattr(result, "raw"):
                    st.text(result.raw)
                elif hasattr(result, "json"):
                    st.json(result.json)
                
                # Save JSON results
                if save_results:
                    os.makedirs("results", exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    results_file = f"results/hospital_prediction_{timestamp}.json"
                    with open(results_file,"w") as f:
                        json.dump({"inputs": inputs, "results": str(result)}, f, indent=2)
                    st.info(f"💾 Results saved to: {results_file}")
                
                # === PDF Download Integration for Windows ===
                md_file = "resources/reports/hospital_preparedness_report.md"
                pdf_file = "resources/reports/hospital_preparedness_report.pdf"
                
                # Path to wkhtmltopdf.exe
                wkhtmltopdf_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
                pdf_config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
                
                if os.path.exists(md_file):
                    with open(md_file, "r", encoding="utf-8") as f:
                        md_text = f.read()
                    html_text = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
                    html_template = f"""
                    <html>
                    <head>
                    <style>
                    body {{ font-family: Arial, sans-serif; margin: 30px; line-height: 1.5; }}
                    h1, h2, h3 {{ color: #2E86C1; }}
                    table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                    table, th, td {{ border: 1px solid black; padding: 8px; }}
                    th {{ background-color: #D6EAF8; }}
                    </style>
                    </head>
                    <body>
                    {html_text}
                    </body>
                    </html>
                    """
                    pdfkit.from_string(html_template, pdf_file, configuration=pdf_config)
                    
                    with open(pdf_file, "rb") as f:
                        pdf_bytes = f.read()
                    st.download_button(
                        label="📄 Download Hospital Preparedness Report (PDF)",
                        data=pdf_bytes,
                        file_name="hospital_preparedness_report.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.info("📁 Hospital report not generated yet. Run the analysis first.")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                if debug_mode:
                    st.text(traceback.format_exc())
