import os
import json
import re
import codecs

script_directory = os.path.dirname(os.path.abspath(__file__)) + "/"

CONFIG_DIR = script_directory + '../configs'
HOSTS_FILE = "/etc/hosts"
ITEMS = ['host', 'mikrotik', 'vpn', 'node']

result_dict = {}

# Проходим по всем подпапкам и файлам .json
for item in ITEMS:
    for subdir, dirs, files in os.walk(os.path.join(CONFIG_DIR, item)):
        for file in files:
            if file == "config":
                with open(os.path.join(subdir, file), 'r') as f:
                    data = json.load(f)
                    if item != 'node':
                        result_dict[item + subdir.split('/')[-1].lower()] = data.get(f"{item.upper()}_IP_ADDRESS")
                    else:
                        result_dict[item + subdir.split('/')[-1].lower()] = f"10.{data.get('NODE_HOST_ID')}.0.254"
                      
# Отсортировываем полученный словарь
result_dict = dict(sorted(result_dict.items()))

# Читаем оригинальный файл
with codecs.open(HOSTS_FILE, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Создаем сет для названий хостов
hosts_set = set(result_dict.keys())

# Очищаем файл от ненужных строк
lines = [line for line in lines if not any(host in line for host in hosts_set)]

# Добавляем новые строки
for host, ip in result_dict.items():
    lines.append(f"{ip}\t{host}\n")

# Записываем обновленный файл
with codecs.open(HOSTS_FILE, 'w', encoding='utf-8') as file:
    file.writelines(lines)