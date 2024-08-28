package com.kafka.strimzi.oauth.model.catalog;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
public class MessageDataTopic {
    private String name;
    private int messageBusId;
    private String encoding;
}
