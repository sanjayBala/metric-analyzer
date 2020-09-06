import psycopg2, os, json

def print_json(json_object):
    """
        pretty printing json
    """
    print(json.dumps(json_object, indent=2, sort_keys=True)) 

def connectDB():
    try:
        print("Trying to make a connection to the DB...")
        DATABASE_URL = os.environ['DATABASE_URL']
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        print("Connected to the DB...")
        return conn
    except Exception as error:
        print ("Oops! An exception has occured:", error)
        print ("Exception TYPE:", type(error))
        return

def insertDeployPoint(repo_name, check_suite_id, timestamp, status):
    conn = connectDB()
    cursor = conn.cursor()
    try:
        print("Trying to add row...")
        sql_query = "INSERT INTO metric_deployment(repository_name, pipeline_id, pipeline_timestamp, pipeline_status) values (%s, %s, %s, %s);"
        data = (repo_name, int(check_suite_id), timestamp, status)
        print("##DEGBUG")
        for i in data:
            print(str(type(i))+ ":" + str(i))
        cursor.execute(sql_query, data)
        conn.commit()
        print("Inserted!")
    except Exception as error:
        print ("Oops! An exception has occured:", error)
        print ("Exception TYPE:", type(error))
    finally:
        cursor.close()
        conn.close()

def retriveDeployPoints():
    LDIF = {
        "connectorType": "cloudockit",
        "connectorId": "CDK",
        "connectorVersion": "1.0.0",
        "lxVersion": "1.0.0",
        "lxWorkspace": "workspace-id",
        "description": "Deployment Metric",
        "processingDirection": "inbound",
        "processingMode": "partial",
        "content": []
    }
    sql_query = "SELECT repository_name, pipeline_id, pipeline_timestamp, pipeline_status FROM metric_deployment;"
    conn = connectDB()
    cursor = conn.cursor()
    cursor.execute(sql_query)
    deploy_records = cursor.fetchall()
    for entry in deploy_records:
        deploy_point = {
            "type": "DeployPoint",
            "id": entry[0],
            "data": {
                "isSuccess": entry[3],
                "timestamp": entry[2],
                "ciPipelineId": entry[1]
            }
        }
        LDIF['content'].append(deploy_point)
    return LDIF

def testParser(json_object):
    """
        takes in a github webhook json, 
        parses it and does a bit of metadata processing
    """
    # checking if it really is a check_suite json object
    if 'check_suite' in json_object and json_object['action'] == 'completed':
        if json_object['check_suite']['conclusion'] == 'success':
            # repo metadata
            repo_name = str(json_object['repository']['name']).strip()
            # CI metadata
            check_suite = json_object['check_suite']
            check_suite_id = str(check_suite['id'])
            timestamp = str(check_suite['updated_at'])
            conclusion = check_suite['conclusion']=='success'
            print("#####################################################################")
            print("INFO CI-ID#" + check_suite_id + ": This looks like a valid deployment | Deployment Timestamp: " + timestamp)
            # aggregating the POST requests into data points
            deploy_point = {
                        "type": "DeployPoint",
                        "id": repo_name,
                        "data": {
                            "isSuccess": conclusion,
                            "timestamp": timestamp,
                            "ciPipelineId": check_suite_id
                        }
                    }
            print_json(deploy_point)
            # aggregating that into a file for now
            insertDeployPoint(repo_name, check_suite_id, timestamp, conclusion)      
            print("#####################################################################")
        else:
            print("#####################################################################")
            print("INFO: This seems to be a failed deployment")
            print("#####################################################################")
