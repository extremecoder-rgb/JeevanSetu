import sys
import os
from pathlib import Path
import json
from pydantic import BaseModel
from typing import Dict, Any

# Add the current directory to the path so we can import from crew
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crew import InventoryRequirement

# Path to the inventory file
inventory_path = Path('../../resources/plans/supply_chain_inventory.md')

# Read the inventory file
with open(inventory_path, 'r') as f:
    inventory_content = f.read()

# Parse the JSON content
try:
    inventory_data = json.loads(inventory_content)
    print("✅ JSON parsing successful")
    print(f"Data type: {type(inventory_data)}")
    
    # Validate with Pydantic model
    try:
        inventory_model = InventoryRequirement.model_validate(inventory_data)
        print("✅ Pydantic validation successful")
        print(f"Validated model: {inventory_model}")
    except Exception as e:
        print(f"❌ Pydantic validation error: {e}")
        
except json.JSONDecodeError as e:
    print(f"❌ JSON parsing error: {e}")