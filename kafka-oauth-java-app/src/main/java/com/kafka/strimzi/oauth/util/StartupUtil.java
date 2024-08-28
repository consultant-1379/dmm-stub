package com.kafka.strimzi.oauth.util;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.event.EventListener;
import org.springframework.scheduling.annotation.Async;

import com.kafka.strimzi.oauth.service.DataCatalogService;

@Configuration
public class StartupUtil {
    private static final Logger logger = LoggerFactory.getLogger(StartupUtil.class);
    @Autowired
	private DataCatalogService DcService;

	@Autowired
	private RetryUtil retryUtil;
    @Async
    @EventListener(ApplicationReadyEvent.class)
	public void startupRegisterMessageSchema(){
		retryUtil.retryTemplate(100, 10000).execute(context ->DcService.registerMessageSchema());
	}
}
