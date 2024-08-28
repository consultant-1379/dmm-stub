package com.kafka.strimzi.oauth.producer;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/produce")
public class KafkaProducer {

	@Value( "${topic-name}" )
	private String topicName;

	@Autowired
	private KafkaTemplate<String, Object> kafkaTemplate;

	
	@PostMapping("/message")
	public String sendMessage(@RequestParam String message) {

		try {
			kafkaTemplate.send(topicName, message);
		}
		catch (Exception e) {
			e.printStackTrace();
		}
		return "Message sent succuessfully";
	}



}
