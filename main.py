import requests
from bs4 import BeautifulSoup
import os
import shutil
from datetime import datetime
import urllib.parse


def get_v2ray_links(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        divs = soup.find_all('div', class_='tgme_widget_message_text')
        divs2 = soup.find_all('div', class_='tgme_widget_message_text js-message_text before_footer')
        spans = soup.find_all('span', class_='tgme_widget_message_text')
        codes = soup.find_all('code')
        span = soup.find_all('span')
        main = soup.find_all('div')
        
        all_tags = divs + spans + codes + divs2 + span + main

        v2ray_configs = []
        for tag in all_tags:
            text = tag.get_text()
            if text.startswith('vless://') or text.startswith('vmess://') or text.startswith('trojan://') or text.startswith('tuic://') or text.startswith('hy2://'):
                v2ray_configs.append(text)

        return v2ray_configs
    else:
        print(f"Failed to fetch URL (Status Code: {response.status_code})")
        return None

def get_region_from_ip(ip):
    api_endpoints = [
        f'https://ipapi.co/{ip}/json/',
        f'https://ipwhois.app/json/{ip}',
        f'http://www.geoplugin.net/json.gp?ip={ip}',
        f'https://api.ipbase.com/v1/json/{ip}'
    ]

    for endpoint in api_endpoints:
        try:
            response = requests.get(endpoint)
            if response.status_code == 200:
                data = response.json()
                if 'country' in data:
                    return data['country']
        except Exception as e:
            print(f"Error retrieving region from {endpoint}: {e}")
    return None

def save_configs_by_region(configs):
    config_folder = "sub"
    if os.path.exists(config_folder):
        for folder in os.listdir(config_folder):
            folder_path = os.path.join(config_folder, folder)
            if os.path.isdir(folder_path):
                shutil.rmtree(folder_path)

    if not os.path.exists(config_folder):
        os.makedirs(config_folder)
    if not os.path.exists('sub/Mix'):
        os.makedirs('sub/Mix')

    for config in configs:
        with open(os.path.join('sub/Mix/mix.txt'), 'a', encoding='utf-8') as file:
                file.write(config + '\n')
        ip = config.split('//')[1].split('/')[0]
        region = get_region_from_ip(ip)
        if region:
            region_folder = os.path.join(config_folder, region)
            if not os.path.exists(region_folder):
                os.makedirs(region_folder)

            with open(os.path.join(region_folder, 'config.txt'), 'a', encoding='utf-8') as file:
                file.write(config + '\n')


def create_sub_section():
    readme_path = "README.md"
    sub_folder = "sub"
    found_sub_section = False

    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as readme_file:
            content = readme_file.read()

            if '## Sub' in content:
                found_sub_section = True

    new_content = ""
    new_content += "## Sub\n"
    new_content += "| Sub |\n"
    new_content += "|-----|\n"

    for root, dirs, files in os.walk(sub_folder):
        for directory in dirs:
            config_path = os.path.join(root, directory, 'config.txt')
            if os.path.exists(config_path):
                url = f"https://raw.githubusercontent.com/Surfboardv2ray/V2rayCollector_Py/main/sub/{urllib.parse.quote(directory)}/config.txt"
                new_content += f"| [{directory}]({url}) |\n"

    with open(readme_path, 'w', encoding='utf-8') as readme_file:
        if found_sub_section:
            readme_file.write(content.replace(content[content.find('## Sub'):content.find('\n\n', content.find('## Sub'))], new_content))
        else:
            readme_file.write(content + new_content)

if __name__ == "__main__":
    telegram_urls = [
        "https://t.me/ConfigsHubPlus",
        "https://t.me/v2ray_configs_pool",
    ]

    all_v2ray_configs = []
    for url in telegram_urls:
        v2ray_configs = get_v2ray_links(url)
        if v2ray_configs:
            all_v2ray_configs.extend(v2ray_configs)

    if all_v2ray_configs:
        save_configs_by_region(all_v2ray_configs)
        create_sub_section()
        print("Configs saved successfully.")
    else:
        print("No V2Ray configs found.")
