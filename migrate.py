#!/usr/bin/python3

import requests

def list_keys(token, url, kv, base_key=''):
    full_url = '{}/v1/{}/metadata/{}'.format(url, kv, base_key)
    headers = {'X-Vault-Token': token}
    res = requests.request('LIST', full_url, headers=headers)
    res.raise_for_status()
    keys = res.json()['data']['keys']
    for key in keys:
        full_key = base_key + key
        if key.endswith('/'):
            yield from list_keys(token, url, kv, full_key)
        else:
            yield full_key

def get_key_value(token, url, kv, key):
    full_url = '{}/v1/{}/data/{}'.format(url, kv, key)
    headers = {'X-Vault-Token': token}
    res = requests.request('GET', full_url, headers=headers)
    if res.status_code == 404:
        return None
    res.raise_for_status()
    return res.json()['data']['data']

def write_key_value(token, url, kv, key, data):
    full_url = '{}/v1/{}/data/{}'.format(url, kv, key)
    headers = {'X-Vault-Token': token}
    res = requests.request('POST', full_url, headers=headers, json={'data': data})
    res.raise_for_status()

# params
token_src = '<token>'
url_src='<vault url>'
kv_src = '<vault kv name>'

token_dst = '<token>'
url_dst = '<vault url>'
kv_dst = '<vault kv name>'

for key in list_keys(token_src, url_src, kv_src):
    value = get_key_value(token_src, url_src, kv_src, key)
    if value is  None:
        print('got 404 for', key)
        continue
    write_key_value(token_dst, url_dst, kv_dst, key, value)
