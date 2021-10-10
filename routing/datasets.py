from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
import requests
from database.db import session
from database.models import Dataset, User
import json


router = APIRouter(prefix="/api/v1")


@router.get("/dataset/{dataset_id}", tags=["datasets"], status_code=200)
async def dataset_info(dataset_id: int):
    dataset = session.query(Dataset).filter_by(id=dataset_id).first()
    return JSONResponse(content=dataset.data, status_code=status.HTTP_200_OK)


@router.get("/dataset_delete/{dataset_name}", tags=["datasets"], status_code=200)
async def delete_dataset(dataset_name: str):
    dataset = session.query(Dataset).filter_by(name=dataset_name).first()
    session.delete(dataset)
    session.commit()
    return JSONResponse(content={"Deleted"}, status_code=status.HTTP_200_OK)


@router.get("/dataset_change/{dataset_name}/{new_price}", tags=["datasets"], status_code=200)
async def change_price_dataset(dataset_name: str, new_price: int):
    dataset = session.query(Dataset).filter_by(name=dataset_name).first()
    dataset.price = new_price
    session.commit()
    return JSONResponse(content={"Price change"}, status_code=status.HTTP_200_OK)


@router.get("/dataset_list/", tags=["datasets"], status_code=200)
async def dataset_list():
    """
    Получение всех datasets
    """
    connect = await login()
    generated_dataset = await join_dataset(connect, datasets=None)
    return JSONResponse(content=generated_dataset, status_code=status.HTTP_200_OK)


def get_dataset(connect, dataset_type: str, dataset_name: str):
    """
    Получения одного датасет
    hive dataset list:
        SampleHiveDataset
        fct_users_created
        fct_users_deleted
        logging_events
    hdfs dataset list:
        SampleHdfsDataset
    kafka dataset list:
        SampleKafkaDataset
    """
    data = {"query": """{
        dataset(urn: "urn:li:dataset:(urn:li:dataPlatform:%s,%s,PROD)"){
            urn
            name
            properties {
                description
            }
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
                  foreignFields {
                    fieldPath
                  }
                  foreignDataset {
                    name
                  }
                }
            }
        }
    }""" % (dataset_type, dataset_name)}
    response = connect.post("http://datahub.yc.pbd.ai:9002/api/graphql", json=data)
    return json.loads(response.text)


@router.post("/create/", tags=["datasets"], status_code=200)
async def create():
    """
    Create testing users datasets
    """
    for x in range(10):
        try:
            session.add(Dataset(name='name', status='Done/', data={'some': 'json'}, sell=True, price=x))
            session.commit()
        except:
            session.rollback()
    return JSONResponse(status_code=status.HTTP_200_OK)


@router.get("/users_dataset_list/", tags=["datasets"], status_code=200)
async def users_dataset_list():
    """
    Users Dataset list for sell
    """
    try:
        data_list = session.query(Dataset).all()
    except:
        session.rollback()
    print(data_list, flush=True)
    datasets = {}
    for data in data_list:
        datasets[data.id] = {
            'name': data.name,
            'status': data.status,
            'data': data.data,
            'sell': data.sell,
            'price': data.price
        }
    return JSONResponse(content=datasets, status_code=status.HTTP_200_OK)


@router.post("/new_dataset/", tags=["datasets"], status_code=200)
async def new_dataset(mail: str, data: dict, data_sell: bool, data_price: str):
    connect = await login()
    datasets = {}
    for dataset in data['datasets']:
        # Сплитим urn и достаем из них данные
        key = dataset['urn'].split(':')[-1].split(',')[0]
        value = dataset['urn'].split(':')[-1].split(',')[1]
        try:
            if datasets[key]:
                datasets[key].append(value)
        except KeyError:
            datasets[key] = [value]
    print(datasets)
    generated_dataset = await join_dataset(connect, datasets=datasets)
    print(generated_dataset)
    user = session.query(User).filter_by(mail=mail).first()
    dataset = session.add(Dataset(name='Some name',
                                  status='pending',
                                  data=generated_dataset,
                                  sell=data_sell,
                                  price=data_price,
                                  user_pk=user.id))

    session.commit()

    return JSONResponse(content=dataset, status_code=status.HTTP_200_OK)


async def login():
    """
    LogIn
    """
    connect = requests.Session()
    data = {"username": "datahub", "password": "datahub"}
    connect.post("http://datahub.yc.pbd.ai:9002/logIn", json=data)
    return connect


async def join_dataset(connect, datasets, user_tags=None):
    """
    Объединение запрашиваемых dataset
    """
    result = {}
    if not datasets:
        datasets = {
            'hive': ('SampleHiveDataset', 'fct_users_created', 'fct_users_deleted', 'logging_events'),
            'hdfs': ('SampleHdfsDataset',),
            'kafka': ('SampleKafkaDataset',)
        }
    for dataset_type, dataset_name in datasets.items():
        type_list = {dataset_type: []}
        for name in dataset_name:
            response = get_dataset(connect, dataset_type, name)
            is_suitable = await filter_by_tag(
                dataset_tags=response["data"]["dataset"]["tags"],
                user_tags=user_tags
            )
            if is_suitable:
                type_list[dataset_type].append(response)
        result[dataset_type] = (type_list[dataset_type])
    return result


async def filter_by_tag(dataset_tags, user_tags=None):
    """
    Фильтрация dataset по тегам указаным пользователем
    :param dataset_tags: теги присутствующие в датасет
    :param user_tags: пользовательские теги
    :return: соответствие (Boolean)
    """
    if not user_tags:
        return True
    if dataset_tags:
        for tag in dataset_tags["tags"]:
            if tag["tag"]["name"] in user_tags:
                return True
    return False
