package com.kafka.strimzi.oauth.service;
import java.util.LinkedHashMap;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.kafka.strimzi.oauth.model.catalog.DataCategory;
import com.kafka.strimzi.oauth.model.catalog.DataProviderTypeForMessageSchemaPUT;
import com.kafka.strimzi.oauth.model.catalog.DataServiceForMessageSchemaPut;
import com.kafka.strimzi.oauth.model.catalog.DataServiceInstance;
import com.kafka.strimzi.oauth.model.catalog.DataSpace;
import com.kafka.strimzi.oauth.model.catalog.DataType;
import com.kafka.strimzi.oauth.model.catalog.MessageDataTopic;
import com.kafka.strimzi.oauth.model.catalog.MessageSchema;
import com.kafka.strimzi.oauth.model.catalog.MessageSchemaPut;
import com.kafka.strimzi.oauth.model.catalog.MessageStatusTopic;
import com.kafka.strimzi.oauth.model.catalog.SupportedPredicateParameter;
import com.kafka.strimzi.oauth.util.ResponseEntityDTO;
import com.kafka.strimzi.oauth.util.RestExecuter;

@Service

public class DataCatalogService {
    private static final Logger logger = LoggerFactory.getLogger(DataCatalogService.class);
    @Autowired
    private RestExecuter restExecuter;

    @Value("${message-schema-url}")
    private String messageSchemaURL;


    private ResponseEntityDTO<String> response;
    private HttpEntity<String> entity;

    private HttpEntity<String> responseBody(final Map<String, Object> requestBody) throws JsonProcessingException{
        final HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        String jsonData = new ObjectMapper().writeValueAsString(requestBody);
        logger.info("JSON to be Sent {}", jsonData);
        return new HttpEntity<>(jsonData, headers);
    }
    public ResponseEntityDTO<String> registerMessageSchema(){
        MessageSchemaPut messageSchema = updateMessageSchemaValues();
        final Map<String, Object> messageSchemaTypeBody =generateMessageSchemaPutPaylod(messageSchema);

        try {
            entity = responseBody(messageSchemaTypeBody);
            response= restExecuter.makePutRequest(messageSchemaURL, entity);
            logger.info("response {}",response.getResponseEntity().getStatusCode().value());
            if (response.getResponseEntity().getStatusCode().value() == 201 || response.getResponseEntity().getStatusCode().value() == 200 || response.getResponseEntity().getStatusCode().value() == 409){
                logger.info("Sucessfully created message schema {} :: {}", response.getResponseEntity().getStatusCode().value(),response.getResponseEntity().getBody());
            }else  if (response.getResponseEntity().getStatusCode().value() == 408) {
                logger.info("Unable to register Message Schema as another process is already attempting to register. We should retry");
                throw new RestClientException("Unable to register Message Schema. Error code from Data Catalog: " + response.getResponseEntity().getStatusCode());
            } else  if (response.getResponseEntity().getStatusCode().is4xxClientError()) {
                logger.error("Unable to register Message Schema. Error code: {}", response.getResponseEntity().getStatusCode());
                throw new RestClientException("Unable to register Message Schema. Error code from Data Catalog: " + response.getResponseEntity().getStatusCode());
            }
        } catch (JsonProcessingException e) {
            logger.error("failed to processing JSON object {}", e);
            e.printStackTrace();
        }       
        return response;

    }
    private Map<String,Object> generateMessageSchemaPutPaylod(final MessageSchemaPut messageSchema){
        final Map<String,Object> messageSchemaBody = new LinkedHashMap<>(10);
        messageSchemaBody.put("dataSpace", messageSchema.getDataSpace());
        messageSchemaBody.put("dataService", messageSchema.getDataService());
        messageSchemaBody.put("dataCategory", messageSchema.getDataCategory());
        messageSchemaBody.put("dataProviderType", messageSchema.getDataProviderType());
        messageSchemaBody.put("messageStatusTopic", messageSchema.getMessageStatusTopic());
        messageSchemaBody.put("messageDataTopic", messageSchema.getMessageDataTopic());
        messageSchemaBody.put("dataServiceInstance", messageSchema.getDataServiceInstance());
        messageSchemaBody.put("dataType", messageSchema.getDataType());
        messageSchemaBody.put("supportedPredicateParameter", messageSchema.getSupportedPredicateParameter());
        messageSchemaBody.put("messageSchema", messageSchema.getMessageSchema());
        return messageSchemaBody;

    }

    /**
     * @param messageschema
     * @return
     */
    private MessageSchemaPut updateMessageSchemaValues(){
        MessageSchemaPut updated = MessageSchemaPut.builder()
                    .dataSpace(new DataSpace("17G"))
                    .dataService(new DataServiceForMessageSchemaPut("kafka-wrapperr"))
                    .dataServiceInstance(new DataServiceInstance("dsinst10111"))
                    .dataCategory(new DataCategory("app-eng-PM_statee"))
                    .dataProviderType(new DataProviderTypeForMessageSchemaPUT("wrapper"))
                    .messageStatusTopic(new MessageStatusTopic("streams_topic",1,"SppecRef101","JSON"))
                    .messageDataTopic(new MessageDataTopic("streams_topic",1, "JSON"))
                    .dataType(new DataType("stream", "RANSCHEMAA", "3"))
                    .supportedPredicateParameter(new SupportedPredicateParameter("pd10111", true))
                    .messageSchema(new MessageSchema("SpecRef20200"))
                    .build();
        return updated;
    }
}
