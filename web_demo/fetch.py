import gradio as gr
import requests

base_url = "http://localhost:8003"
headers = {
    'accept': 'application/json',
}

def fetch_users():
    response = requests.get(f'{base_url}/users/all', headers=headers)
    data = response.json()

    choices = [f"{item['id']}: {item['username']}" for item in data]
    return choices

def fetch_workspaces():
    response = requests.get(f'{base_url}/workspaces/all', headers=headers)
    data = response.json()

    choices = [f"{item['id']}: {item['name']}" for item in data]
    return choices

def fetch_spaces(workspace_id):
    if not workspace_id:
        return gr.update(choices=[], value=None)
    workspace_id = workspace_id.split(":")[0]
    # workspace_id = int(workspace_id)

    params = {
        'workspace_id': workspace_id,
    }
    response = requests.get(f'{base_url}/spaces/all-in-workspace', params=params, headers=headers)

    data = response.json()
    choices = [f"{item['id']}: {item['name']}" for item in data]
    if len(choices) > 0:
        value = choices[0]
    else:
        value = None

    return gr.update(choices=choices, value=value)