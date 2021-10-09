from pydantic import BaseModel


class DataSets(BaseModel):
    id: int
    name: str
    url: str
    status: str
    sell: bool
    price: int
