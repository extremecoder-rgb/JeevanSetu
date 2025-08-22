#!/usr/bin/env python
import os
import sys
import logging
from dotenv import load_dotenv
from hospital.crew import HospitalSurgePredictionCrew, create_llm_instance

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_pollution_agent():
    """Test the Pollution & Climate Health Risk Agent initialization"""
    try:
        # Verify API key
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            print("❌ Error: GEMINI_API_KEY environment variable is not set.")
            return False
            
        # Verify model
        model_name = os.getenv("MODEL", "gemini/gemini-1.5-flash")
        print(f"Using model: {model_name}")
        
        # Create crew instance
        crew = HospitalSurgePredictionCrew()
        
        # Try to initialize the agent
        agent = crew.pollution_climate_health_risk()
        
        print(f"✅ Successfully initialized Pollution & Climate Health Risk Agent")
        print(f"Agent role: {agent.role}")
        print(f"Agent goal: {agent.goal}")
        print(f"Agent tools: {[tool.__class__.__name__ for tool in agent.tools]}")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Pollution & Climate Health Risk Agent initialization...")
    success = test_pollution_agent()
    if success:
        print("✅ Test passed!")
        sys.exit(0)
    else:
        print("❌ Test failed!")
        sys.exit(1)