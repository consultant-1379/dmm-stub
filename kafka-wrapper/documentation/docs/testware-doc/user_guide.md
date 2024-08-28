# USER GUIDE


Overview

This document provides an overview of the Kafka Wrapper. It gives a brief description of its main features.

The Kafka Wrapper provides support for retrieving topic from any Kafka that can return a topic as the endpoint of an URL, and also support for the Kafka which returns Topics in a custom endpoint format.

Description of the Service:
--------------------------
•	The consumer use Kafka Wrapper for the hitting the endpoint for topic, consume message and validate the messages.

•	This request go to Broker and Consumers for validating the topic.

•	It is developed from python flask module.

Supported Endpoints:
The function of Kafka Wrapper is to validate topic through GET and Describe endpoints.

The key use cases supported for Kafka represented through Table are as follows:

Table :  Kafka Wrapper



| S.No.        |   Supported Topics                     |           Endpoints                         |                    Description                                     |
|--------------|----------------------------------------|---------------------------------------------|--------------------------------------------------------------------|
| 1            |   Get request for Counting Topics    	|  GET /resources/topic/topic-name/int:count  |   This endpoint will get number of message as per the topic.       |
| 2            |   Get request for Topics               |  GET /resources/topic/topic-name            |   This endpoint will get Topic name as per the Topic.	           |
| 3            |   Get Request for Describing Topics    |  GET /resources/topic/topic-name/describe   |   This endpoint will get Describe Topic name as per the Topic.     |





  

  

