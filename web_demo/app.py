import os.path
from uuid import uuid4

import gradio as gr
import requests
from loguru import logger
from fetch import fetch_users, fetch_workspaces, fetch_spaces, base_url


def chatbot_response(message, history, user, space, thread_id, *args, **kargs):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    space_id = int(space.split(":")[0])
    user_id = int(user.split(":")[0])

    json_data = {
        'question': message,
        'space_id': space_id,
        'user_id': user_id,
        'thread_id': thread_id,
    }

    logger.info(json_data)

    response = requests.post(f'{base_url}/chatbot/chat', headers=headers, json=json_data)
    logger.info(response.text)
    data = response.json()
    return data["answer"]

def upload_file(file, user, workspace, space):
    if file is None:
        return "No file uploaded"

    headers = {
        'accept': 'application/json',
    }
    params = {
        'advance': 'true',
    }

    filename = os.path.basename(file.name)
    user_id = int(user.split(":")[0])
    workspace_id = int(workspace.split(":")[0])
    space_id = int(space.split(":")[0])

    files = {
        'file': (filename, open(file, "rb"), 'application/pdf'),
        'document_schema': (None, f'{{"owner_id":{user_id},"workspace_id":{workspace_id},"space_id":{space_id}}}'),
    }

    response = requests.post(f'{base_url}/documents/upload', params=params, headers=headers, files=files)

    if response.ok:
        return f"Uploaded file: {filename}"
    else:
        return "Upload failed"


def return_uuid():
    return str(uuid4())

with gr.Blocks(fill_height=True) as demo:
    with gr.Row(scale=1):
        gr.Markdown("# AGENT - RAG & Text-to-SQL")
        thread_id = gr.State()
        demo.load(fn=return_uuid, outputs=thread_id)

    with gr.Row(scale=5):
        with gr.Column(scale=1):
            user_choices = fetch_users()
            workspace_choices = fetch_workspaces()
            user = gr.Dropdown(
                user_choices, label="User", info="id: user_name", interactive=True
            )
            workspace = gr.Dropdown(
                workspace_choices, label="Workspace", info="id: workspace_name", interactive=True
            )
            space = gr.Dropdown(
                [], label="Space", info="id: space_name", interactive=True
            )
            upload_btn = gr.File(label="Upload a Document", file_types=[".pdf"])
            output = gr.Textbox(label="Upload status")

            upload_btn.upload(upload_file, inputs=[upload_btn, user, workspace, space], outputs=output)
            workspace.change(fetch_spaces, inputs=[workspace], outputs=[space])

        with gr.Column(scale=3):
            chatbot = gr.ChatInterface(
                chatbot_response,
                additional_inputs=[user, space, thread_id],
            )


if __name__ == "__main__":

    demo.launch()
