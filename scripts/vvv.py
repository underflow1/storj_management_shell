import os
import argparse
import json
from tabulate import tabulate

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("--env-file", default="~/config.env", help="Specify the path to the .env file")
args = parser.parse_args()

# Load variables from the .env file
env_file = os.path.expanduser(args.env_file)
if os.path.exists(env_file):
    with open(env_file, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            os.environ[key] = value
else:
    print("File with variables is unavailable. Exiting.")
    exit()

# Get the config path
config_path = os.path.expanduser(os.environ.get('CONFIG_PATH'))

# Process configuration files
data = []
for item_type in ['node', 'vpn']:
    for item_id in os.listdir(os.path.join(config_path, 'configuration_items', item_type)):
        config_file = os.path.join(config_path, 'configuration_items', item_type, item_id, 'config.json')
        with open(config_file, 'r') as file:
            config_data = json.load(file)
            if item_type == 'node':
                data.append(['node' + str(config_data['NODE_VPN_ID']).zfill(3), 
                             config_data.get('NODE_IP_ADDRESS_EXTERNAL', ''), item_id, 
                             config_data['VPN_COMMENT'])
            else:
                vpn_ip_list = config_data['VPN_IP_ADDRESS_LIST']
                for idx, vpn_ip in enumerate(vpn_ip_list):
                    if idx == 0:
                        vpn_name = 'vpn' + str(config_data['VPN_IP_ADDRESS']).replace('.', '')
                    else:
                        vpn_name = str(idx)
                    data.append([vpn_name, vpn_ip, item_id, config_data['VPN_COMMENT']])

# Print table
headers = ["vpn", "ip", "nodes", "comment"]
print(tabulate(data, headers=headers, tablefmt="pretty"))