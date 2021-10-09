from yoomoney import Client
from database.models import Bill, Dataset, User
from pytz import utc
from database.db import session
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
import dramatiq

broker = RabbitmqBroker(url='amqp://vtb:vtb@rabbitmq:5672/vtb')

dramatiq.set_broker(broker)


def check_bill(bill_id):
    token = "YOUR_TOKEN"
    client = Client(token)
    bill = session.query(Bill).filter_by(id=bill_id)
    history = client.operation_history(label=bill.receipt)
    for operation in history.operations:
        if operation.status == 'success':
            dataset = session.query(Dataset).filter_by(id=bill.dataset_id)
            session.delete(bill)
            session.add(Dataset(name=dataset.name,
                                status=dataset.status,
                                data=dataset.data,
                                sell=dataset.sell,
                                price=dataset.price))
            user = session.query(User).filter_by(id=bill.user_id)
            session.query(dataset).join(user)
            session.commit()


@dramatiq.actor(broker=broker, max_retries=0)
def chek_new_transactions():
    print('Start check new transactions')
    try:
        bills = session.query(Bill).all()
        if len(bills) != 0:
            for bill in bills:
                check_bill(bill_id=bill.id)
    except:
        print('Buy limc token transaction is None')


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    executors = {
        'default': {'type': 'threadpool', 'max_workers': 5},
        'processpool': ProcessPoolExecutor(max_workers=3)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 1
    }
    scheduler.configure(executors=executors, job_defaults=job_defaults, timezone=utc)
    scheduler.add_job(
        chek_new_transactions.send,
        'interval',
        minutes=1
    )
    try:
        scheduler.start()
        print('Scheduler is starting...', flush=True)
    except Exception as e:
        print(e)




