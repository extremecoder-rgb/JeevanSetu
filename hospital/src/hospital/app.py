import streamlit as st
import os
import json
import traceback
import warnings
from datetime import datetime
from dotenv import load_dotenv

# Filter out Pydantic deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic")

# Load environment variables
load_dotenv()

try:
    # Try absolute import first
    from hospital.crew import HospitalSurgePredictionCrew
except ImportError:
    try:
        # Try relative import as fallback
        from .crew import HospitalSurgePredictionCrew
    except ImportError:
        st.error("❌ Could not import HospitalSurgePredictionCrew. Please ensure the crew module is properly installed.")
        st.stop()

# Streamlit configuration
st.set_page_config(
    page_title="🏥 Hospital Surge Prediction System", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .prediction-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .error-card {
        background: #ffeaa7;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #e17055;
        margin: 1rem 0;
    }
    .success-card {
        background: #d1f2eb;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #00b894;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("🏥 Hospital Surge Prediction System")
st.markdown("**AI-Powered Hospital Preparedness & Resource Optimization**")
st.markdown("Forecast patient surges, optimize staffing, manage inventory, and prepare communication strategies.")
st.markdown('</div>', unsafe_allow_html=True)

# Sidebar for quick info and settings
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
        required_vars = ["SERPER_API_KEY", "GOOGLE_API_KEY"]
        for var in required_vars:
            if os.getenv(var):
                st.success(f"✅ {var}")
            else:
                st.error(f"❌ {var} missing")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Input form
    with st.form("hospital_inputs"):
        st.subheader("🏥 Hospital & Regional Information")
        
        # Basic hospital info
        col_a, col_b = st.columns(2)
        with col_a:
            hospital_name = st.text_input(
                "Hospital Name *", 
                value=os.getenv("HOSPITAL_NAME", ""),
                help="Official name of the hospital"
            )
            region = st.text_input(
                "Region *", 
                value=os.getenv("REGION", ""),
                help="City, state, or geographical region"
            )
        
        with col_b:
            hospital_type = st.selectbox(
                "Hospital Type",
                ["Government", "Private", "Semi-Government", "Trust/NGO"],
                help="Type of healthcare institution"
            )
            hospital_capacity = st.number_input(
                "Total Bed Capacity",
                min_value=10,
                max_value=5000,
                value=int(os.getenv("HOSPITAL_CAPACITY", 200)),
                help="Total number of beds in the hospital"
            )
        
        # Time and seasonal info
        st.subheader("📅 Temporal Information")
        col_c, col_d = st.columns(2)
        with col_c:
            historical_data_period = st.text_input(
                "Historical Data Period", 
                value=os.getenv("HISTORICAL_DATA_PERIOD", "2020-2024"),
                help="Period for historical analysis (e.g., 2020-2024)"
            )
        with col_d:
            current_season = st.selectbox(
                "Current Season", 
                ["Winter", "Summer", "Monsoon", "Post-Monsoon"],
                index=["Winter", "Summer", "Monsoon", "Post-Monsoon"].index(os.getenv("CURRENT_SEASON", "Winter")) if os.getenv("CURRENT_SEASON") in ["Winter", "Summer", "Monsoon", "Post-Monsoon"] else 0
            )
        
        # Surveillance and monitoring
        st.subheader("🦠 Disease Surveillance & Monitoring")
        surveillance_data = st.text_area(
            "Current Disease Surveillance Data", 
            value=os.getenv("SURVEILLANCE_DATA", ""),
            placeholder="Government health bulletins, case trends, outbreak reports, etc.",
            height=100,
            help="Current epidemic/endemic disease data and trends"
        )
        
        # Staffing information
        st.subheader("👥 Staffing & Human Resources")
        current_staffing = st.text_area(
            "Current Staffing Levels *", 
            value=os.getenv("CURRENT_STAFFING", ""),
            placeholder="Example: 50 doctors, 120 nurses, 30 technicians, 20 support staff",
            height=80,
            help="Current staffing by category and department"
        )
        budget_constraints = st.text_input(
            "Budget Constraints", 
            value=os.getenv("BUDGET_CONSTRAINTS", ""),
            placeholder="Example: ₹50 lakhs emergency budget, limited overtime pay",
            help="Financial limitations and budget allocations"
        )
        
        # Inventory and supply chain
        st.subheader("📦 Inventory & Supply Chain")
        current_inventory = st.text_area(
            "Current Inventory Levels", 
            value=os.getenv("CURRENT_INVENTORY", ""),
            placeholder="Example: PPE kits: 500, Ventilators: 25, Oxygen cylinders: 200, ICU beds: 50",
            height=100,
            help="Current stock levels of critical medical supplies and equipment"
        )
        vendor_details = st.text_area(
            "Vendor & Supplier Information", 
            value=os.getenv("VENDOR_DETAILS", ""),
            placeholder="Vendor names, contact details, lead times, emergency procurement contacts",
            height=80,
            help="Supply chain and vendor contact information"
        )
        
        # Communication and administration
        st.subheader("📢 Communication & Administration")
        col_e, col_f = st.columns(2)
        with col_e:
            regional_languages = st.text_input(
                "Regional Languages", 
                value=os.getenv("REGIONAL_LANGUAGES", "Hindi,English"),
                help="Languages for patient advisories (comma-separated)"
            )
            administrator_name = st.text_input(
                "Administrator Name *", 
                value=os.getenv("ADMINISTRATOR_NAME", ""),
                help="Name of the chief medical officer or administrator"
            )
        
        with col_f:
            emergency_contacts = st.text_area(
                "Emergency Contacts", 
                value=os.getenv("EMERGENCY_CONTACTS", ""),
                placeholder="Emergency services, district health officer, backup contacts",
                height=100,
                help="Critical contact information for emergency situations"
            )
        
        # Auto-populate current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        st.info(f"📅 Analysis Date: {current_date}")
        
        # Form submission
        st.markdown("---")
        submitted = st.form_submit_button(
            "🚀 Start Hospital Surge Prediction Analysis", 
            use_container_width=True,
            type="primary"
        )

with col2:
    st.subheader("📋 Quick Guidelines")
    
    with st.expander("🎯 Required Fields"):
        st.markdown("""
        **Mandatory Information:**
        - Hospital Name
        - Region 
        - Current Staffing Levels
        - Administrator Name
        
        *These fields are essential for generating accurate predictions.*
        """)
    
    with st.expander("💡 Input Tips"):
        st.markdown("""
        **Staffing Format:**
        - Use clear categories: doctors, nurses, technicians
        - Include numbers: "25 ICU doctors, 60 nurses"
        
        **Inventory Format:**
        - List critical items with quantities
        - Include equipment and supplies
        - Mention current stock levels
        """)
    
    with st.expander("🔍 What We Analyze"):
        st.markdown("""
        **System Predictions:**
        - Festival-related surge forecasts
        - Pollution-induced health risks
        - Epidemic outbreak surveillance
        - Optimal staffing schedules
        - Supply chain requirements
        - Patient communication strategies
        """)

# Results section
if submitted:
    # Validation
    required_fields = [
        ("Hospital Name", hospital_name),
        ("Region", region), 
        ("Current Staffing", current_staffing),
        ("Administrator Name", administrator_name)
    ]
    
    missing_fields = [field[0] for field in required_fields if not field[1]]
    
    if missing_fields:
        st.markdown('<div class="error-card">', unsafe_allow_html=True)
        st.error(f"⚠️ Missing Required Fields: {', '.join(missing_fields)}")
        st.markdown("Please fill in all required fields marked with * to proceed.")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Prepare inputs
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
        }
        
        # Debug information
        if debug_mode:
            with st.expander("🔧 Debug Information"):
                st.json(inputs)
        
        # Run prediction
        with st.spinner("🤖 Running AI-powered hospital surge prediction analysis..."):
            try:
                # Initialize and run crew
                crew = HospitalSurgePredictionCrew()
                result = crew.hospital_surge_crew().kickoff(inputs=inputs)
                
                # Success message
                st.markdown('<div class="success-card">', unsafe_allow_html=True)
                st.success("✅ Hospital surge prediction analysis completed successfully!")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Display results
                st.subheader("📊 Prediction Results")
                
                # Create tabs for different result sections
                tab1, tab2, tab3, tab4 = st.tabs(["📈 Summary", "📋 Detailed Results", "📁 File Outputs", "🔗 Actions"])
                
                with tab1:
                    st.markdown('<div class="prediction-card">', unsafe_allow_html=True)
                    if hasattr(result, 'raw'):
                        st.markdown("### Executive Summary")
                        st.write(result.raw)
                    else:
                        st.write("**Analysis completed successfully.** Check the detailed results and file outputs for comprehensive findings.")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with tab2:
                    st.markdown("### Complete Analysis Output")
                    if hasattr(result, 'json'):
                        st.json(result.json)
                    elif hasattr(result, 'raw'):
                        st.text(result.raw)
                    else:
                        st.write(str(result))
                
                with tab3:
                    st.markdown("### Generated Files")
                    expected_files = [
                        "resources/forecasts/festival_surge_forecast.md",
                        "resources/forecasts/pollution_health_risk.md",
                        "resources/forecasts/epidemic_surveillance.md",
                        "resources/plans/staffing_optimization.md",
                        "resources/plans/supply_chain_inventory.md",
                        "resources/communications/patient_advisories/",
                        "resources/reports/hospital_preparedness_report.md"
                    ]
                    
                    for file_path in expected_files:
                        if os.path.exists(file_path):
                            st.success(f"✅ {file_path}")
                        else:
                            st.info(f"📁 {file_path} (check if generated)")
                
                with tab4:
                    st.markdown("### Recommended Actions")
                    st.markdown("""
                    **Next Steps:**
                    1. 📋 Review the generated hospital preparedness report
                    2. 👥 Share staffing recommendations with HR department
                    3. 📦 Initiate supply chain procurement based on inventory analysis
                    4. 📢 Distribute patient advisories through recommended channels
                    5. 🔄 Schedule regular re-analysis based on changing conditions
                    """)
                    
                    if st.button("📧 Generate Summary Email"):
                        st.info("Email summary feature will be implemented in the next version.")
                
                # Save results if requested
                if save_results:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    results_file = f"results/hospital_prediction_{timestamp}.json"
                    
                    try:
                        os.makedirs("results", exist_ok=True)
                        with open(results_file, 'w') as f:
                            json.dump({
                                "inputs": inputs,
                                "results": str(result),
                                "timestamp": timestamp
                            }, f, indent=2)
                        st.info(f"💾 Results saved to: {results_file}")
                    except Exception as save_error:
                        st.warning(f"Could not save results: {save_error}")
                
            except Exception as e:
                st.markdown('<div class="error-card">', unsafe_allow_html=True)
                st.error(f"❌ An error occurred during analysis: {str(e)}")
                
                if debug_mode:
                    st.text("Full error traceback:")
                    st.text(traceback.format_exc())
                    
                st.markdown("""
                **Troubleshooting Tips:**
                - Check if all required API keys are set in your .env file
                - Ensure the crew module is properly installed
                - Verify network connectivity for web search tools
                - Try reducing the complexity of input data
                """)
                st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    🏥 Hospital Surge Prediction System | Powered by CrewAI & Gemini | 
    <a href='https://github.com/your-repo' target='_blank'>Documentation</a>
</div>
""", unsafe_allow_html=True)