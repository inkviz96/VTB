import random

from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from database.db import session
from database.models import Dataset, Bill
from yoomoney import Authorize
from yoomoney import Client
from yoomoney import Quickpay

Authorize(
      client_id="0856F742C08EAD9603B3DCC0007B1F21CDD8107242926232F",
      redirect_uri="http://0.0.0.0:8080",
      scope=["account-info",
             "operation-history",
             "operation-details",
             "incoming-transfers",
             "payment-p2p",
             "payment-shop",
             ]
      )


router = APIRouter(prefix="/api/v1")


@router.post("buy_request", status_code=200)
async def buy_request(dataset_id: int, amount: int, user_id: int):
    token = "C143D36E78923BE"
    client = Client(token)
    user = client.account_info()
    if user.balance < amount:
        return HTTPException(status_code=400)
    cards = user.cards_linked
    if len(cards) != 0:
        for card in cards:
            print(card.pan_fragment, " - ", card.type)
    else:
        print("No card is linked to the account")
        return HTTPException(status_code=400)
    receipt = str(amount)+'&&'+str(dataset_id)+str(random.randint(0, 10))
    quickpay = Quickpay(
        receiver="410019014512803",
        quickpay_form="shop",
        targets="Sponsor this project",
        paymentType="SB",
        sum=amount,
        label=receipt
    )
    session.add(Bill(receipt=receipt, dataset_id=dataset_id, user_id=user_id))
    session.commit()
    return JSONResponse(content={'redirected_url': quickpay.redirected_url, 'base_url': quickpay.base_url},
                        status_code=status.HTTP_200_OK)
