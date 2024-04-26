import os, json, sys, re
from os import listdir

item_types = ['vpn', 'host', 'mikrotik']
configuration_items_path = os.path.join(sys.argv[1],'configuration_items')
if not os.path.exists(configuration_items_path):
    os.makedirs(configuration_items_path)

config_file_name = 'config'
data = {}

def parse(item_type):
    prefix = item_type.upper() + "_"
    
    item_type_path = os.path.join(configuration_items_path, item_type)
    if not os.path.exists(item_type_path):
        os.makedirs(item_type_path)
       
    temp_array = []
    for item in os.listdir(item_type_path):
        item_path = os.path.join(item_type_path, item, config_file_name)
        try:
            if os.path.isfile(item_path):
                with open(item_path) as json_file:
                    config = json.load(json_file)
                    try:
                        parsed_item = {}
                        parsed_item["id"] = item
                        parsed_item["ip"] = str(config[prefix+"IP_ADDRESS"])
                        parsed_item["port"] = str(config[prefix+"SSH_PORT"])
                    except:
                        pass
                    temp_array.append(parsed_item)
        except Exception as e:
            pass
    data[item_type] = temp_array

inventory_path = os.path.join(sys.argv[1], 'inventory')
if not os.path.exists(inventory_path):
    os.makedirs(inventory_path)

outfile = open(os.path.join(inventory_path, 'static-inventory'), 'w')
for item_type in item_types:
    parse(item_type)
    print(item_type)
    outfile.write("[" + item_type + "]" + "\n")
    for item in data[item_type]:
        
        if item_type == 'vpn':
            print(item)
            try:
                port = ' ansible_port=' + item['port']
            except:
                port = ""
        name = item_type + item['id']
        # host = 'ansible_host=' + item['ip']
        host = f" ansible_host={item['ip']}"
        ansible_item_id = f" ansible_item_id={item['id']}"
        the_line = f"{name}{host}{port}{ansible_item_id}\n"
        outfile.write(the_line)
        # outfile.write(name + " " + host + port + " " + ansible_item_id + '\n')
    outfile.write("\n")
outfile.close()

