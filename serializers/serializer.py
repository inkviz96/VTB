from pydantic import BaseModel


class DataSets(BaseModel):
    id: int
    name: str
    url: str
    stat
    sell: bool
    price: int
