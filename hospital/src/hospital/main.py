#!/usr/bin/env python
import sys
import os
import warnings
from datetime import datetime
from dotenv import load_dotenv

from hospital.crew import HospitalSurgePredictionCrew

# Load environment variables
load_dotenv()

# Filter out Pydantic deprecation warnings - more comprehensive approach
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*class-based.*config.*")
warnings.filterwarnings("ignore", message=".*Support for class-based.*")

# Filter out other warnings
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information


def get_inputs():
    """
    Get inputs from environment variables with validation.
    """
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
    
    # Validate required fields
    required_fields = ["hospital_name", "region", "current_staffing", "administrator_name"]
    missing_fields = [field for field in required_fields if not inputs[field]]
    
    if missing_fields:
        print(f"❌ Error: Missing required environment variables:")
        for field in missing_fields:
            print(f"   - {field.upper()}")
        print("\n📋 Please check your .env file and ensure all required variables are set.")
        print("   Refer to the .env.example file for the complete list of required variables.")
        sys.exit(1)
    
    # Display configuration summary
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
    """
    Run the hospital surge prediction crew.
    """
    print("🚀 Starting Hospital Surge Prediction Analysis...")
    
    try:
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
        print(f"\n❌ An error occurred while running the crew: {e}")
        print("🔧 Please check your configuration and try again.")
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    if len(sys.argv) < 3:
        print("❌ Usage: python main.py train <n_iterations> <filename>")
        print("   Example: python main.py train 5 training_results.json")
        sys.exit(1)
    
    print(f"🎓 Training Hospital Surge Prediction Crew...")
    print(f"   Iterations: {sys.argv[1]}")
    print(f"   Output file: {sys.argv[2]}")
    
    try:
        inputs = get_inputs()
        crew = HospitalSurgePredictionCrew()
        
        result = crew.hospital_surge_crew().train(
            n_iterations=int(sys.argv[1]), 
            filename=sys.argv[2], 
            inputs=inputs
        )
        
        print(f"\n✅ Training completed! Results saved to {sys.argv[2]}")
        return result
        
    except ValueError:
        print("❌ Error: Number of iterations must be a valid integer.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ An error occurred while training the crew: {e}")
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    if len(sys.argv) < 2:
        print("❌ Usage: python main.py replay <task_id>")
        print("   Example: python main.py replay festival_event_analysis")
        sys.exit(1)
    
    print(f"🔄 Replaying Hospital Surge Prediction from task: {sys.argv[1]}")
    
    try:
        crew = HospitalSurgePredictionCrew()
        result = crew.hospital_surge_crew().replay(task_id=sys.argv[1])
        
        print(f"\n✅ Replay completed successfully!")
        return result
        
    except Exception as e:
        print(f"\n❌ An error occurred while replaying the crew: {e}")
        print("🔧 Please ensure the task_id is valid and try again.")
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and returns the results.
    """
    if len(sys.argv) < 3:
        print("❌ Usage: python main.py test <n_iterations> <eval_llm>")
        print("   Example: python main.py test 3 gemini/gemini-2.0-flash")
        sys.exit(1)
    
    print(f"🧪 Testing Hospital Surge Prediction Crew...")
    print(f"   Iterations: {sys.argv[1]}")
    print(f"   Evaluation LLM: {sys.argv[2]}")
    
    try:
        inputs = get_inputs()
        crew = HospitalSurgePredictionCrew()
        
        result = crew.hospital_surge_crew().test(
            n_iterations=int(sys.argv[1]), 
            eval_llm=sys.argv[2], 
            inputs=inputs
        )
        
        print(f"\n✅ Testing completed successfully!")
        return result
        
    except ValueError:
        print("❌ Error: Number of iterations must be a valid integer.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ An error occurred while testing the crew: {e}")
        raise Exception(f"An error occurred while testing the crew: {e}")


def validate_env():
    """
    Validate environment configuration.
    """
    print("🔍 Validating environment configuration...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found.")
        print("   Please create a .env file based on the provided template.")
        return False
    
    # Check critical API keys
    critical_keys = ["SERPER_API_KEY", "GOOGLE_API_KEY"]
    missing_keys = []
    
    for key in critical_keys:
        if not os.getenv(key):
            missing_keys.append(key)
    
    if missing_keys:
        print("❌ Missing critical API keys:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\n🔑 Please add these API keys to your .env file.")
        return False
    
    print("✅ Environment configuration looks good!")
    return True


def main():
    """
    Main entry point with command routing.
    """
    if len(sys.argv) < 2:
        print("🏥 Hospital Surge Prediction System")
        print("\nUsage:")
        print("  python main.py run                              # Run surge prediction analysis")
        print("  python main.py train <iterations> <filename>    # Train the system")
        print("  python main.py test <iterations> <eval_llm>     # Test the system")
        print("  python main.py replay <task_id>                 # Replay from specific task")
        print("  python main.py validate                         # Validate environment setup")
        print("\nExamples:")
        print("  python main.py run")
        print("  python main.py train 5 training_results.json")
        print("  python main.py test 3 gemini/gemini-2.0-flash")
        print("  python main.py replay festival_event_analysis")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "run":
        run()
    elif command == "train":
        train()
    elif command == "test":
        test()
    elif command == "replay":
        replay()
    elif command == "validate":
        validate_env()
    else:
        print(f"❌ Unknown command: {command}")
        print("   Use 'python main.py' to see available commands.")
        sys.exit(1)


if __name__ == "__main__":
    main()