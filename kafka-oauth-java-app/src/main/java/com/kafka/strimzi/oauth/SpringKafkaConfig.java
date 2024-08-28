package com.kafka.strimzi.oauth;

import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.kafka.config.ConcurrentKafkaListenerContainerFactory;
import org.springframework.kafka.core.ConsumerFactory;
import org.springframework.kafka.core.DefaultKafkaConsumerFactory;
import org.springframework.kafka.core.DefaultKafkaProducerFactory;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.core.ProducerFactory;

import io.strimzi.kafka.oauth.client.ClientConfig;
import io.strimzi.kafka.oauth.common.Config;
import io.strimzi.kafka.oauth.common.ConfigProperties;

@Configuration
@EnableKafka
public class SpringKafkaConfig {	@Value( "${kafka.bootstrapAddress}" )
private String bootstrapAddress;
@Value( "${security.protocol}" )
private String securityProtocol;
@Value( "${sasl.mechanism}" )
private String saslMechanism;
@Value( "${oauth.client.id}" )
private String clientId;
@Value( "${oauth.client.secret}" )
private String clientSecret;
@Value( "${oauth.token.endpoint.uri}" )
private String oauthTokenEndpointUri;
@Value( "${oauth.scope}" )
private String oauthScope;

@Value( "${group-id}" )
private String groupId;
@Value("${sasl.jaas.config}")
private String saslJaasConfig;
@Value("${sasl.login.callback.handler.class}")
private String saslLoginCallbackHandler;

@Value("${javax.net.ssl.trustStore}")
private String javaxTrustStore;
@Value("${javax.net.ssl.trustStorePassword}") 
private String javaxTrustStorePwd;

@Bean
public ProducerFactory<String, Object> producerFactory() {
	Map<String, Object> configMap = new HashMap<>();
	configMap.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapAddress);
	configMap.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
	configMap.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
	// configMap.put("security.protocol", securityProtocol);
	// configMap.put("sasl.mechanism",saslMechanism);
	// configMap.put("sasl.jaas.config", saslJaasConfig);
	// configMap.put("sasl.login.callback.handler.class", saslLoginCallbackHandler);

	
    // Properties defaults = new Properties();
    // defaults.setProperty(ClientConfig.OAUTH_TOKEN_ENDPOINT_URI, oauthTokenEndpointUri);
    // defaults.setProperty("javax.net.ssl.trustStore", javaxTrustStore);
    // defaults.setProperty("javax.net.ssl.trustStorePassword", javaxTrustStorePwd);

    // defaults.setProperty("oauth.client.id", clientId);
    // defaults.setProperty("oauth.client.secret", clientSecret);
    // defaults.setProperty(Config.OAUTH_SCOPE, oauthScope);
    // ConfigProperties.resolveAndExportToSystemProperties(defaults);
	return new DefaultKafkaProducerFactory<String, Object>(configMap);
	
}

@Bean
public KafkaTemplate<String, Object> kafkaTemplate() {
	return new KafkaTemplate<>(producerFactory());
}

 	 

@Bean
public ConsumerFactory<String,String> consumerFactory() {
	Map<String, Object> configMap = new HashMap<>();
	configMap.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapAddress);
	configMap.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
	configMap.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG,StringDeserializer.class.getName());
	configMap.put(ConsumerConfig.GROUP_ID_CONFIG, groupId);
	// configMap.put("security.protocol", securityProtocol);
	// configMap.put("sasl.mechanism", saslMechanism);
	// configMap.put("sasl.jaas.config", saslJaasConfig);
	// configMap.put("sasl.login.callback.handler.class", saslLoginCallbackHandler);

	// Properties defaults = new Properties();
	// defaults.setProperty(ClientConfig.OAUTH_TOKEN_ENDPOINT_URI, oauthTokenEndpointUri);
	// defaults.setProperty("javax.net.ssl.trustStore", javaxTrustStore);
    // defaults.setProperty("javax.net.ssl.trustStorePassword", javaxTrustStorePwd);
	// defaults.setProperty(Config.OAUTH_CLIENT_ID, clientId);
	// defaults.setProperty(Config.OAUTH_CLIENT_SECRET, clientSecret);
	// defaults.setProperty(Config.OAUTH_SCOPE, oauthScope);
	// ConfigProperties.resolveAndExportToSystemProperties(defaults);
	return new DefaultKafkaConsumerFactory<>(configMap);
}

@Bean
public ConcurrentKafkaListenerContainerFactory<String, String> kafkaListenerContainerFactory() {
	ConcurrentKafkaListenerContainerFactory<String, String> factory = new ConcurrentKafkaListenerContainerFactory<String, String>();
	factory.setConsumerFactory(consumerFactory());
	return factory;
}
}
