from fastapi import APIRouter

router = APIRouter()

# TEMPORARY
@router.get("/health")
async def session_health():
    return {"status": "session router available"}
