from app.db.document import DocumentsService
from fastapi import APIRouter, Depends, status

from app.schemas.document_request import DocumentRequest
from app.schemas.document_response import DocumentResponse

router = APIRouter(
    prefix='/documents',
    tags=['Documents'],
)


@router.post(
    '/create',
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    name='User creation'
)
def create_document(
    document_schema: DocumentRequest,
    document_service: DocumentsService = Depends(),
):
    return document_service.add_document(document_schema)


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
