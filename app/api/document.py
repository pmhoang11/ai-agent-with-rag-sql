import json
import os
import shutil
from typing import Optional

from app.contextual_vectordb import context_vectordb
from app.core.config import settings
from app.db.document import DocumentsService
from app.db.space import SpacesService

from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException, Form
from app.schemas.document_request import DocumentRequest
from app.schemas.document_response import DocumentResponse
from app.vectordb import vectordb
from typing_extensions import Annotated


router = APIRouter(
    prefix='/documents',
    tags=['Documents'],
)


def parse_document_schema(document_schema: str = Form(...)) -> DocumentRequest:
    try:
        data = json.loads(document_schema)
        return DocumentRequest(**data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in document_schema")


@router.post(
    '/upload',
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    name='Upload PDF'
)
def upload_pdf(
        file: Annotated[UploadFile, File(description="Accept: application/pdf")],
        document_schema: DocumentRequest = Depends(parse_document_schema),
        document_service: DocumentsService = Depends(),
        space_service: SpacesService = Depends(),
        advance: bool = True,
):
    """
    API Upload PDF

    Requires:

        - pdf file
        - document_schema (example):
        {
            "owner_id": 1,
            "workspace_id": 1,
            "space_id": 1
        }
    """
    try:

        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed!")

        file_path = os.path.join(settings.PDF_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        document_schema.title = str(file.filename)
        doc_obj = document_service.add_document(document_schema)
        space_service.increase_num_documents(doc_obj.workspace_id)

        if advance:
            context_vectordb.embed_docs(file_path, doc_obj.space_id, doc_obj.id)
        else:
            vectordb.embed_docs(file_path, doc_obj.space_id, doc_obj.id)

        return doc_obj

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    '/all',
    response_model=list[DocumentResponse],
    status_code=status.HTTP_200_OK,
    name='Get all documents'
)
def get_all_documents(
        document_service: DocumentsService = Depends()
):
    return document_service.get_all_documents()
