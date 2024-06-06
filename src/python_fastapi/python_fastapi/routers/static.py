from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def get_root():
    return {"message": "Hello, world!"}
