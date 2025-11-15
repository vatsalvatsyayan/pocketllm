from fastapi import APIRouter

router = APIRouter()

# TEMPORARY
@router.post("/login")
async def login():
    return {"status": "todo authenticate"}
