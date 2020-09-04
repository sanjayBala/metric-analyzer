import json

def print_json(json_object):
    print(json.dumps(json_object, indent = 1)) 

def testParser(json_object):
    #print_json(json_object)
    if  'check_suite' in json_object and json_object['action']=='completed':
        if json_object['check_suite']['conclusion']=='success':
            check_suite_id = str(json_object['check_suite']['id'])
            print("INFO ID#" + check_suite_id + ": This looks like a valid deployment | Deployment Time: " + str(json_object['check_suite']['updated_at']))
        else:
            print("INFO: This seems to be a failed deployment")
