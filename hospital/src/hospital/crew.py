from typing import List
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

from crewai_tools import (
    SerperDevTool,
    ScrapeWebsiteTool,
    DirectoryReadTool,
    FileWriterTool,
    FileReadTool,
)
from pydantic import BaseModel, Field, ConfigDict, RootModel
from dotenv import load_dotenv
from datetime import datetime
import os
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
_ = load_dotenv()

# Define the LLM to be used with better configuration
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set. Please add it to your .env file.")

# Create a more robust LLM configuration
def create_llm_instance(temperature=0.7, max_tokens=4000, max_retries=3):
    """Create LLM instance with retry logic and better configuration"""
    # Get model from environment or use default
    model_name = os.getenv("MODEL", "gemini/gemini-1.5-flash")
    
    return LLM(
        model=model_name,  # Using model from environment
        temperature=temperature,
        api_key=gemini_api_key,
        max_tokens=max_tokens,
        request_timeout=120,  # Increased timeout
        max_retries=max_retries,
        retry_delay=2  # Add delay between retries
    )

# Primary LLM instance
llm = create_llm_instance()

# ---------------------------
# Pydantic Models (Fixed)
# ---------------------------

class SurgeReport(BaseModel):
    model_config = ConfigDict(extra="forbid")
    report_type: str = Field(default="general_forecast", description="festival_forecast, pollution_risk, epidemic_alert, etc.")
    region: str = Field(default="Unknown", description="Region/area covered")
    risk_level: str = Field(default="Medium", description="Low / Medium / High")
    timeline: str = Field(default="Next 30 days", description="Timeline for predicted surge")
    affected_departments: List[str] = Field(default=["Emergency", "General Medicine"], description="Departments likely affected")
    recommendations: str = Field(default="Standard preparedness measures", description="Specific recommendations and action items")
    confidence_score: float = Field(default=0.7, description="Prediction confidence (0-1)")


class StaffingPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    department: str = Field(default="Emergency", description="Hospital department")
    required_staff: int = Field(default=10, description="Required number of staff")
    staff_type: str = Field(default="Mixed", description="Doctors, nurses, technicians")
    shift_schedule: str = Field(default="Standard 8-hour shifts", description="Recommended shift schedule")
    backup_plan: str = Field(default="On-call staff available", description="Emergency backup plan")


class StaffingPlanList(RootModel):
    root: List[StaffingPlan] = Field(default=[], description="List of staffing plans for different departments")


class InventoryRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid")
    item_category: str = Field(default="General", description="Medicines, PPE, equipment")
    item_name: str = Field(default="Basic supplies", description="Specific item name")
    required_quantity: int = Field(default=100, description="Required quantity")
    current_stock: int = Field(default=50, description="Current stock level")
    reorder_threshold: int = Field(default=25, description="Reorder threshold")
    urgency: str = Field(default="Medium", description="Low / Medium / High")


class PatientAdvisory(BaseModel):
    model_config = ConfigDict(extra="forbid")
    advisory_type: str = Field(default="general", description="Preventive, emergency, general")
    language: str = Field(default="English", description="Language of advisory")
    target_audience: str = Field(default="General public", description="Target audience")
    message: str = Field(default="Follow standard health guidelines", description="Advisory message content")
    distribution_channels: List[str] = Field(default=["Hospital website", "Social media"], description="Distribution channels")

# ---------------------------
# Enhanced Crew Definition
# ---------------------------

