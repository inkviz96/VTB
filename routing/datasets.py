from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
import requests
from database.db import session
from database.models import Dataset, User
import json


router = APIRouter(prefix="/api/v1")


@router.get("/dataset/{dataset_id}", tags=["datasets"], status_code=200)
async def dataset_info(dataset_id: int):
    """
    Datasets JSON data
    :param dataset_id: id dataset
    :return: Json dataset data
    """
    dataset = session.query(Dataset).filter_by(id=dataset_id).first()
    return JSONResponse(content=dataset.data, status_code=status.HTTP_200_OK)


@router.get("/dataset_delete/{dataset_id}", tags=["datasets"], status_code=200)
async def delete_dataset(dataset_id: int):
    """
    Delete dataset
    :param dataset_id: id dataset
    :return: {"Deleted": dataset id}
    """
    dataset = session.query(Dataset).filter_by(id=dataset_id).first()
    session.delete(dataset)
    session.commit()
    return JSONResponse(content={"Deleted": dataset.id}, status_code=status.HTTP_200_OK)


@router.get("/dataset_change/{dataset_id}/{new_price}", tags=["datasets"], status_code=200)
async def change_price_dataset(dataset_id: int, new_price: int):
    """
    Delete dataset
    :param dataset_id: id dataset
    :param new_price: New price dataset
    :return: {"Price change": new price}
    """
    dataset = session.query(Dataset).filter_by(id=dataset_id).first()
    dataset.price = new_price
    session.commit()
    return JSONResponse(content={"Price change": dataset.price}, status_code=status.HTTP_200_OK)


@router.get("/dataset_list/", tags=["datasets"], status_code=200)
async def dataset_list():
    """
    Получение всех datasets
    :return: json
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


@router.get("/users_dataset_list/", tags=["datasets"], status_code=200)
async def users_dataset_list():
    """
    Users Dataset list for sell
    :return: {"dataset_list": datasets info}
    """
    try:
        data_list = session.query(Dataset).all()
    except:
        session.rollback()
    datasets = []
    for data in data_list:
        datasets.append(
            {'id': data.id,
             'name': data.name,
             'status': data.status,
             'data': data.data,
             'sell': data.sell,
             'price': data.price})

    return JSONResponse(content={"dataset_list": datasets}, status_code=status.HTTP_200_OK)


@router.post("/new_dataset/", tags=["datasets"], status_code=200)
async def new_dataset(data_name: str, mail: str, data: dict, data_sell: bool, data_price: str):
    """
    Create new user dataset
    :param data_name: Name new dataset
    :param mail: User mail
    :param data: Rules for creating new dataset
    :param data_sell: Sell or not this dataset
    :param data_price: Price new dataset
    :return:
    """
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
    dataset = session.add(Dataset(name=data_name,
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
