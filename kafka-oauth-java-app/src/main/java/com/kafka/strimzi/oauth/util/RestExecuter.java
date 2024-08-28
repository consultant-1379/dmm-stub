package com.kafka.strimzi.oauth.util;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

@Service
public class RestExecuter {
    private static final Logger logger = LoggerFactory.getLogger(RestExecuter.class);
    @Autowired
    private RestTemplate restTemplate;

    public ResponseEntityDTO<String> makePutRequest(String url,HttpEntity<String> body){
        ResponseEntityDTO<String> responseEntity = new ResponseEntityDTO<>();
        try{
            ResponseEntity<String> response= restTemplate.exchange(url, HttpMethod.PUT,body,String.class);
            logger.info("DC body -{}",response);
            logger.info("DC Called -{}",response.getStatusCode());
            responseEntity.setResponseEntity(response);
        }
        catch(HttpClientErrorException error){
            logger.error("put request failed {} status", error.getMessage());
            responseEntity.setResponseEntity(new ResponseEntity<>(error.getStatusCode()));
        }
        catch(RestClientException error){
            responseEntity.setResponseEntity(new ResponseEntity<>(HttpStatus.SERVICE_UNAVAILABLE));
            logger.error("put request failed {} status", error.getMessage());
        }

        return responseEntity;

    }
}
