from fastapi import APIRouter

router = APIRouter()

# TEMPORARY
@router.get("/me")
async def current_user():
    return {"status": "user placeholder"}
