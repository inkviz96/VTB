from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
import requests
from database.db import session
from database.models import Dataset
import json

router = APIRouter(prefix="/api/v1")


@router.get("/dataset_list", status_code=200)
async def dataset_list():
    """ Получение всех datasets
    """
    session = requests.Session()
    data = {"username": "datahub", "password": "datahub"}
    session.post("http://datahub.yc.pbd.ai:9002/logIn", json=data)
    result = {}
    datasets = {
        'hive': ('SampleHiveDataset', 'fct_users_created', 'fct_users_deleted', 'logging_events'),
        'hdfs': ('SampleHdfsDataset', ),
        'kafka': ('SampleKafkaDataset',)
    }
    for dataset_type, dataset_name in datasets.items():
        type_list = {dataset_type: []}
        for name in dataset_name:
            response = get_dataset(session, dataset_type, name)
            type_list[dataset_type].append(response)
        result[dataset_type] = (type_list[dataset_type])
    return JSONResponse(content=result, status_code=status.HTTP_200_OK)


def get_dataset(session, dataset_type: str, dataset_name: str):
    """ В первую строчку запроса вместо hive и SampleHiveDataset (как было ранее)
        подставляем тип и название dataset (из url) и получаем его данные
    hive dataset list:
        SampleHiveDataset
        fct_users_created
        fct_users_deleted
        logging_events
    hdfs dataset list:
        SampleHdfsDataset
    kafka dataset list:
        SampleKafkaDataset
    Example: http://0.0.0.0:8017/api/v1/dataset_list/hife/fct_users_created
    """
    data = {"query": """{
        dataset(urn: "urn:li:dataset:(urn:li:dataPlatform:%s,%s,PROD)"){
            urn
            name
            tags {
                tags {
                    tag {
                        name
                    }
                }
            }
            schemaMetadata(version: 0) {
                version
                name
                fields {
                    fieldPath
                    description
                    type
                    tags {
                        tags {
                            tag {
                                name
                            }
                        }
                    }
                }
                primaryKeys
                foreignKeys {
                    name
                }
            }
        }
    }""" % (dataset_type, dataset_name)}
    response = session.post("http://datahub.yc.pbd.ai:9002/api/graphql", json=data)
    return JSONResponse(content=response.text, status_code=status.HTTP_200_OK)


@router.post("/create/", status_code=200)
async def create():
    for x in range(10):
        try:
            session.add(Dataset(name='name', url='https/', status='Done', sell=True, price=x))
            session.commit()
        except:
            session.rollback()
    return JSONResponse(status_code=status.HTTP_200_OK)


@router.get("/users_dataset_list/", status_code=200)
async def dataset_list():
    data_list = session.query(Dataset).filter_by(sell=True)
    datasets = {}
    for data in data_list:
        datasets[data.id] = {
            'name': data.name,
            'url': data.url,
            'status': data.status,
            'sell': data.sell,
            'price': data.price
        }
    return JSONResponse(content=json.dumps(datasets), status_code=status.HTTP_200_OK)
