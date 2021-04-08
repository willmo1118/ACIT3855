import connexion
from connexion import NoContent
import json
import os.path
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from add_movie_orders import AddMovieOrder
from payments import Payment
import mysql.connector
import pymysql
import requests
import yaml
import logging.config
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from sqlalchemy import and_
import os
import time

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yaml"
    log_conf_file = "/config/log_conf.yaml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yaml"
    log_conf_file = "log_conf.yaml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
    DB_ENGINE = create_engine(f"mysql+pymysql://{app_config['datastore']['user']}:{app_config['datastore']['password']}@{app_config['datastore']['hostname']}:{app_config['datastore']['port']}/{app_config['datastore']['db']}")
    Base.metadata.bind = DB_ENGINE
    DB_SESSION = sessionmaker(bind=DB_ENGINE)

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())


# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

# with open('app_conf.yaml', 'r') as f:
#     app_config = yaml.safe_load(f.read())
#     DB_ENGINE = create_engine(f"mysql+pymysql://{app_config['datastore']['user']}:{app_config['datastore']['password']}@{app_config['datastore']['hostname']}:{app_config['datastore']['port']}/{app_config['datastore']['db']}")
#     Base.metadata.bind = DB_ENGINE
#     DB_SESSION = sessionmaker(bind=DB_ENGINE)

# with open('log_conf.yaml', 'r') as f:
#     log_config = yaml.safe_load(f.read())
#     logging.config.dictConfig(log_config)

# logger = logging.getLogger('basicLogger')

# with open('app_conf.yaml', 'r') as f:
#     app_config = yaml.safe_load(f.read())


def get_add_movie_order(start_timestamp, end_timestamp):
    """ Gets new movie order details after the timestamp """
    session = DB_SESSION()
    # Convert timestamp into datetime object
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

    # Use timestamp to query event
    orders = session.query(AddMovieOrder).filter(and_(AddMovieOrder.date_created >= start_timestamp_datetime, AddMovieOrder.date_created < end_timestamp_datetime))

    results_list = []
    # Convert each item to dictionary
    for order in orders:
        results_list.append(order.to_dict())

    session.close()

    logger.info("Query for Movie Order details after %s returns %d results" % (end_timestamp, len(results_list)))

    return results_list, 200

def get_payment(start_timestamp, end_timestamp):
    """ Gets new payment details after the timestamp """
    session = DB_SESSION()
    # Convert timestamp into datetime object
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

    # Use timestamp to query event
    payments = session.query(Payment).filter(and_(Payment.date_created >= start_timestamp_datetime, Payment.date_created < end_timestamp_datetime))

    results_list = []
    # Convert each item to dictionary
    for payment in payments:
        results_list.append(payment.to_dict())

    session.close()

    logger.info("Query for Payment details after %s returns %d results" % (end_timestamp, len(results_list)))

    return results_list, 200

def add_movie_order(body):
    """ Receives a movie order """

    session = DB_SESSION()

    morder = AddMovieOrder(body['customer_id'],
                      body['order_id'],
                      body['timestamp'],
                      body['movie'],
                      body['movie_price'],
                      body['movie_company']
                      )

    session.add(morder)

    session.commit()
    session.close()

    unique_id_movie_order = body['customer_id']
    logger.debug(f"Stored event add_movie_order request with a unique id of {unique_id_movie_order}")

    return NoContent, 201
    
def payment(body):
    """ Receives a payment """

    session = DB_SESSION()

    pay = Payment(body['customer_id'],
                      body['payment_id'],
                      body['timestamp'],
                      body['movie'],
                      body['movie_company'])

    session.add(pay)

    session.commit()
    session.close()

    unique_id_payment = body['customer_id']
    logger.debug(f"Stored event payment request with a unique id of {unique_id_payment}")

    return NoContent, 201

def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])

    retries = 0

    while retries < app_config["max_retries"]:

        try:
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["events"]["topic"])]
        except:
            logger.error("Connection Failed")
            time.sleep(app_config["sleep_time"])
            retries += 1


    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).

    consumer = topic.get_simple_consumer(consumer_group=b'event_group', reset_offset_on_start=False, auto_offset_reset=OffsetType.LATEST)

    # This is blocking - it will wait for a new message

    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)

        payload = msg["payload"]

        if msg["type"] == "add_movie_order":
            add_movie_order(payload)
        elif msg["type"] == "payment":
            payment(payload)

        # Commit the new message as being read
        consumer.commit_offsets()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    logger.info(f"Connecting to DB. Hostname:{app_config['datastore']['hostname']}, Port:{app_config['datastore']['port']}")
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
