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
from pydantic import BaseModel, Field, ConfigDict
from dotenv import load_dotenv
from datetime import datetime
import os

# Load environment variables
_ = load_dotenv()

# Define the LLM to be used
llm = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.4,  # Reduced temperature for more deterministic responses
    api_key=os.getenv("GEMINI_API_KEY"),
    max_tokens=2048,  # Reduced token limit to avoid empty responses
    request_timeout=60  # Increased timeout for API requests
)

# ---------------------------
# Pydantic Models
# ---------------------------

class SurgeReport(BaseModel):
    model_config = ConfigDict(extra="forbid")
    report_type: str = Field(..., description="festival_forecast, pollution_risk, epidemic_alert, etc.")
    region: str = Field(..., description="Region/area covered")
    risk_level: str = Field(..., description="Low / Medium / High")
    timeline: str = Field(..., description="Timeline for predicted surge")
    affected_departments: List[str] = Field(..., description="Departments likely affected")
    recommendations: str = Field(..., description="Specific recommendations and action items")
    confidence_score: float = Field(..., description="Prediction confidence (0-1)")


class StaffingPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    department: str = Field(..., description="Hospital department")
    required_staff: int = Field(..., description="Required number of staff")
    staff_type: str = Field(..., description="Doctors, nurses, technicians")
    shift_schedule: str = Field(..., description="Recommended shift schedule")
    backup_plan: str = Field(..., description="Emergency backup plan")


class InventoryRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid")
    item_category: str = Field(..., description="Medicines, PPE, equipment")
    item_name: str = Field(..., description="Specific item name")
    required_quantity: int = Field(..., description="Required quantity")
    current_stock: int = Field(..., description="Current stock level")
    reorder_threshold: int = Field(..., description="Reorder threshold")
    urgency: str = Field(..., description="Low / Medium / High")


class PatientAdvisory(BaseModel):
    model_config = ConfigDict(extra="forbid")
    advisory_type: str = Field(..., description="Preventive, emergency, general")
    language: str = Field(..., description="Language of advisory")
    target_audience: str = Field(..., description="Target audience")
    message: str = Field(..., description="Advisory message content")
    distribution_channels: List[str] = Field(..., description="Distribution channels")

# ---------------------------
# Crew Definition
# ---------------------------

