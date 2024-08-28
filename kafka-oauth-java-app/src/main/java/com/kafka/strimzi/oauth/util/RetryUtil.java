 package com.kafka.strimzi.oauth.util;

 import org.slf4j.Logger;
 import org.slf4j.LoggerFactory;
 import org.springframework.retry.backoff.FixedBackOffPolicy;
 import org.springframework.retry.policy.SimpleRetryPolicy;
 import org.springframework.retry.support.RetryTemplate;
 import org.springframework.stereotype.Component;
 
 
 @Component
 public class RetryUtil {
     private static final Logger logger = LoggerFactory.getLogger(RetryUtil.class);
 
     /**
      * Simpled retry template that use application variables set at deploy time for the number of
      * retry attempt and interval in mS.
      *
      * @returns false if all retries are exhausted
      */
     public RetryTemplate retryTemplate(int retryAttempts, int retryInterval) {
 
         SimpleRetryPolicy retryPolicy = new SimpleRetryPolicy();
         retryPolicy.setMaxAttempts(retryAttempts);
 
         FixedBackOffPolicy backOffPolicy = new FixedBackOffPolicy();
         backOffPolicy.setBackOffPeriod(retryInterval);
 
         RetryTemplate template = new RetryTemplate();
         template.setRetryPolicy(retryPolicy);
         template.setBackOffPolicy(backOffPolicy);
 
         return template;
     }
 

 
 
 }
 