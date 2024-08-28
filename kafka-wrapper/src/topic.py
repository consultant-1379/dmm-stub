from kafka import KafkaAdminClient ,KafkaClient, TopicPartition
from flask import abort , jsonify
from kafka.admin import ConfigResource, ConfigResourceType , NewTopic
class KafkaManager:
    def __init__(self, bootstrap_servers,topic=None,partitions=None,replication=None):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.partitions = partitions
        self.replication = replication
        self.admin_client = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
        self.kafka_client = KafkaClient(
            bootstrap_servers=self.bootstrap_servers
            )

    def create_topic(self):  
        # Create a NewTopic object
        topic_list = self.admin_client.list_topics()
        for topic in self.topic:
            if topic not in topic_list:
                print(f"Topic is not available {topic}")
                new_topic = NewTopic(
                    name=topic,
                    num_partitions=self.partitions,
                    replication_factor=self.replication,
                )
                # Create the topic
                self.admin_client.create_topics(new_topics=[new_topic])
                # Close the KafkaAdminClient
        self.admin_client.close()
        msg="Topic is Created suessfully "
        return msg

    def describe_topic(self):
        topic_name = self.topic
        topic_list = [topic_name]

        # Fetch topic metadata
        topic_metadata = self.admin_client.describe_topics(topic_list)
        # Find the desired topic in the metadata list
        target_topic = None
        for topic in topic_metadata:
            print(topic)
            if topic["topic"] == topic_name:
                target_topic = topic
                break

        if target_topic is None:
            print(f"Topic '{topic_name}' not found.")
            return

        # Print relevant information about the topic
        print("Topic Name:", target_topic["topic"])
        print("Number of Partitions:", len(target_topic["partitions"]))
        print("Replication Factor:", len(target_topic["partitions"][0]["replicas"]))
        print("Partitions Information:")
        if target_topic['partitions']:
            replicas_count = len(target_topic['partitions'][0]['replicas'])
            print("Replicas Count:", replicas_count)
            
        # Get topic configuration to retrieve the retention period
        config_resources = [ConfigResource(ConfigResourceType.TOPIC, topic_name)]
        topic_configs = self.admin_client.describe_configs(config_resources)

        # Print retention period
        # print(topic_configs[0].resources)
        retention=''
        for find in topic_configs[0].resources:
            print(find)
            if isinstance(find,tuple):
                for find1 in find:
                    if isinstance(find1,list):
                        for find2 in find1:
                            if isinstance(find2,tuple):
                                if find2[0] == "retention.ms":
                                    retention=find2[1]
        print(retention)
        self.admin_client.close()
        return {
            'topic_name': target_topic["topic"],
            'num_partitions': len(target_topic["partitions"]),
            'replica_assignment': len(target_topic["partitions"][0]["replicas"]),
            'retention_seconds': retention
        }


    def check_topic(self):
        mss=''
        topic_list = self.admin_client.list_topics()
        if self.topic in topic_list:
            print(f"Topic is available {self.topic}")
            msg="Topic is available "+ self.topic
        else:
            abort(400, self.topic + " topic is not available ")
        self.admin_client.close()
        return msg

    def list_topics(self):
        topic_list = self.admin_client.list_topics()
        print(topic_list)
        self.admin_client.close()
        return jsonify(topic_list)

    def delete_topic(self):  
        # delete a NewTopic object
        topic_list = self.admin_client.list_topics()
        for topic in self.topic:
            if topic in topic_list:
                print(f"Topic is available - {topic}")
                self.admin_client.delete_topics([topic])
                # Close the KafkaAdminClient
        self.admin_client.close()
        msg="Topic is Deleted suessfully "
        return msg