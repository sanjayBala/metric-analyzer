import json

def print_json(json_object):
    """
        pretty printing json
    """
    print(json.dumps(json_object, indent=2)) 

def testParser(json_object):
    # checking if it really is a check_suite json object
    if 'check_suite' in json_object and json_object['action'] == 'completed':
        if json_object['check_suite']['conclusion'] == 'success':
            # repo metadata
            repo_name = str(json_object['repository']['name'])
            # CI metadata
            check_suite = json_object['check_suite']
            check_suite_id = str(check_suite['id'])
            timestamp = str(json_object['check_suite']['updated_at'])
            conclusion = str(json_object['check_suite']['conclusion'])
            print("#####################################################################")
            print("INFO CI-ID#" + check_suite_id + ": This looks like a valid deployment | Deployment Timestamp: " + timestamp)
            # aggregating the POST requests into data points
            deploy_point = {
                        "type": "DeployPoint",
                        "id": repo_name,
                        "data": {
                            "status": conclusion,
                            "timestamp": timestamp,
                            "ciPipelineId": check_suite_id
                        }
                    }
            print_json(deploy_point)
            # aggregating that into a file for now
            with open('./data/aggregation.json', 'r+') as file:
                print("Aggregating data...")
                aggregated_json = json.load(file)
                file.seek(0)
                aggregated_json['content'].append(deploy_point)
                # sorting keys to maintain order
                json.dump(aggregated_json, file, indent=2, sort_keys=True)         
                print("Done...")       
                #json.dumps(deploy_point)
            print("#####################################################################")
        else:
            print("#####################################################################")
            print("INFO: This seems to be a failed deployment")
            print("#####################################################################")
