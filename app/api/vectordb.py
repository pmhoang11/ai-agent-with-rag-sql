import os
import shutil

from fastapi import APIRouter, Depends, status
from fastapi import UploadFile, File, HTTPException

from app.core.config import settings
from app.vectordb import load_docs

router = APIRouter(
    prefix='/vectordb',
    tags=['VectorDB'],
)

@router.post("/upload-pdf")
def upload_pdf(file: UploadFile = File(...)):
    try:

        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed!")

        file_path = os.path.join(settings.PDF_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        docs = load_docs(file_path)
        content = [page.page_content[:100] for page in docs[:3]]

        return {"filename": file.filename, "content": content}

        # return {"filename": file.filename, "status": "PDF uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
