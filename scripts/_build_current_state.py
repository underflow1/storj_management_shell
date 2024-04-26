import json
import os

# Define the config paths
CONFIG_PATH = os.path.expanduser("~/.config/sms")
CONFIGURATION_ITEMS_DIR = os.path.join(CONFIG_PATH, "configuration_items")
CURRENT_STATE = os.path.join(CONFIG_PATH, "current_state.json")

# Function to read and verify the JSON structure
def read_and_verify_json(file_path):
    """
    Open the config file, validate its JSON structure and return the data.
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

# Function to get the current state of configuration items
def get_current_state():
    """
    Walk through the configuration items directory, read each config file,
    validate its JSON structure, and construct a comprehensive dict of all items.
    """
    categories = ["node", "host", "vpn", "mikrotik"]
    state = {category: {} for category in categories}

    for category in categories:
        category_path = os.path.join(CONFIGURATION_ITEMS_DIR, category)
        if os.path.exists(category_path):
            for item_id in os.listdir(category_path):
                item_path = os.path.join(category_path, item_id, "config")
                if os.path.exists(item_path):
                    data = read_and_verify_json(item_path)
                    if data is not None:
                        state[category][item_id] = data
    
    return state

# Main function to execute the script logic
def main():
    """
    Main function to execute the script's logic: gather the current state and save it to the specified file.
    """
    current_state = get_current_state()
    
    # Print the current state to the console
    print(json.dumps(current_state, indent=2))
    
    # Save the current state to a file
    with open(CURRENT_STATE, 'w') as file:
        json.dump(current_state, file, indent=2)

if __name__ == "__main__":
    main()