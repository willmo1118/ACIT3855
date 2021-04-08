import connexion
import json
from connexion import NoContent
from pykafka import KafkaClient
import logging.config
import yaml
from flask_cors import CORS, cross_origin
import os

# if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
#     print("In Test Environment")
#     app_conf_file = "/config/app_conf.yaml"
#     log_conf_file = "/config/log_conf.yaml"
# else:
#     print("In Dev Environment")
#     app_conf_file = "app_conf.yaml"
#     log_conf_file = "log_conf.yaml"

# with open(app_conf_file, 'r') as f:
#     app_config = yaml.safe_load(f.read())


# # External Logging Configuration
# with open(log_conf_file, 'r') as f:
#     log_config = yaml.safe_load(f.read())
#     logging.config.dictConfig(log_config)

# logger = logging.getLogger('basicLogger')

# logger.info("App Conf File: %s" % app_conf_file)
# logger.info("Log Conf File: %s" % log_conf_file)

with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())


with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def get_add_movie_order(index):
    """ Get Movie Order Report in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]



    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=600)

    logger.info("Retrieving order report at index %d" % index)
    count = 0
    movie_order = None
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == "add_movie_order":
                if count == index:
                    movie_order = msg["payload"]
                    return movie_order, 200
                count += 1
    except:
        logger.error("No more messages found")


    logger.error("Could not find movie order report at index %d" % index)
    return {"message": "Not Found"}, 404

def get_payment(index):
    """ Get Payment Report in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=600)
    logger.info("Retrieving payment report at index %d" % index)

    count = 0
    payment = None
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == "payment":
                if count == index:
                    payment = msg["payload"]
                    return payment, 200
                count += 1
    except:
        logger.error("No more messages found")

    logger.error("Could not find payment report at index %d" % index)
    return {"message": "Not Found"}, 404



app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110)
