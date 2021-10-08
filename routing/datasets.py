import requests
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
import requests

router = APIRouter(prefix="/api/v1")


@router.get("/dataset_list/", status_code=200)
async def dataset_list():
    session = requests.Session()
    data = {"username": "datahub", "password": "datahub"}
    session.post("http://datahub.yc.pbd.ai:9002/logIn", json=data)
    data = {"query": '{dataset(urn: "urn:li:dataset:(urn:li:dataPlatform:hive,SampleHiveDataset,PROD)"){name}}'}
    response = session.post("http://datahub.yc.pbd.ai:9002/api/graphql", json=data)
    return JSONResponse(content=response.text, status_code=status.HTTP_200_OK)
