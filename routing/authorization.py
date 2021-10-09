from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from database.db import session
from database.models import Dataset, User

router = APIRouter(prefix="/api/v1")


@router.get("/profile/{mail}/", tags=["authorization"], status_code=200)
async def profile(mail: str):
    user = session.query(User).filter_by(mail=mail).first()
    ds = session.query(Dataset).filter_by(user_id=int(user.id))
    all_dataset = []
    for dataset in ds:
        all_dataset.append({
            'id': dataset.id,
            'name': dataset.name,
            'url': dataset.url,
            'sell': dataset.sell,
            'price': dataset.price
        })
    data = {
        'datasets': all_dataset
    }
    return JSONResponse(content=data, status_code=status.HTTP_200_OK)


@router.get("/registration/{mail}/", tags=["authorization"], status_code=200)
async def register(mail: str):
    session.add(User(mail=mail))
    session.commit()
    return JSONResponse(status_code=status.HTTP_200_OK)
