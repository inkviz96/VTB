from pydantic import BaseModel


class DataSets(BaseModel):
    id: int
    name: str
    url: str
    sell: bool
    price: int
