package com.kafka.strimzi.oauth.model.catalog;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class DataServiceForMessageSchemaPut {
    private String dataServiceName;
}
