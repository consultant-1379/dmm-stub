package com.kafka.strimzi.oauth.model.catalog;


import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;

@AllArgsConstructor
@Data
@Builder
public class MessageSchemaPut {
    private DataSpace dataSpace;
    private DataServiceForMessageSchemaPut dataService;
    private DataServiceInstance dataServiceInstance;
    private DataCategory dataCategory;
    private DataProviderTypeForMessageSchemaPUT dataProviderType;
    private MessageStatusTopic messageStatusTopic;
    private MessageDataTopic messageDataTopic;
    private DataType dataType;
    private SupportedPredicateParameter supportedPredicateParameter;
    private MessageSchema messageSchema; 
}
