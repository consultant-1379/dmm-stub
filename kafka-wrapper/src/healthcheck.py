import time
import requests
from logger_config import logger

def healthCheck():    
    while True:
        try:
            response = requests.get('http://127.0.0.1:8082/health')
            if response.status_code == 200:
                logger.info("Wrapper is ready")
                break
        except requests.ConnectionError:
            logger.error("Connection refused. Retrying in 5 seconds...")
            time.sleep(5)