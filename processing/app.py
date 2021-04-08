import connexion
import json
from connexion import NoContent
import os.path
import requests
import yaml
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
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


url = app_config["eventstore"]["url"]
json_file = app_config["datastore"]["filename"]
time_interval = app_config['scheduler']['period_sec']

def populate_stats():
    """ Periodically update stats """
    logger.info("Processing")
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    if os.path.isfile(json_file):
        with open(json_file, 'r') as file:
            data = json.loads(file.read())
            last_datetime = data["end_timestamp"]
            data["start_timestamp"] = last_datetime
            data["end_timestamp"] = now
            url_order = url + "/orders/movie_orders?start_timestamp=" + last_datetime + "&end_timestamp=" + now
            url_payment = url + "/orders/payments?start_timestamp=" + last_datetime + "&end_timestamp=" + now
            try:
                response1 = requests.get(url_order)
                

                if response1.status_code == 200:
                    order_data = response1.json()
                    len_order_data = len(order_data)
                    data["num_movie_orders"] += len_order_data

                    movie_price_list = [i["movie_price"] for i in order_data]
                    data["sum_movie_price"] += round(sum(movie_price_list), 2)

                    if data["num_movie_orders"] == 0:
                        data["avg_movie_price"] == 0
                    else:
                        average_price = data["sum_movie_price"] / data["num_movie_orders"]
                        data["avg_movie_price"] = round(average_price, 2)

                logger.info(f"Returned number of order events {data['num_movie_orders']}")
                logger.info(f"Processed number of order events {len_order_data}")

                response2 = requests.get(url_payment)

                if response2.status_code == 200:
                    payment_data = response2.json()
                    len_payment_data = len(payment_data)
                    data["num_payments"] += len_payment_data

                logger.info(f"Returned number of payment events {data['num_payments']}")
                logger.info(f"Processed number of order events {len_payment_data}")
            
                with open(json_file, 'w') as file:
                    json_data = json.dumps(data)
                    file.write(json_data)
                logger.debug(f"Current Statistics: {data}")
            except requests.exceptions.RequestException as e:
                logger.error(e)
    else:
        with open(json_file, 'w') as file:
            default_data = {"start_timestamp": now,"end_timestamp": now, "num_movie_orders": 0, "num_payments": 0, "sum_movie_price": 0, "avg_movie_price": 0}
            json_data = json.dumps(default_data)
            file.write(json_data)
        logger.debug(f"Current Statistics: {default_data}")

    logger.info("Done Processing")

def get_stats():

    if os.path.isfile(json_file):
        with open(json_file, "r") as file:
            data = json.loads(file.read())
            logger.debug(f"Current Statistics: {data}")
            logger.info("Your request has completed")
        return data, 200
    else:
        logger.error("No data.json exist")
        return "Statistics do not exist", 404

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval',
                  seconds=time_interval)
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)
