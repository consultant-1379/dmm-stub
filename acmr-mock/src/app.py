from route import app
import configuration
import multiprocessing
from consumer_oauth import MessageConsumeOauth
import uuid
from logger_config import logger
if __name__ == '__main__':
    initial = MessageConsumeOauth(configuration.broker,"policy-acruntime-participant",str(uuid.uuid4()))
    test_thread = multiprocessing.Process(target=initial.consume_from_topic)
    test_thread.start()
    app.run(host='0.0.0.0',port="8083")
