"""
Document Upload Router
Handles medical history and profile document uploads
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
from pydantic import BaseModel

from services.document_service import document_service

router = APIRouter(prefix="/api/profile", tags=["Profile & Documents"])

# Allowed document types
ALLOWED_DOC_TYPES = [
    "application/msword",  # .doc
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    "application/octet-stream"  # Sometimes sent by browsers
]

ALLOWED_EXTENSIONS = [".doc", ".docx"]


class DocumentUploadResponse(BaseModel):
    success: bool
    message_bengali: str
    extracted_info: Optional[dict] = None
    bengali_summary: Optional[str] = None
    error: Optional[str] = None


class ProfileResponse(BaseModel):
    success: bool
    has_profile: bool
    profile_data: Optional[dict] = None
    message_bengali: str


def is_valid_document(content_type: str, filename: str) -> bool:
    """Check if uploaded file is a valid Word document"""
    # Check content type
    if content_type and content_type.lower() in ALLOWED_DOC_TYPES:
        return True
    # Fallback: check extension
    if filename:
        ext = "." + filename.lower().split(".")[-1]
        if ext in ALLOWED_EXTENSIONS:
            return True
    return False


@router.post("/upload-document", response_model=DocumentUploadResponse)
async def upload_medical_document(
    file: UploadFile = File(...),
    user_id: str = Form(default="default_user")
):
    """
    📄 আপনার মেডিকেল ডকুমেন্ট আপলোড করুন
    
    Upload your medical history, test reports, or health profile document.
    Supported formats: .doc, .docx (Word documents)
    
    The system will extract:
    - Medical conditions (anemia, diabetes, BP, etc.)
    - Allergies
    - Current medications
    - Test results (Hemoglobin, Blood Sugar, etc.)
    - Financial/budget information
    - Pregnancy details
    """
    # Validate file type
    if not is_valid_document(file.content_type, file.filename):
        return DocumentUploadResponse(
            success=False,
            message_bengali="শুধুমাত্র Word ডকুমেন্ট (.doc, .docx) আপলোড করুন।",
            error=f"Invalid file type: {file.content_type}. Only .doc and .docx files are supported."
        )
    
    # Check file size (max 10MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        return DocumentUploadResponse(
            success=False,
            message_bengali="ফাইল অনেক বড়। সর্বোচ্চ ১০ MB সাইজের ফাইল আপলোড করুন।",
            error="File too large. Maximum size is 10MB."
        )
    
    # Process document
    result = await document_service.process_document(
        file_content=contents,
        filename=file.filename,
        user_id=user_id
    )
    
    # Sync to main patient profile (Merge Logic)
    try:
        from routers.midwife_router import sync_document_data_to_profile
        sync_document_data_to_profile(user_id)
    except Exception as e:
        print(f"Post-upload sync failed: {e}")

    return DocumentUploadResponse(
        success=result.get("success", False),
        message_bengali=result.get("message_bengali", ""),
        extracted_info=result.get("extracted_info"),
        bengali_summary=result.get("bengali_summary"),
        error=result.get("error")
    )


@router.get("/my-profile", response_model=ProfileResponse)
async def get_my_profile(user_id: str = "default_user"):
    """
    📋 আপনার প্রোফাইল দেখুন
    
    Get your stored health profile extracted from uploaded documents.
    """
    profile = document_service.get_user_profile(user_id)
    
    if profile:
        return ProfileResponse(
            success=True,
            has_profile=True,
            profile_data=profile,
            message_bengali="আপনার প্রোফাইল পাওয়া গেছে।"
        )
    else:
        return ProfileResponse(
            success=True,
            has_profile=False,
            profile_data=None,
            message_bengali="কোনো প্রোফাইল পাওয়া যায়নি। অনুগ্রহ করে আপনার মেডিকেল ডকুমেন্ট আপলোড করুন।"
        )


@router.get("/health")
async def health_check():
    """Health check for document service"""
    return {"status": "healthy", "service": "document_upload"}
