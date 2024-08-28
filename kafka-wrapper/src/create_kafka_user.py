import yaml
import os
from kubernetes import client, config
import configuration
# Load Kubernetes configuration from default location
config.load_incluster_config()

# Define the CRD Group, Version, and Plural
group = "kafka.strimzi.io"
version = "v1alpha1"
plural = "kafkausers"
namespace = configuration.namespace

class KafkaUser:
    def __init__(self, KafkaUser):
        self.KafkaUser = KafkaUser
    def create_kafka_user(self):
        KafkaUser = self.KafkaUser
        print(KafkaUser)
        api = client.CustomObjectsApi()
        for user in KafkaUser:
            kafka_user = {
                "apiVersion": f"{group}/{version}",
                "kind": "KafkaUser",
                "metadata": {
                    "name": user,  # Replace with the desired username
                    "namespace": namespace,
                    "labels": {
                        "strimzi.io/cluster": "eric-oss-dmm-kf-op-sz"
                    },
                },
                "spec": {
                    "authentication": {
                        "type": "tls-external",
                    },
                    "authorization": {
                        "type": "simple",
                        "acls": [
                            {
                                "resource": {
                                    "type": "group",
                                    "name": "*",  # Replace with the desired topic name
                                },
                                "operation": "All",
                            },
                        ],
                    },
                },
            }

            api.create_namespaced_custom_object(
                group=group,
                version=version,
                namespace=namespace,
                plural=plural,
                body=kafka_user,
            )
            print("KafkaUser created successfully.")
        return("KafkaUser created successfully.")


    def delete_kafka_user(self):
        KafkaUser = self.KafkaUser
        api = client.CustomObjectsApi()
        for user in KafkaUser:
            api.delete_namespaced_custom_object(
                group=group,
                version=version,
                namespace=namespace,
                plural=plural,
                name=user,
                body=client.V1DeleteOptions(),
            )
            print(f"KafkaUser '{user}' deleted successfully.")
        return((f"KafkaUser '{KafkaUser}' deleted successfully."))