@CrewBase
class HospitalSurgePredictionCrew():
    """Forecasts patient surges and optimizes hospital preparedness."""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # ----------- Agents -----------
    @agent
    def festival_event_forecaster(self) -> Agent:
        return Agent(
            config=self.agents_config['festival_event_forecaster'],
            tools=[SerperDevTool(), ScrapeWebsiteTool(),
                   DirectoryReadTool('resources/forecasts'),
                   FileWriterTool(), FileReadTool()],
            reasoning=True, inject_date=True, llm=llm,
            allow_delegation=True, max_rpm=3
        )

    @agent
    def pollution_climate_health_risk(self) -> Agent:
        return Agent(
            config=self.agents_config['pollution_climate_health_risk'],
            tools=[SerperDevTool(), ScrapeWebsiteTool(),
                   DirectoryReadTool('resources/forecasts'),
                   FileWriterTool(), FileReadTool()],
            inject_date=True, llm=llm, allow_delegation=True,
            max_iter=30, max_rpm=3
        )

    @agent
    def epidemic_surveillance(self) -> Agent:
        # Configure a more reliable LLM instance for this specific agent
        epidemic_llm = LLM(
            model="gemini/gemini-2.0-flash",
            temperature=0.3,  # Lower temperature for more deterministic responses
            api_key=os.getenv("GEMINI_API_KEY"),
            max_tokens=2048  # Reduced token limit to avoid empty responses
        )
        
        return Agent(
            config=self.agents_config['epidemic_surveillance'],
            tools=[SerperDevTool(), ScrapeWebsiteTool(),
                   DirectoryReadTool('resources/forecasts'),
                   FileWriterTool(), FileReadTool()],
            inject_date=True, llm=epidemic_llm, allow_delegation=False,
            max_iter=15, max_rpm=2  # Reduced iterations and rate to avoid overwhelming the model
        )

    @agent
    def staffing_optimizer(self) -> Agent:
        return Agent(
            config=self.agents_config['staffing_optimizer'],
            tools=[DirectoryReadTool('resources/forecasts'),
                   DirectoryReadTool('resources/plans'),
                   FileWriterTool(), FileReadTool()],
            inject_date=True, llm=llm, allow_delegation=True,
            max_iter=20, max_rpm=3
        )

    @agent
    def supply_chain_inventory(self) -> Agent:
        return Agent(
            config=self.agents_config['supply_chain_inventory'],
            tools=[DirectoryReadTool('resources/forecasts'),
                   DirectoryReadTool('resources/plans'),
                   FileWriterTool(), FileReadTool()],
            inject_date=True, llm=llm, allow_delegation=True,
            max_iter=15, max_rpm=3
        )

    @agent
    def patient_advisory_communication(self) -> Agent:
        return Agent(
            config=self.agents_config['patient_advisory_communication'],
            tools=[DirectoryReadTool('resources/forecasts'),
                   DirectoryReadTool('resources/communications'),
                   FileWriterTool(), FileReadTool()],
            inject_date=True, llm=llm, allow_delegation=True,
            max_iter=10, max_rpm=3
        )

    @agent
    def central_orchestrator(self) -> Agent:
        return Agent(
            config=self.agents_config['central_orchestrator'],
            tools=[DirectoryReadTool('resources/forecasts'),
                   DirectoryReadTool('resources/plans'),
                   DirectoryReadTool('resources/communications'),
                   DirectoryReadTool('resources/reports'),
                   FileWriterTool(), FileReadTool()],
            reasoning=True, inject_date=True, llm=llm,
            allow_delegation=True, max_iter=5, max_rpm=3
        )

    # ----------- Tasks -----------
    @task
    def festival_event_analysis(self) -> Task:
        return Task(config=self.tasks_config['festival_event_analysis'],
                    agent=self.festival_event_forecaster(),
                    output_json=SurgeReport)

    @task
    def pollution_health_risk_assessment(self) -> Task:
        return Task(config=self.tasks_config['pollution_health_risk_assessment'],
                    agent=self.pollution_climate_health_risk(),
                    output_json=SurgeReport)

    @task
    def epidemic_outbreak_surveillance(self) -> Task:
        return Task(config=self.tasks_config['epidemic_outbreak_surveillance'],
                    agent=self.epidemic_surveillance(),
                    output_json=SurgeReport)

    @task
    def staffing_optimization_planning(self) -> Task:
        return Task(config=self.tasks_config['staffing_optimization_planning'],
                    agent=self.staffing_optimizer(),
                    output_json=StaffingPlan)

    @task
    def supply_chain_inventory_management(self) -> Task:
        return Task(config=self.tasks_config['supply_chain_inventory_management'],
                    agent=self.supply_chain_inventory(),
                    output_json=InventoryRequirement)

    @task
    def patient_advisory_preparation(self) -> Task:
        return Task(config=self.tasks_config['patient_advisory_preparation'],
                    agent=self.patient_advisory_communication(),
                    output_json=PatientAdvisory)

    @task
    def hospital_preparedness_orchestration(self) -> Task:
        return Task(config=self.tasks_config['hospital_preparedness_orchestration'],
                    agent=self.central_orchestrator(),
                    output_json=SurgeReport)

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
            max_rpm=3
        )

# ---------------------------
# Entrypoint (CLI usage)
# ---------------------------

if __name__ == "__main__":
    inputs = {
        "hospital_name": os.getenv("HOSPITAL_NAME", ""),
        "region": os.getenv("REGION", ""),
        "historical_data_period": os.getenv("HISTORICAL_DATA_PERIOD", ""),
        "current_season": os.getenv("CURRENT_SEASON", ""),
        "surveillance_data": os.getenv("SURVEILLANCE_DATA", ""),
        "current_staffing": os.getenv("CURRENT_STAFFING", ""),
        "budget_constraints": os.getenv("BUDGET_CONSTRAINTS", ""),
        "current_inventory": os.getenv("CURRENT_INVENTORY", ""),
        "vendor_details": os.getenv("VENDOR_DETAILS", ""),
        "regional_languages": os.getenv("REGIONAL_LANGUAGES", ""),
        "administrator_name": os.getenv("ADMINISTRATOR_NAME", ""),
        "emergency_contacts": os.getenv("EMERGENCY_CONTACTS", ""),
        "current_date": datetime.now().strftime("%Y-%m-%d"),
    }

    required = ["hospital_name", "region", "current_staffing"]
    missing = [f for f in required if not inputs[f]]

    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        exit(1)

    crew = HospitalSurgePredictionCrew()
    result = crew.hospital_surge_crew().kickoff(inputs=inputs)
    print("✅ Prediction completed:\n", result)
