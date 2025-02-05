from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status

from app.db.base import get_session
from app.models.document import Document
from app.schemas.document_request import DocumentRequest, DocumentUpdateRequest



class DocumentsService:
    """Documents service for interacting with the database."""

    def __init__(self) -> None:
        self.session = next(get_session())

    def __del__(self):
        self.session.close()  # Ensure the session is closed when the object is destroyed

    def get_all_documents(self) -> list[Document]:
        """Returns all documents.
        Returns:
            list[Document]: list of documents.
        """
        documents = (
            self.session
            .query(Document)
            .order_by(Document.id.desc())
            .all()
        )
        return documents

    def get_document_by_id(self, document_id: int) -> Document:
        """Finds document by given document_id.
        Args:
            document_id: document_id id.
        Returns:
            document: found document.
        """
        document = (
            self.session
            .query(Document)
            .filter(Document.id == document_id)
            .first()
        )
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        return document

    def get_document_by_name(self, document_name: str) -> Document:
        """Finds document by given document_name.
        Args:
            document_name: document_name.
        Returns:
            document: found document.
        """
        document = (
            self.session
            .query(Document)
            .filter(Document.name == document_name)
            .first()
        )
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        return document

    def add_document(self, document_schema: DocumentRequest) -> Document:
        """Creates document by given document schema and saves it in database.
        Args:
            document_schema: document request schema.
        Returns:
            document: found document.
        """
        document = Document(
            title=document_schema.title,
            owner_id=document_schema.owner_id,
            workspace_id=document_schema.workspace_id,
            space_id=document_schema.space_id,
        )
        self.session.add(document)
        self.session.commit()
        return document

    def update_document(self, document_id: int, document_schema: DocumentUpdateRequest) -> Document:
        """Updates document by given document schema.
        Args:
            document_id: changeable document id.
            document_schema: document update schema.
        Returns:
            document: updated document.
        """
        document = self.get_document_by_id(document_id)

        for field, value in document_schema:
            if value:
                setattr(document, field, value)

        self.session.commit()
        return document

    def delete_document(self, document_id: int) -> None:
        """Deletes document by given id.
        Args:
            document_id: document_id.
        """
        document = self.get_document_by_id(document_id)
        self.session.delete(document)
        self.session.commit()
