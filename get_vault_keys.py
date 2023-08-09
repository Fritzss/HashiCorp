import argparse
from json import loads, dumps
import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', type=str, default='./config.json')
args = parser.parse_args()

with open(args.config, 'r', encoding='utf-8') as f:
    config = loads(f.read())
    f.close()


secrets_path = f'{config["branch"]}/metadata/dotnet/'


def connect_vault():
    header = {
        "X-Vault-Token": config["token"],
        "Content-Type": "application/json",
        "Url": config["vault_url"]
    }
    ses = requests.session()
    ses.headers.update(header)
    return ses


session = connect_vault()


def get_keys(paths):
    keys = []
    path_and_keys = {}
    for p in paths:
        path = p.replace('metadata', 'data')
        k = session.get(url=f'{config["vault_url"]}/v1/{path}', verify=False).json()['data']['data']
        keys.append(k)
        path_and_keys.update([(p, k)])
    return path_and_keys, keys


secrets = []


def list_secrets(path):
    paths = session.request('list', url=f'{config["vault_url"]}/v1/{path}', verify=False).json()
    if path[-1] == '/':
        for key in paths["data"]["keys"]:
            if key[-1] == '/':
                p_ath = f'{path}{key}'
                list_secrets(path=p_ath)
            else:
                secrets.append(f'{path}{key}')
    else:
        secrets.append(path)
    return secrets


def common_ttk():
   pass


def mutate_data(data):
    old = [key for key in data]
    new = [key.replace(config["branch"], f'{NEW}/newbranch') for key in data ]
    new_data = dict_key_changer(data, old, new)
    return new_data


def add_keys(data):
    for i in data:
        if 'database-servers' in i or 'elastic' in i or 'kafka' in i:
        #session.post(url=f'{config["vault_url"]}/v1/{i.key}', data=dumps(i.value), verify=False)

            for k in data[i]:
                print(f'{k} {data[i][k]}')


def dict_key_changer(data, old_key, new_key):
    list_all_key = list(data.keys())
    for x in range(0, len(new_key)):
        data[new_key[x]] = data[old_key[x]] if old_key[x] in list_all_key else None
    for x in list_all_key:
        data.pop(x)
    return data


data = loads(open('.\\data.json').read())
add_keys(mutate_data(data))
print(mutate_data(data))
