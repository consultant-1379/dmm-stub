package com.kafka.strimzi.oauth.consumer;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.config.KafkaListenerEndpointRegistry;
import org.springframework.retry.RetryCallback;
import org.springframework.stereotype.Component;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.kafka.strimzi.oauth.constant.ApplicationConstant;
import com.kafka.strimzi.oauth.service.DataCatalogService;
import com.kafka.strimzi.oauth.util.ResponseEntityDTO;
import com.kafka.strimzi.oauth.util.RetryUtil;

@Component
public class KafkaConsumer {

	private static final Logger logger = LoggerFactory.getLogger(KafkaConsumer.class);


	@Autowired
	KafkaListenerEndpointRegistry kafkaListenerEndpointRegistry;
	

	@KafkaListener(id="id1",groupId = "${group-id}", topics = "${topic-name}", containerFactory = ApplicationConstant.KAFKA_LISTENER_CONTAINER_FACTORY,autoStartup = "false")
	public void receivedMessage(String message) throws JsonProcessingException {
			logger.info("Message received using Kafka listener " + message);
	}
}

