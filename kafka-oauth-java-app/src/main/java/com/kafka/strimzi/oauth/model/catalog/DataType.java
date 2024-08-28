package com.kafka.strimzi.oauth.model.catalog;


import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor

public class DataType {
    private String mediumType;
    private String schemaName;
    private String schemaVersion;
    @JsonProperty("isExternal")
    private boolean isExternal = true;
    private String consumedDataProvider = "";
    private String consumedDataSpace = "";
    private String consumedDataCategory = "";
    private String consumedSchemaName = "";
    private String consumedSchemaVersion = "";
    public DataType(String mediumType, String schemaName,String schemaVersion){
        this.mediumType =mediumType;
        this.schemaName = schemaName;
        this.schemaVersion = schemaVersion;
    }
}
