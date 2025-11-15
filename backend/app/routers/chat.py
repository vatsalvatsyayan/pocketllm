from fastapi import APIRouter

router = APIRouter()

# TEMPORARY
@router.get("/history")
async def chat_history():
    return {"status": "chat history placeholder"}
