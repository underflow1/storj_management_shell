#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import uuid

def build_session_config(node_id):
    """
    Build session configuration based on the provided node_id.
    
    :param node_id: Node ID (integer)
    """
    # Define paths
    CONFIG_PATH = os.path.expanduser("~/.config/sms")
    CURRENT_STATE = os.path.join(CONFIG_PATH, "current_state")
    DEFAULTS = os.path.join(CONFIG_PATH, "defaults")
    CURRENT_SESSION_CONFIG = f"/tmp/{uuid.uuid4()}"
    
    # Check if node_id is provided and is an integer
    if not node_id or not isinstance(node_id, int):
        print("Invalid node_id. Please provide an integer value.")
        sys.exit(1)
    
    # Check if CURRENT_STATE file exists and is a valid JSON
    if not os.path.isfile(CURRENT_STATE):
        print(f"File {CURRENT_STATE} does not exist.")
        sys.exit(1)
    try:
        with open(CURRENT_STATE) as f:
            current_state = json.load(f)
    except json.JSONDecodeError:
        print(f"File {CURRENT_STATE} is not a valid JSON.")
        sys.exit(1)
    
    # Check if DEFAULTS file exists and is a valid JSON
    if not os.path.isfile(DEFAULTS):
        print(f"File {DEFAULTS} does not exist.")
        sys.exit(1)
    try:
        with open(DEFAULTS) as f:
            defaults = json.load(f)
    except json.JSONDecodeError:
        print(f"File {DEFAULTS} is not a valid JSON.")
        sys.exit(1)
    
    # Check if node_id exists in current_state['node']
    if str(node_id) not in current_state['node']:
        print(f"Node ID {node_id} not found in {CURRENT_STATE}.")
        sys.exit(1)
    
    # Build the new JSON configuration
    new_config = {}
    new_config.update(defaults)
    new_config.update(current_state['host'][str(current_state['node'][str(node_id)]['NODE_HOST_ID'])])
    new_config.update(current_state['mikrotik'][str(current_state['node'][str(node_id)]['NODE_MIKROTIK_ID'])])
    new_config.update(current_state['vpn'][str(current_state['node'][str(node_id)]['NODE_VPN_ID'])])
    new_config.update(current_state['node'][str(node_id)])
    new_config['NODE_ID'] = str(node_id)
    
    # Substitute composite values
    new_config["NODE_PORT_EXTERNAL"] = new_config["NODE_HOST_ID"] + new_config["NODE_ID"]
    new_config["NODE_PORT_CONSOLE"] = new_config["NODE_PORT_CONSOLE_PREFIX"] + new_config["NODE_ID"]
    new_config["NODE_IP_ADDRESS_EXTERNAL"] = new_config["VPN_IP_ADDRESS_LIST"][new_config["NODE_VPN_IP_ADDRESS_NUMBER"]]
    new_config["NODE_IP_ADDRESS_INTERNAL"] = "10." + new_config["NODE_HOST_ID"] + ".0.254"
    new_config["MIKROTIK_IP_ADDRESS_INTERNAL"] = "10." + new_config["NODE_MIKROTIK_ID"] + ".0.1"

    # Remove unnecessary keys
    keys_to_remove = ["HOST_IP_ADDRESS", "HOST_PROCESSING", "NODE_PORT_CONSOLE_PREFIX", "NODE_PORT_EXTERNAL_PREFIX",
                      "NODE_PORT_EXTERNAL_TYPE", "NODE_VPN_IP_ADDRESS_NUMBER", "NODE_VPN_TYPE", "VPN_IP_ADDRESS_LIST"]
    for key in keys_to_remove:
        new_config.pop(key, None)

    # Print the new configuration
    print(json.dumps(new_config, indent=4))
    
    # Save the new configuration to CURRENT_SESSION_CONFIG file
    with open(CURRENT_SESSION_CONFIG, 'w') as f:
        json.dump(new_config, f, indent=4)
    
    print(f"Session configuration saved to {CURRENT_SESSION_CONFIG}")
    return json.dumps(new_config)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: build_session_config.py <node_id>")
        sys.exit(1)
    
    node_id = int(sys.argv[1])
    build_session_config(node_id)