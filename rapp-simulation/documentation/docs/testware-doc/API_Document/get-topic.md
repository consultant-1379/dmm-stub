Get request for Topics.
----------------------

Description:

This API will get Topic name as per the Topic.

Path: GET /resources/topic/topic-name

curl -I -X GET http://127.0.0.1:5000/topic/topic-name


API Body:- 
@app.route('/topic/topic',methods=['GET'])

def topic(topic):

    #Running multiple consumers
    broker = 'eric-oss-dmm-kf-op-sz-kafka-bootstrap:9092'
    admin = KafkaManager(broker,topic)
    topics=admin.list_topics()
    return topics
    
    
Response: