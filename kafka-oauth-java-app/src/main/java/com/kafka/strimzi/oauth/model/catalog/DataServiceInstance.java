package com.kafka.strimzi.oauth.model.catalog;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class DataServiceInstance {
	private String dataServiceInstanceName;
	private String consumedDataSpace = "";
	private String consumedDataCategory = "";
	private String consumedDataProvider ="";
	private String controlEndPoint = "";
	private String consumedSchemaName = "";
	private String consumedSchemaVersion = "";
	public DataServiceInstance(String dataServiceInstanceName){
		this.dataServiceInstanceName = dataServiceInstanceName;
	}
}