@CrewBase
class HospitalSurgePredictionCrew():
    """Forecasts patient surges and optimizes hospital preparedness."""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # Helper method to create agents with consistent configuration
    def _create_agent_with_fallback(self, config_key, tools, **kwargs):
        """Create agent with fallback configuration if config file is missing"""
        try:
            return Agent(
                config=self.agents_config[config_key] if hasattr(self, 'agents_config') else {},
                tools=tools,
                inject_date=True,
                allow_delegation=kwargs.get('allow_delegation', True),
                max_iter=kwargs.get('max_iter', 10),
                max_rpm=kwargs.get('max_rpm', 2),
                llm=kwargs.get('llm', llm),
                **{k: v for k, v in kwargs.items() if k not in ['allow_delegation', 'max_iter', 'max_rpm', 'llm']}
            )
        except Exception as e:
            logger.warning(f"Config file issue for {config_key}, using fallback: {e}")
            # Fallback configuration
            fallback_configs = {
                'festival_event_forecaster': {
                    'role': 'Festival and Event Surge Forecaster',
                    'goal': 'Predict patient surges during festivals and major events',
                    'backstory': 'Expert in analyzing historical data and event patterns to forecast healthcare demand.'
                },
                'pollution_climate_health_risk': {
                    'role': 'Environmental Health Risk Analyst',
                    'goal': 'Assess pollution and climate-related health risks',
                    'backstory': 'Specialist in environmental health impact assessment and air quality analysis.'
                },
                'epidemic_surveillance': {
                    'role': 'Epidemic Surveillance Specialist',
                    'goal': 'Monitor and predict epidemic outbreaks',
                    'backstory': 'Public health expert focused on disease surveillance and outbreak prediction.'
                },
                'staffing_optimizer': {
                    'role': 'Hospital Staffing Optimizer',
                    'goal': 'Optimize staff allocation based on predicted surges',
                    'backstory': 'Healthcare operations expert specializing in staff scheduling and resource allocation.'
                },
                'supply_chain_inventory': {
                    'role': 'Medical Supply Chain Manager',
                    'goal': 'Ensure adequate medical supplies and equipment',
                    'backstory': 'Supply chain expert focused on medical inventory management and procurement.'
                },
                'patient_advisory_communication': {
                    'role': 'Patient Communication Specialist',
                    'goal': 'Create effective patient advisories and communications',
                    'backstory': 'Healthcare communication expert specializing in patient education and public health messaging.'
                },
                'central_orchestrator': {
                    'role': 'Hospital Preparedness Coordinator',
                    'goal': 'Coordinate all aspects of hospital surge preparedness',
                    'backstory': 'Senior healthcare administrator with expertise in emergency preparedness and crisis management.'
                }
            }
            
            return Agent(
                **fallback_configs.get(config_key, fallback_configs['central_orchestrator']),
                tools=tools,
                inject_date=True,
                allow_delegation=kwargs.get('allow_delegation', True),
                max_iter=kwargs.get('max_iter', 10),
                max_rpm=kwargs.get('max_rpm', 2),
                llm=kwargs.get('llm', llm)
            )

    # ----------- Agents -----------
    @agent
    def festival_event_forecaster(self) -> Agent:
        return self._create_agent_with_fallback(
            'festival_event_forecaster',
            tools=[SerperDevTool(), ScrapeWebsiteTool(),
                   DirectoryReadTool('resources/forecasts'),
                   FileWriterTool(), FileReadTool()],
            reasoning=True,
            max_rpm=2
        )

    @agent
    def pollution_climate_health_risk(self) -> Agent:
        # Use a more conservative LLM configuration for this agent
        conservative_llm = create_llm_instance(temperature=0.5, max_tokens=3000, max_retries=5)
        
        return self._create_agent_with_fallback(
            'pollution_climate_health_risk',
            tools=[SerperDevTool(), ScrapeWebsiteTool(),
                   DirectoryReadTool('resources/forecasts'),
                   FileWriterTool(), FileReadTool()],
            llm=conservative_llm,  # Use more conservative LLM settings
            max_iter=10,  # Reduced from 15 to prevent timeouts
            max_rpm=1,    # More conservative rate limiting
            allow_delegation=True  # Allow delegation to other agents if needed
        )

    @agent
    def epidemic_surveillance(self) -> Agent:
        # Use a more conservative LLM configuration for this critical agent
        conservative_llm = create_llm_instance(temperature=0.3, max_tokens=3000)
        
        return self._create_agent_with_fallback(
            'epidemic_surveillance',
            tools=[SerperDevTool(), ScrapeWebsiteTool(),
                   DirectoryReadTool('resources/forecasts'),
                   FileWriterTool(), FileReadTool()],
            llm=conservative_llm,
            allow_delegation=False,
            max_iter=10,
            max_rpm=1  # Most conservative rate limiting
        )

    @agent
    def staffing_optimizer(self) -> Agent:
        return self._create_agent_with_fallback(
            'staffing_optimizer',
            tools=[DirectoryReadTool('resources/forecasts'),
                   DirectoryReadTool('resources/plans'),
                   FileWriterTool(), FileReadTool()],
            max_iter=15,
            max_rpm=2
        )

    @agent
    def supply_chain_inventory(self) -> Agent:
        return self._create_agent_with_fallback(
            'supply_chain_inventory',
            tools=[DirectoryReadTool('resources/forecasts'),
                   DirectoryReadTool('resources/plans'),
                   FileWriterTool(), FileReadTool()],
            max_iter=12,
            max_rpm=2
        )

    @agent
    def patient_advisory_communication(self) -> Agent:
        return self._create_agent_with_fallback(
            'patient_advisory_communication',
            tools=[DirectoryReadTool('resources/forecasts'),
                   DirectoryReadTool('resources/communications'),
                   FileWriterTool(), FileReadTool()],
            max_iter=8,
            max_rpm=2
        )

    @agent
    def central_orchestrator(self) -> Agent:
        return self._create_agent_with_fallback(
            'central_orchestrator',
            tools=[DirectoryReadTool('resources/forecasts'),
                   DirectoryReadTool('resources/plans'),
                   DirectoryReadTool('resources/communications'),
                   DirectoryReadTool('resources/reports'),
                   FileWriterTool(), FileReadTool()],
            reasoning=True,
            max_iter=5,
            max_rpm=2
        )

    # Helper method for task creation with fallbacks
    def _create_task_with_fallback(self, config_key, agent_method, output_model, **kwargs):
        """Create task with fallback configuration"""
        try:
            return Task(
                config=self.tasks_config[config_key] if hasattr(self, 'tasks_config') else {},
                agent=agent_method(),
                output_json=output_model,
                **kwargs
            )
        except Exception as e:
            logger.warning(f"Config file issue for task {config_key}, using fallback: {e}")
            # Fallback task descriptions
            fallback_descriptions = {
                'festival_event_analysis': """
                Analyze upcoming festivals and major events in the region to predict potential patient surges.
                Consider historical data, event scale, and regional factors.
                Provide a comprehensive surge report with risk assessment and timeline.
                """,
                'pollution_health_risk_assessment': """
                Assess current and predicted pollution levels and their potential health impacts.
                Analyze air quality data, weather patterns, and seasonal factors.
                Generate recommendations for handling pollution-related health issues.
                """,
                'epidemic_outbreak_surveillance': """
                Monitor disease surveillance data and assess epidemic outbreak risks.
                Analyze current health trends, seasonal patterns, and outbreak indicators.
                Provide early warning for potential disease outbreaks.
                """,
                'staffing_optimization_planning': """
                Based on surge predictions, create optimal staffing plans for different hospital departments.
                Consider current staffing levels, predicted patient loads, and staff availability.
                Generate detailed staffing recommendations with backup plans.
                """,
                'supply_chain_inventory_management': """
                Assess medical supply needs based on predicted surges.
                Analyze current inventory levels and forecast requirements.
                Provide procurement recommendations and inventory management plans.
                """,
                'patient_advisory_preparation': """
                Create patient advisories and public health communications.
                Develop clear, actionable messages for different scenarios.
                Consider local languages and communication channels.
                """,
                'hospital_preparedness_orchestration': """
                Coordinate all aspects of hospital preparedness based on previous analyses.
                Synthesize findings from all agents into a comprehensive preparedness plan.
                Provide executive summary and action items for hospital administration.
                """
            }
            
            return Task(
                description=fallback_descriptions.get(config_key, "Perform assigned healthcare analysis task."),
                expected_output="Detailed analysis report in the specified JSON format.",
                agent=agent_method(),
                output_json=output_model,
                **kwargs
            )

    # ----------- Tasks -----------
    @task
    def festival_event_analysis(self) -> Task:
        return self._create_task_with_fallback(
            'festival_event_analysis',
            self.festival_event_forecaster,
            SurgeReport
        )

    @task
    def pollution_health_risk_assessment(self) -> Task:
        return self._create_task_with_fallback(
            'pollution_health_risk_assessment',
            self.pollution_climate_health_risk,
            SurgeReport
        )

    @task
    def epidemic_outbreak_surveillance(self) -> Task:
        return self._create_task_with_fallback(
            'epidemic_outbreak_surveillance',
            self.epidemic_surveillance,
            SurgeReport
        )

    @task
    def staffing_optimization_planning(self) -> Task:
        return self._create_task_with_fallback(
            'staffing_optimization_planning',
            self.staffing_optimizer,
            StaffingPlanList
        )

    @task
    def supply_chain_inventory_management(self) -> Task:
        return self._create_task_with_fallback(
            'supply_chain_inventory_management',
            self.supply_chain_inventory,
            InventoryRequirement
        )

    @task
    def patient_advisory_preparation(self) -> Task:
        return self._create_task_with_fallback(
            'patient_advisory_preparation',
            self.patient_advisory_communication,
            PatientAdvisory
        )

    @task
    def hospital_preparedness_orchestration(self) -> Task:
        return self._create_task_with_fallback(
            'hospital_preparedness_orchestration',
            self.central_orchestrator,
            SurgeReport
        )

    # ----------- Crew -----------
    @crew
    def hospital_surge_crew(self) -> Crew:
        """Creates the Hospital Surge Prediction crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            planning=True,
            planning_llm=llm,
            max_rpm=1,  # Very conservative rate limiting
            memory=True,  # Enable memory for better context
            embedder={
                "provider": "google",
                "config": {
                    "api_key": gemini_api_key,
                    "model": "models/embedding-001"
                }
            }
        )

# ---------------------------
# Enhanced Error Handling
# ---------------------------

def run_with_retry(crew_instance, inputs, max_retries=3, retry_delay=5):
    """Run crew with retry logic and enhanced error handling"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1} of {max_retries}")
            # Verify API key before proceeding
            if not gemini_api_key or len(gemini_api_key.strip()) < 10:
                raise ValueError("GEMINI_API_KEY appears to be invalid or too short. Please check your .env file.")
                
            # Verify model configuration
            model_name = os.getenv("MODEL", "gemini/gemini-1.5-flash")
            logger.info(f"Using model: {model_name}")
            
            # Verify required inputs
            required_inputs = ["hospital_name", "region", "current_staffing", "administrator_name"]
            missing = [f for f in required_inputs if not inputs.get(f)]
            if missing:
                raise ValueError(f"Missing required inputs: {', '.join(missing)}")
                
            result = crew_instance.hospital_surge_crew().kickoff(inputs=inputs)
            return result
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error on attempt {attempt + 1}: {error_msg}")
            
            # Handle different error types
            if "None or empty" in error_msg:
                logger.warning("Received empty response from LLM. This could indicate an API quota issue or model availability problem.")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 1.5  # Exponential backoff
                else:
                    logger.error("Max retries exceeded. Consider checking API key quotas or model availability.")
                    raise ValueError(f"Failed after {max_retries} attempts: {error_msg}. Please verify your API key and model configuration.")
            elif "API key" in error_msg.lower() or "authentication" in error_msg.lower():
                logger.error("API key authentication error. Please check your GEMINI_API_KEY.")
                raise ValueError(f"API key error: {error_msg}. Please verify your GEMINI_API_KEY in the .env file.")
            elif "model" in error_msg.lower() and ("not found" in error_msg.lower() or "invalid" in error_msg.lower()):
                logger.error(f"Model error: {error_msg}")
                raise ValueError(f"Invalid model configuration: {error_msg}. Please check the MODEL value in your .env file.")
            else:
                logger.error(f"Non-recoverable error: {error_msg}")
                raise

