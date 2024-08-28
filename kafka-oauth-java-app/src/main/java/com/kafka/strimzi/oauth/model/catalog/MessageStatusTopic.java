package com.kafka.strimzi.oauth.model.catalog;

import lombok.AllArgsConstructor;
import lombok.Data;


@Data
@AllArgsConstructor
public class MessageStatusTopic {
    private String name;
    private Integer messageBusId;
    private String specificationReference;
    private String encoding;

}