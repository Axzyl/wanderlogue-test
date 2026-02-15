from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import User, Photo, Analysis
from services.auth_service import get_current_user
from services.storage_service import storage_service
from services.claude_service import claude_service
from pydantic import BaseModel

router = APIRouter(prefix="/photos", tags=["photos"])


class PhotoResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    storage_url: str
    file_size: Optional[int]
    created_at: str
    analysis: Optional[dict] = None

    class Config:
        from_attributes = True


class AnalysisResponse(BaseModel):
    id: str
    photo_id: str
    location_info: Optional[str]
    historical_context: Optional[str]
    user_context: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


@router.post("/upload")
async def upload_photos(
    files: list[UploadFile] = File(...),
    context: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload one or more photos and optionally analyze them."""
    uploaded_photos = []

    for file in files:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} is not an image",
            )

        # Upload to storage
        file_data = await storage_service.upload_file(file, current_user.id)

        # Create photo record
        photo = Photo(
            user_id=current_user.id,
            filename=file_data["filename"],
            original_filename=file_data["original_filename"],
            storage_url=file_data["storage_url"],
            file_size=file_data["file_size"],
            mime_type=file_data["mime_type"],
        )
        db.add(photo)
        db.commit()
        db.refresh(photo)

        uploaded_photos.append({
            "id": photo.id,
            "filename": photo.filename,
            "original_filename": photo.original_filename,
            "storage_url": photo.storage_url,
            "file_size": photo.file_size,
        })

    return {"photos": uploaded_photos, "count": len(uploaded_photos)}


@router.post("/{photo_id}/analyze")
async def analyze_photo(
    photo_id: str,
    context: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Analyze a photo using Claude vision."""
    # Get photo
    photo = (
        db.query(Photo)
        .filter(Photo.id == photo_id, Photo.user_id == current_user.id)
        .first()
    )
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    # Check if analysis already exists
    existing_analysis = db.query(Analysis).filter(Analysis.photo_id == photo_id).first()
    if existing_analysis:
        # Update with new context if provided
        if context and context != existing_analysis.user_context:
            analysis_result = await claude_service.analyze_photo(
                photo.storage_url, context
            )
            existing_analysis.user_context = context
            existing_analysis.location_info = analysis_result["location_info"]
            existing_analysis.historical_context = analysis_result["historical_context"]
            existing_analysis.full_response = analysis_result["full_response"]
            db.commit()
            db.refresh(existing_analysis)
        return {
            "id": existing_analysis.id,
            "photo_id": photo_id,
            "location_info": existing_analysis.location_info,
            "historical_context": existing_analysis.historical_context,
            "user_context": existing_analysis.user_context,
            "full_response": existing_analysis.full_response,
        }

    # Perform analysis
    analysis_result = await claude_service.analyze_photo(photo.storage_url, context)

    # Save analysis
    analysis = Analysis(
        photo_id=photo_id,
        user_context=context,
        location_info=analysis_result["location_info"],
        historical_context=analysis_result["historical_context"],
        full_response=analysis_result["full_response"],
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return {
        "id": analysis.id,
        "photo_id": photo_id,
        "location_info": analysis.location_info,
        "historical_context": analysis.historical_context,
        "user_context": analysis.user_context,
        "full_response": analysis.full_response,
    }


@router.post("/analyze-batch")
async def analyze_batch(
    photo_ids: list[str],
    context: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Analyze multiple photos at once."""
    results = []
    for photo_id in photo_ids:
        try:
            result = await analyze_photo(photo_id, context, db, current_user)
            results.append({"photo_id": photo_id, "success": True, "analysis": result})
        except HTTPException as e:
            results.append({"photo_id": photo_id, "success": False, "error": e.detail})
        except Exception as e:
            results.append({"photo_id": photo_id, "success": False, "error": str(e)})

    return {"results": results}


@router.get("/")
async def list_photos(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all photos for the current user."""
    photos = (
        db.query(Photo)
        .filter(Photo.user_id == current_user.id)
        .order_by(Photo.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []
    for photo in photos:
        photo_data = {
            "id": photo.id,
            "filename": photo.filename,
            "original_filename": photo.original_filename,
            "storage_url": photo.storage_url,
            "file_size": photo.file_size,
            "created_at": photo.created_at.isoformat() if photo.created_at else None,
            "analysis": None,
        }
        if photo.analysis:
            photo_data["analysis"] = {
                "id": photo.analysis.id,
                "location_info": photo.analysis.location_info,
                "historical_context": photo.analysis.historical_context,
                "user_context": photo.analysis.user_context,
            }
        result.append(photo_data)

    return {"photos": result, "count": len(result)}


@router.get("/{photo_id}")
async def get_photo(
    photo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific photo with its analysis."""
    photo = (
        db.query(Photo)
        .filter(Photo.id == photo_id, Photo.user_id == current_user.id)
        .first()
    )
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    result = {
        "id": photo.id,
        "filename": photo.filename,
        "original_filename": photo.original_filename,
        "storage_url": photo.storage_url,
        "file_size": photo.file_size,
        "created_at": photo.created_at.isoformat() if photo.created_at else None,
        "analysis": None,
    }
    if photo.analysis:
        result["analysis"] = {
            "id": photo.analysis.id,
            "location_info": photo.analysis.location_info,
            "historical_context": photo.analysis.historical_context,
            "user_context": photo.analysis.user_context,
            "full_response": photo.analysis.full_response,
        }

    return result


@router.delete("/{photo_id}")
async def delete_photo(
    photo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a photo and its analysis."""
    photo = (
        db.query(Photo)
        .filter(Photo.id == photo_id, Photo.user_id == current_user.id)
        .first()
    )
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    # Delete from storage
    storage_service.delete_file(photo.filename)

    # Delete from database (cascade will delete analysis)
    db.delete(photo)
    db.commit()

    return {"message": "Photo deleted successfully"}
