from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health():
    """Health check endpoint returning status ok."""
    return {"status": "ok"}
