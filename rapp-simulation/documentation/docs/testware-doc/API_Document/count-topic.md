Get Request for Counting the topics.
------------------------------------

Description:

This API will get counting topics as per the topics.

Path: GET /resources/topic/topic-name/int:count

curl -I -X GET http://127.0.0.1:5000/topic/topic-name/int:count


API body:- 

@app.route('/topic/topic/int:count',methods=['GET'])
  
def test(topic,count):

    #Running multiple consumers
    broker = 'eric-oss-dmm-kf-op-sz-kafka-bootstrap:9092'
    group_id = 'consumer-1'

    consumer1 = MessageConsumer(broker,topic,group_id,count)
    msg=consumer1.activate_listener()
    return msg 
    
    
Response: