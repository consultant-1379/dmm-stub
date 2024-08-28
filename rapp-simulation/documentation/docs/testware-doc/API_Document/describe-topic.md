Get Request for Describing the Topics.
--------------------------------------

Description:

This API will get Describe Topic as per the Topic.

Path: GET /resources/topic/topic-name/describe

curl -I -X GET http://127.0.0.1:5000/topic/topic-name/describe


API Body:- 
@app.route('/topic/topic/describe',methods=['GET'])

def describe(topic):

    #Running multiple consumers
    broker = 'eric-oss-dmm-kf-op-sz-kafka-bootstrap:9092'
    response = requests.get('http://127.0.0.1:5000/topic/'+topic)
    if response.status_code != 200:
        abort(400,"Topic is not available")

    admin = KafkaManager(broker,topic)
    describe=admin.describe_topic()
    return describe
    
    
Response: