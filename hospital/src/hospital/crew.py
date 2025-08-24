import os
import random
import itertools
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, FileWriterTool, FileReadTool

# Load environment variables
load_dotenv()

# === Rotating API Key Manager ===
class GeminiKeyRotator:
    def __init__(self):
        self.keys = [
            os.getenv("GEMINI_API_KEY_1"),
            os.getenv("GEMINI_API_KEY_2"),
            os.getenv("GEMINI_API_KEY_3"),
            os.getenv("GEMINI_API_KEY_4"),
            os.getenv("GEMINI_API_KEY_5"),
            os.getenv("GEMINI_API_KEY_6"),
            os.getenv("GEMINI_API_KEY_7"),
        ]
        self.keys = [k for k in self.keys if k]  # filter None
        if not self.keys:
            raise ValueError("No valid Gemini API keys found!")
        self._cycle = itertools.cycle(self.keys)

    def next_key(self):
        return next(self._cycle)

rotator = GeminiKeyRotator()

# === Helper: Create LLM with rotating key and random model ===
def create_rotating_llm():
    models = os.getenv("MODEL_POOL", "1.5-flash").split(",")
    model = random.choice(models).strip()
    os.environ["GEMINI_API_KEY"] = rotator.next_key()
    return LLM(
        model=f"gemini/{model}",
        temperature=0.6,
        max_tokens=4000,
        config={"request_timeout": 120, "max_retries": 3, "retry_delay": 2}
    )

# === Crew Definition ===
@CrewBase
class HospitalSurgePredictionCrew:
    """Forecasts patient surges and optimizes hospital preparedness using CSV data."""

    DATA_PATH = "resources/data"

    # ---------- Agents ----------
    @agent
    def festival_event_forecaster(self) -> Agent:
        def forecast_festival_surge():
            path = os.path.join(self.DATA_PATH, "festival_admissions.csv")
            df = pd.read_csv(path)
            report_lines = ["## Festival Surge Forecast Report\n"]
            for idx, row in df.iterrows():
                report_lines.append(f"{row['date']}: {row['festival_name']} -> {row['patient_count']} patients in {row['department']}")
            return "\n".join(report_lines)

        return Agent(
            role="Festival & Event Forecaster",
            goal="Predict patient surges linked to cultural events and festivals.",
            backstory="Analyzes Indian cultural calendars, holidays, and historical admissions data.",
            llm=create_rotating_llm(),
            tools=[FileWriterTool(), FileReadTool()],
            verbose=True,
            execute=forecast_festival_surge
        )

    @agent
    def pollution_climate_health_risk(self) -> Agent:
        def forecast_pollution_risks():
            path = os.path.join(self.DATA_PATH, "pollution_health_data.csv")
            df = pd.read_csv(path)
            report_lines = ["## Pollution Health Risk Forecast Report\n", f"**Date:** {datetime.today().strftime('%Y-%m-%d')}\n"]
            for idx, row in df.iterrows():
                report_lines.append(f"{row['date']}: AQI={row['aqi']}, PM2.5={row['pm2_5']}, Respiratory Cases={row['respiratory_cases']}, Cardiac Cases={row['cardiac_cases']}")
            return "\n".join(report_lines)

        return Agent(
            role="Pollution & Climate Health Risk Analyst",
            goal="Monitor AQI, pollution, and weather to forecast health risks.",
            backstory="Predicts respiratory and cardiac surges based on environmental data.",
            llm=create_rotating_llm(),
            tools=[FileWriterTool(), FileReadTool()],
            verbose=True,
            execute=forecast_pollution_risks
        )

    @agent
    def epidemic_surveillance(self) -> Agent:
        def generate_epidemic_report():
            path = os.path.join(self.DATA_PATH, "epidemic_data.csv")
            df = pd.read_csv(path)
            report_lines = ["## Epidemic Surveillance Report\n", f"**Date:** {datetime.today().strftime('%Y-%m-%d')}\n"]
            for idx, row in df.iterrows():
                report_lines.append(f"{row['date']} - {row['disease']}: {row['cases']} cases, {row['deaths']} deaths. Source: {row['source_url']}")
            return "\n".join(report_lines)

        return Agent(
            role="Epidemic Surveillance",
            goal="Monitor current infectious disease trends in the region.",
            backstory="Tracks COVID-19, influenza, and other outbreaks.",
            llm=create_rotating_llm(),
            tools=[FileWriterTool(), FileReadTool(), SerperDevTool()],
            verbose=True,
            execute=generate_epidemic_report
        )

    @agent
    def staffing_optimizer(self) -> Agent:
        def generate_staffing_plan():
            path = os.path.join(self.DATA_PATH, "staffing_data.csv")
            df = pd.read_csv(path)
            report_lines = ["## Staffing Optimization Plan\n"]
            for idx, row in df.iterrows():
                report_lines.append(f"{row['role']}: Total={row['total_staff']}, Available={row['available']}, On-call={row['on_call']}")
            return "\n".join(report_lines)

        return Agent(
            role="Staffing Optimizer",
            goal="Recommend optimal staffing schedules during surges.",
            backstory="Uses surge predictions to optimize staff allocation.",
            llm=create_rotating_llm(),
            tools=[FileWriterTool(), FileReadTool()],
            verbose=True,
            execute=generate_staffing_plan
        )

    @agent
    def supply_chain_inventory(self) -> Agent:
        def generate_inventory_plan():
            path = os.path.join(self.DATA_PATH, "inventory_data.csv")
            df = pd.read_csv(path)
            report_lines = ["## Hospital Supply Chain and Inventory Management Plan\n"]
            for idx, row in df.iterrows():
                report_lines.append(f"{row['item_name']}: Current Stock={row['current_stock']}, Reorder Point={row['reorder_point']}, Daily Consumption={row['daily_consumption']}")
            return "\n".join(report_lines)

        return Agent(
            role="Supply Chain & Inventory Planner",
            goal="Anticipate and manage hospital inventory needs.",
            backstory="Forecasts demand for medicines, PPE, oxygen, ICU beds, ventilators.",
            llm=create_rotating_llm(),
            tools=[FileWriterTool(), FileReadTool()],
            verbose=True,
            execute=generate_inventory_plan
        )

    @agent
    def patient_advisory_communication(self) -> Agent:
        def generate_advisories():
            return "\n".join([
                "## Patient Advisories",
                "Festival Advisory: Follow hospital guidance for festival surge periods.",
                "Pollution Advisory: Limit outdoor exposure on high AQI days.",
                "Epidemic Advisory: Maintain hygiene, mask-wearing, vaccination updates.",
                "Staffing Advisory: Follow scheduled shifts.",
                "Supply Chain Advisory: Essential resources will be available."
            ])

        return Agent(
            role="Patient Advisory & Communication Specialist",
            goal="Generate advisories and communication materials in multiple languages.",
            backstory="Creates preventive guidance and hospital visit protocols.",
            llm=create_rotating_llm(),
            tools=[FileWriterTool(), FileReadTool()],
            verbose=True,
            execute=generate_advisories
        )

    @agent
    def central_orchestrator(self) -> Agent:
        def integrate_reports():
            outputs = []
            for agent_name in ["festival_event_forecaster","pollution_climate_health_risk","epidemic_surveillance","staffing_optimizer","supply_chain_inventory","patient_advisory_communication"]:
                agent = getattr(self, agent_name)()
                if hasattr(agent, "execute"):
                    outputs.append(agent.execute())
            return "\n\n".join(outputs)

        return Agent(
            role="Central Orchestrator",
            goal="Integrate outputs into a unified hospital preparedness report.",
            backstory="Synthesizes predictions into a comprehensive plan.",
            llm=create_rotating_llm(),
            tools=[FileWriterTool(), FileReadTool()],
            verbose=True,
            execute=integrate_reports
        )

    # ---------- Tasks ----------
    @task
    def festival_event_analysis(self) -> Task:
        return Task(
            description="Analyze festival-related surges.",
            expected_output="resources/forecasts/festival_surge_forecast.md",
            agent=self.festival_event_forecaster(),
        )

    @task
    def pollution_health_risk_assessment(self) -> Task:
        return Task(
            description="Analyze pollution health risks.",
            expected_output="resources/forecasts/pollution_health_risk.md",
            agent=self.pollution_climate_health_risk(),
        )

    @task
    def epidemic_outbreak_surveillance(self) -> Task:
        return Task(
            description="Track outbreaks and epidemic trends.",
            expected_output="resources/forecasts/epidemic_surveillance.md",
            agent=self.epidemic_surveillance(),
        )

    @task
    def staffing_optimization_planning(self) -> Task:
        return Task(
            description="Optimize staffing based on forecasts.",
            expected_output="resources/plans/staffing_optimization.md",
            agent=self.staffing_optimizer(),
        )

    @task
    def supply_chain_inventory_management(self) -> Task:
        return Task(
            description="Plan hospital inventory and supply chain.",
            expected_output="resources/plans/supply_chain_inventory.md",
            agent=self.supply_chain_inventory(),
        )

    @task
    def patient_advisory_preparation(self) -> Task:
        return Task(
            description="Generate patient advisories.",
            expected_output="resources/communications/patient_advisories/advisories.md",
            agent=self.patient_advisory_communication(),
        )

    @task
    def hospital_preparedness_orchestration(self) -> Task:
        return Task(
            description="Integrate all reports into hospital preparedness document.",
            expected_output="resources/reports/hospital_preparedness_report.md",
            agent=self.central_orchestrator(),
        )

    # ---------- Crew ----------
    @crew
    def hospital_surge_crew(self) -> Crew:
        return Crew(
            agents=[
                self.festival_event_forecaster(),
                self.pollution_climate_health_risk(),
                self.epidemic_surveillance(),
                self.staffing_optimizer(),
                self.supply_chain_inventory(),
                self.patient_advisory_communication(),
                self.central_orchestrator(),
            ],
            tasks=[
                self.festival_event_analysis(),
                self.pollution_health_risk_assessment(),
                self.epidemic_outbreak_surveillance(),
                self.staffing_optimization_planning(),
                self.supply_chain_inventory_management(),
                self.patient_advisory_preparation(),
                self.hospital_preparedness_orchestration(),
            ],
            process=Process.sequential,
            verbose=True,
        )
