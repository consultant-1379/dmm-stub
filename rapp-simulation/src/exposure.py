import requests
import json
from logger_config import logger
from autz import ClientToken
import config
class ApiExposure:
    def app_service_exposure(self):
        tokenClass=ClientToken()
        token=tokenClass.retrieve_token()        
        try:
            headers= {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
            payload = {
                "id": "rapp-simulation-002",
                "predicates": [
                    {
                    "name": "Path",
                    "args": { "_genkey_0": "/rapp-simulation/**" }
                    }
                ],
               "filters":[
                  {
                    "name": "StripPrefix",
                    "args": {
                        "_genkey_0": 1
                    }
                    }
                ],
                "uri": "http://rapp-simulation:8082"
                }
            resp = requests.post(f"{config.gas_uri}/v1/routes", verify=config.platformcaCertFileFullPath,headers=headers, data=json.dumps(payload))
            resp.raise_for_status()  # Raise an exception for bad status codes
            if resp.status_code ==200:
                logger.info(f"App service exposure create sucessfully")
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred while while creating service exposure: {e}")
  
    def access_control(self):
        tokenClass=ClientToken()
        token=tokenClass.retrieve_token()
        try:
            headers= {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
            payload = {
                "tenant": "master",
                "roles": [
                    {
                        "name": "Rapp_simulation_operation"
                    }
                ],
                "authorization": {
                    "resources": [
                        {
                            "name": "rapp_simulation",
                            "type": "urn:eo:resourcess:extrapp",
                            "ownerManagedAccess": False,
                            "uris": [
                                "/rapp-simulation/list-object",
                                "/rapp-simulation/get-object/**",
                                "/rapp-simulation/write-object/**",
                                "/rapp-simulation/delete-object/**"
                            ],
                            "scopes": [
                                {
                                    "name": "PATCH"
                                },
                                {
                                    "name": "DELETE"
                                },
                                {
                                    "name": "GET"
                                },
                                {
                                    "name": "POST"
                                },
                                {
                                    "name": "PUT"
                                }
                            ]
                        }
                    ],
                    "policies": [
                        {
                            "name": "Rapp simulation",
                            "type": "role",
                            "logic": "POSITIVE",
                            "decisionStrategy": "UNANIMOUS",
                            "config": {
                                "roles": "[{\"id\":\"Rapp_simulation_operation\",\"required\":false}]"
                            }
                        },
                        {
                            "name": "Rapp simulation Permission",
                            "type": "scope",
                            "logic": "POSITIVE",
                            "decisionStrategy": "AFFIRMATIVE",
                            "config": {
                                "resources": "[\"rapp_simulation\"]",
                                "scopes": "[\"GET\",\"POST\",\"DELETE\"]",
                                "applyPolicies": "[\"Rapp simulation\"]"
                            }
                        }
                    ],
                    "scopes": [
                        {
                            "name": "GET"
                        },
                        {
                            "name": "POST"
                        },
                        {
                            "name": "DELETE"
                        },
                        {
                            "name": "PUT"
                        },
                        {
                            "name": "PATCH"
                        }
                    ]
                }
            }
            resp = requests.post(f"{config.gas_uri}/idm/rolemgmt/v1/extapp/rbac", verify=config.platformcaCertFileFullPath,headers=headers, data=json.dumps(payload))
            resp.raise_for_status()  # Raise an exception for bad status codes
            if resp.status_code ==200:
                logger.info(f"App service exposure create sucessfully")
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred while while creating service exposure: {e}")  
