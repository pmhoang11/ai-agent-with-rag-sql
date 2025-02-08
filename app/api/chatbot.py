import json
import os
import shutil
from typing import Optional

from app.agent import agent
from app.core.config import settings
from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse

from app.schemas.chatbot_request import ChatRequest
from typing_extensions import Annotated
from loguru import logger


router = APIRouter(
    prefix='/chatbot',
    tags=['Chatbot'],
)

@router.post(
    '/chat',
    status_code=status.HTTP_201_CREATED,
    name='Chat'
)
def chat(
        chatbot_schema: ChatRequest,
):
    info = "user_id: {}; space_id: {}".format(chatbot_schema.user_id, chatbot_schema.space_id)
    query = "Question: {}\nAdditional Information (optional): {}".format(chatbot_schema.question, info)
    messages = {"messages": [{"role": "human", "content": query}]}
    logger.info(f"{chatbot_schema.thread_id} | {query}")
    config = {"configurable": {"thread_id": chatbot_schema.thread_id}}
    response = agent.graph.invoke(messages, config)
    answer = {"answer": response["messages"][-1].content}

    return JSONResponse(content=answer)
