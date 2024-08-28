from prometheus_client import Counter, Summary

produce_message = Counter('kafka_wrapper_produce_message', 'Number of messages produced to kafka topic', ['topic'])
consume_message = Counter('kafka_wrapper_consume_message', 'Number of messages consumed from kafka topic', ['topic'])