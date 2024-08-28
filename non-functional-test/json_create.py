import json
import os
import sys
import re
my_string  = sys.argv[1]
function_type = sys.argv[2]
# my_string = "[(eric-oss-data-catalog,8080,post,topics/test1,content-type: application/vnd.kafka.json.v2+json,1),(eric-oss-data-catalog,8080,post,topics/test1,content-type: application/vnd.kafka.json.v2+json,2)],[(eric-schema-registry,9590,post,catalog/v1/bulk-data-repository,content-type: application.json,1)]"
pairs = re.findall(r"\[(.*?)\]", my_string)
#print(pairs)  # Output: ['pair1', 'pair2', 'pair3']
for num in range(len(pairs)):
    pair = re.findall(r'\((.*?)\)', pairs[num])
    for num_pair in range(len(pair)):
        #print(pair[num_pair])
        value = pair[num_pair].split(",")
        print(value)
        service_name=value[0]
        port=value[1]
        method=value[2]
        path=value[3]
        head=value[4]
        status=value[5]
        count=value[6]
        with open('payload/'+function_type+"-"+service_name+'-'+count+'.json', 'r',newline='') as f:
            # Read the contents of the file
            payload = f.read().strip()
            # print(payload)

        # Print the contents of the file
        # print(payload)
        filename = "data.json"
        filepath = os.path.join(os.getcwd(), filename)
        if not os.path.exists(filepath):
            data = {}
        else:
            with open(filepath, "r") as f:
                data = json.load(f)

        # test= {
        #     "test": payload 
        # }
        # test1 = test.replace('\n', '')
        # print(test1)
        parsed_json = json.loads(payload)
        singleline_json_str = json.dumps(parsed_json, separators=(',', ':'))
        new_data = {
            service_name:{
                count:{
            "PORT": port,
            "METHOD": method,
            "PATH": path,
            "HEAD": head,
            "STATUS": status,
            "PAYLOAD": json.loads(singleline_json_str)
                }
            }
        }
        # Merge the new data with the existing data
        for parent_key, parent_value in new_data.items():
            if parent_key in data:
                # Append new child values to existing parent
                data[parent_key].update(parent_value)
            else:
                # Add new parent key to existing data
                data[parent_key] = parent_value
        # data.append(new_data)
        # print(data)
        

        with open(filepath, "w", newline='') as f:
            json.dump(data, f, ensure_ascii=False, indent=4,separators=(',', ':'))
        # data[service_name][count]["PAYLOAD"].replace("\n", "")

# port = 8080
# method = "POST"
# path = "topics/test1"
# service_name="eric-oss-dmm-kf-sz-bridge"
# head="content-type: application/vnd.kafka.json.v2+json"
# payload={    
#             "records": [
#             {
#                 "key": "key1",
#                 "value": "h"
#             },   
#             {
#                 "key": "key2",
#                 "value": "h"
#             },      
#             {
#                 "key": "key3",
#                 "value": "h"
#             },
#             {
#                 "key": "key4",
#                 "value": "h"
#             },   
#             {
#                 "key": "key5",
#                 "value": "h"
#             },      
#             {
#                 "key": "key6",
#                 "value": "h"
#             }
    
#         ]}
# filename = "data.json"
# filepath = os.path.join(os.getcwd(), filename)
# numbers = ["1", "2", "3", "4", "5"]
# # Create dictionary
# for num in numbers:
#     if not os.path.exists(filepath):
#         data = []
#     else:
#         with open(filepath, "r") as f:
#             data = json.load(f)

#     new_data = {
#         service_name:{
#         "PORT": port,
#         "METHOD": method,
#         "PATH": path,
#         "HEAD": head,
#         "PAYLOAD":payload
#         }
#     }
#     data.append(new_data)

#     with open(filepath, "w") as f:
#         json.dump(data, f)
