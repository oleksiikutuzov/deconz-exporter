from prometheus_client import start_http_server
from http import client, HTTPStatus
import logging
import time
import sys
import os
import deconz
import signal
from threading import Event

"""
Environment variable labels used to read values from.
HOST_PORT       Sets port to run the prometheus http server, default to 9090
DECONZ_PORT     Sets deconz port, if its not set it will, default to 80
DECONZ_URL      Sets deconz url, default is 'localhost'
DECONZ_TOKEN    Sets deconz token, default is ''
UPDATE_INTERVAL Sets interval between updates in seconds, default is 10.0 seconds
"""
POST_LABEL = 'HOST_PORT'
DECONZ_PORT_LABEL = 'DECONZ_PORT'
URL_LABEL = 'DECONZ_URL'
TOKEN_LABEL = 'DECONZ_TOKEN'
TIMEOUT_LABEL = 'UPDATE_INTERVAL'

exit = Event()


def signalShuttdown(self, *args):
    exit.set()


config = {
    'target_port': 9090,
    'host_port': 80,
    'url': 'localhost',
    'token': '',
    'timeout': 10.0
}

if POST_LABEL in os.environ:
    config['host_port'] = int(os.environ[POST_LABEL
                                         ])

if DECONZ_PORT_LABEL in os.environ:
    config['target_port'] = int(os.environ[DECONZ_PORT_LABEL
                                           ])

if URL_LABEL in os.environ:
    config['url'] = os.environ[URL_LABEL
                               ]

if TOKEN_LABEL in os.environ:
    config['token'] = os.environ[TOKEN_LABEL
                                 ].strip()

if TIMEOUT_LABEL in os.environ:
    config['timeout'] = float(os.environ[TIMEOUT_LABEL
                                         ])


def create_logger(scope):
    logger = logging.getLogger(scope)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%Y-%m-%dT%H:%M:%S"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


if __name__ == '__main__':
    logger = create_logger('deconz-exporter')

    if not config['token']:
        logger.error(f"No deconz token provided.")
        sys.exit(1)

    start_http_server(config['host_port'])
    connection = client.HTTPConnection(config['url'], config['target_port'])
    path = "/api/{}/sensors".format(config['token'])

    signal.signal(signal.SIGTERM, signalShuttdown)
    signal.signal(signal.SIGHUP, signalShuttdown)
    signal.signal(signal.SIGINT, signalShuttdown)
    signal.signal(signal.SIGABRT, signalShuttdown)

    while not exit.is_set():
        connection.request("GET", path)
        response = connection.getresponse()

        if response.status == 200:
            deconz.extract_metrics(logger, response.read())
            logger.info(f"Request succeeded")
        else:
            logger.error(
                f"Request did not result in a successful status, {response.status} {response.reason}.")

        sleepTime = 0.0

        while (config['timeout'] > sleepTime) and not exit.is_set():
            time.sleep(0.1)
            sleepTime += 0.1

    logger.info("shutting down")