# ---------------------------
# Entrypoint (CLI usage)
# ---------------------------

if __name__ == "__main__":
    inputs = {
        "hospital_name": os.getenv("HOSPITAL_NAME", "General Hospital"),
        "region": os.getenv("REGION", "Metropolitan Area"),
        "historical_data_period": os.getenv("HISTORICAL_DATA_PERIOD", "2020-2024"),
        "current_season": os.getenv("CURRENT_SEASON", "Winter"),
        "surveillance_data": os.getenv("SURVEILLANCE_DATA", "Government health bulletins and hospital records"),
        "current_staffing": os.getenv("CURRENT_STAFFING", "Standard staffing levels"),
        "budget_constraints": os.getenv("BUDGET_CONSTRAINTS", "Standard budget"),
        "current_inventory": os.getenv("CURRENT_INVENTORY", "Standard hospital inventory levels"),
        "vendor_details": os.getenv("VENDOR_DETAILS", "Approved medical suppliers"),
        "regional_languages": os.getenv("REGIONAL_LANGUAGES", "Hindi,English"),
        "administrator_name": os.getenv("ADMINISTRATOR_NAME", "Hospital Administrator"),
        "emergency_contacts": os.getenv("EMERGENCY_CONTACTS", "Standard emergency contacts"),
        "current_date": datetime.now().strftime("%Y-%m-%d"),
    }

    required = ["hospital_name", "region", "current_staffing"]
    missing = [f for f in required if not inputs[f] or inputs[f] in ["", "Standard staffing levels"]]

    if missing and inputs["current_staffing"] == "Standard staffing levels":
        logger.warning("Using default values. For better results, set proper environment variables.")

    try:
        crew = HospitalSurgePredictionCrew()
        result = run_with_retry(crew, inputs)
        print("✅ Prediction completed successfully!")
        print("📊 Result summary:", str(result)[:500] + "..." if len(str(result)) > 500 else str(result))
    except Exception as e:
        logger.error(f"Final error: {e}")
        print(f"❌ Failed after all retries: {e}")
        exit(1)