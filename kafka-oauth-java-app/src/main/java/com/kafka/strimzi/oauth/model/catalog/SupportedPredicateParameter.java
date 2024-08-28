package com.kafka.strimzi.oauth.model.catalog;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SupportedPredicateParameter {
    private String parameterName;
    @JsonProperty("isPassedToConsumedService")
    private boolean isPassedToConsumedService;
}
