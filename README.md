# Jeevan Setu - AI-Powered Patient Surge Prediction System

## Overview

Jeevan Setu is a sophisticated multi-agent AI system built on the crewAI framework, designed to predict patient surges and optimize hospital preparedness. This intelligent system analyzes various data sources including cultural events, environmental factors, epidemic trends, and hospital operations to provide comprehensive forecasts and actionable recommendations for hospital administrators.

## 🏥 System Architecture

The system consists of 7 specialized AI agents that work in sequence to analyze, predict, and recommend strategies for hospital surge management:

### 🤖 Agent Ecosystem

#### 1. Festival & Event Forecaster Agent
**Role**: Predicts patient surges linked to cultural events and festivals
**Functionality**:
- Analyzes Indian cultural calendars and public holidays
- Processes historical hospital admission patterns from `festival_admissions.csv`
- Predicts surges during major festivals (Diwali, Holi, Ganesh Chaturthi, Eid, etc.)
- Outputs forecast reports with dates, duration, intensity levels, and affected medical categories

#### 2. Pollution & Climate Health Risk Agent  
**Role**: Monitors environmental data to predict health risks
**Functionality**:
- Analyzes AQI levels, seasonal pollution patterns, and weather data
- Processes `pollution_health_data.csv` for historical trends
- Predicts respiratory, cardiac, and related health complications
- Provides region-specific health risk assessments and department impact forecasts

#### 3. Epidemic Surveillance Agent
**Role**: Tracks infectious disease trends in the region
**Functionality**:
- Monitors current health bulletins and news reports
- Analyzes `epidemic_data.csv` for disease patterns
- Focuses on COVID-19, influenza, and common infectious diseases
- Provides risk level assessments and hospital resource impact predictions

#### 4. Staffing Optimizer Agent
**Role**: Recommends optimal staffing schedules
**Functionality**:
- Analyzes surge forecasts from all prediction agents
- Processes `staffing_data.csv` for current staffing levels
- Recommends staffing levels for doctors, nurses, and technicians
- Develops emergency backup plans and shift reallocation strategies

#### 5. Supply Chain & Inventory Agent
**Role**: Manages hospital inventory needs
**Functionality**:
- Calculates demand for critical supplies based on surge predictions
- Analyzes `inventory_data.csv` for current stock levels
- Manages medicines, oxygen, PPE, ICU beds, and ventilators
- Provides procurement strategies and shortage mitigation plans

#### 6. Patient Advisory & Communication Agent
**Role**: Generates patient communication materials
**Functionality**:
- Creates advisories in multiple languages (English, Hindi, regional languages)
- Provides preventive health measures and emergency protocols
- Generates materials for SMS, WhatsApp, and hospital notice boards
- Guides patients on when to visit hospitals vs. use telemedicine

#### 7. Central Orchestrator Agent
**Role**: Integrates all predictions into unified reports
**Functionality**:
- Synthesizes outputs from all forecasting agents
- Generates comprehensive hospital preparedness reports
- Provides confidence scores and executive summaries
- Creates actionable recommendations for administrators

## 📊 Data Sources

The system processes multiple CSV data files:
- `festival_admissions.csv` - Historical patient admissions during festivals
- `pollution_health_data.csv` - Environmental and health correlation data  
- `epidemic_data.csv` - Disease outbreak and case data
- `staffing_data.csv` - Current hospital staffing information
- `inventory_data.csv` - Medical supply inventory levels

## 🚀 Installation & Setup

### Prerequisites
- Python >=3.10 <3.14
- UV package manager

### Installation Steps

1. **Install UV**:
```bash
pip install uv
```

2. **Install Dependencies**:
```bash
cd hospital
crewai install
```

3. **Environment Configuration**:
Create a `.env` file with required variables:
```bash
# Required Variables
HOSPITAL_NAME="Your Hospital Name"
REGION="Your Region"
CURRENT_STAFFING="Current staffing details"
ADMINISTRATOR_NAME="Hospital Administrator Name"


# Optional Variables
HISTORICAL_DATA_PERIOD="2020-2024"
CURRENT_SEASON="Current season"
SURVEILLANCE_DATA="Government health bulletins and hospital records"
BUDGET_CONSTRAINTS="Budget constraints details"
CURRENT_INVENTORY="Standard hospital inventory levels"
VENDOR_DETAILS="Approved medical suppliers"
REGIONAL_LANGUAGES="Hindi,English"
EMERGENCY_CONTACTS="Emergency contact details"
```

## 🎯 Usage

### Running the System
```bash
cd hospital
crewai run
```

### Output Structure
The system generates comprehensive reports in the following structure:
```
resources/
├── forecasts/
│   ├── festival_surge_forecast.md
│   ├── pollution_health_risk.md
│   └── epidemic_surveillance.md
├── plans/
│   ├── staffing_optimization.md
│   └── supply_chain_inventory.md
├── communications/
│   └── patient_advisories/
│       ├── english_advisories.md
│       ├── hindi_advisories.md
│       └── regional_advisories.md
└── reports/
    └── hospital_preparedness_report.md
```

## 🔧 Customization

### Agent Configuration
Modify `src/hospital/config/agents.yaml` to customize agent roles, goals, and backstories.

### Task Configuration  
Update `src/hospital/config/tasks.yaml` to modify task descriptions and expected outputs.

### Data Integration
Replace CSV files in `resources/data/` with your hospital's actual data for accurate predictions.

## 🛠️ Technical Features

- **API Key Rotation**: Automatic rotation between multiple Gemini API keys for reliability
- **Model Pooling**: Random model selection from configured pool for diversity
- **Error Handling**: Comprehensive error handling with retry mechanisms
- **Data Validation**: Input validation and missing field detection
- **Structured Output**: Machine-readable reports for integration with other systems

## 📈 Use Cases

1. **Festival Preparedness**: Predict patient surges during cultural events
2. **Environmental Health**: Monitor pollution-related health risks
3. **Epidemic Response**: Track and respond to disease outbreaks
4. **Staff Optimization**: Ensure adequate staffing during surge periods
5. **Supply Chain Management**: Maintain optimal inventory levels
6. **Patient Communication**: Provide timely health advisories

## 🤝 Support

For support and questions:
- 📚 [crewAI Documentation](https://docs.crewai.com)
- 🐙 [GitHub Repository](https://github.com/joaomdmoura/crewai)
- 💬 [Discord Community](https://discord.com/invite/X4JWnZnxPb)
- 💡 [Chat with Docs](https://chatg.pt/DWjSBZn)

## 📄 License

This project is built on the crewAI framework and follows its licensing terms.

---

**Built with ❤️ using crewAI - The Framework for Multi-Agent AI Systems**
