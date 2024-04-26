import os
import json

CONFIG_PATH = os.path.expanduser("~/.config/sms")

def read_configs(folder):
    port_dst_range_list = []
    for item_id in os.listdir(folder):
        item_path = os.path.join(folder, item_id)
        if os.path.isdir(item_path):
            config_file = os.path.join(item_path, "config")
            if os.path.exists(config_file):

                with open(config_file, 'r') as file:
                    config_data = json.load(file)
                    port_dst_range_list.append(
                        {
                            "ip": config_data["MIKROTIK_IP_ADDRESS"],
                            "port_range": f"{item_id}000-{item_id}999",
                            "id": item_id

                        })
    return port_dst_range_list

def main():
    configuration_items_folder = os.path.join(CONFIG_PATH, "configuration_items")
    if os.path.exists(configuration_items_folder):
        mikrotik_folder = os.path.join(configuration_items_folder, "mikrotik")
        if os.path.exists(mikrotik_folder):
            port_dst_range_list = read_configs(mikrotik_folder)
            print(port_dst_range_list)
        else:
            print("Folder 'mikrotik' not found.")
    else:
        print("Folder 'configuration_items' not found.")

if __name__ == "__main__":
    main()