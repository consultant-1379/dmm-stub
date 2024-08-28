 package com.kafka.strimzi.oauth.util;

 import org.springframework.http.ResponseEntity;
 
 /**
  * Holds generic Response Entity to be used by RestExtractor
  */
 public class ResponseEntityDTO<T> {
 
     private ResponseEntity<T> responseEntity;
 
     public ResponseEntity<T> getResponseEntity() {
         return responseEntity;
     }
 
     public void setResponseEntity(ResponseEntity<T> responseEntity) {
         this.responseEntity = responseEntity;
     }
 }