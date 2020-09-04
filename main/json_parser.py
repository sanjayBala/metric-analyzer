import json

def print_json(json_object):
    print(json.dumps(json_object, indent = 1)) 

def testParser(json_object):
    #print_json(json_object)
    if  'check_suite' in json_object and json_object['action']=='completed':
        if json_object['check_suite']['conclusion']=='success':
            # repo metadata
            repo_name = str(json_object['repository']['name'])
            # CI metadata
            check_suite = str(json_object['check_suite'])
            check_suite_id = str(check_suite['id'])
            timestamp = str(json_object['check_suite']['updated_at'])
            conclusion = str(json_object['check_suite']['conclusion'])
            print("#####################################################################")
            print("INFO CI-ID#" + check_suite_id + ": This looks like a valid deployment | Deployment Time: " + timestamp)
            deploy_point = {
                "connectorType": "cloudockit",
                "connectorId": "CDK",
                "connectorVersion": "1.0.0",
                "lxVersion": "1.0.0",
                "lxWorkspace": "workspace-id",
                "description": "Deployment Metric",
                "processingDirection": "inbound",
                "processingMode": "partial",
                "content": [
                    {
                        "type": "DeployPoint",
                        "id": repo_name,
                        "data": {
                            "status": conclusion,
                            "timestamp": timestamp,
                            "ciPipelineId": check_suite_id
                        }
                    }
                ]
            }
            #json.dumps(deploy_point)
            print_json(deploy_point)
            print("#####################################################################")
        else:
            print("#####################################################################")
            print("INFO: This seems to be a failed deployment")
            print("#####################################################################")
