import psycopg2, os, json
import urllib.parse as urlparse
def connectDB():
    try:
        print("Trying to make a connection to the DB...")
        DATABASE_URI = os.environ.get('DATABASE_URL')
        result = urlparse(DATABASE_URI)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        conn = psycopg2.connect(
            database = database,
            user = username,
            password = password,
            host = hostname
        )
        #conn = psycopg2.connect(dsn=DATABASE_URI)
        return conn
    except:
        print("Seems like DB connection failed...")

def insertDeployPoint(repo_name, check_suite_id, timestamp, conclusion):
    try:
        conn = connectDB()
        cursor = conn.cursor()
        sql = "INSERT INTO metric_deployment(repository_name, pipeline_id, pipeline_timestamp, pipeline_status) values (%s);"
        cursor.execute(sql, (repo_name, check_suite_id, timestamp, conclusion=='success'))
        conn.commit()
        print("Inserted!")
    except:
        print("Insert Failed!")
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
                "status": entry[3],
                "timestamp": entry[2],
                "ciPipelineId": entry[1]
            }
        }
        LDIF['content'].append(deploy_point)
    return LDIF

def print_json(json_object):
    """
        pretty printing json
    """
    print(json.dumps(json_object, indent=2)) 

def testParser(json_object):
    """
        takes in a github webhook json, 
        parses it and does a bit of metadata processing
    """
    # checking if it really is a check_suite json object
    if 'check_suite' in json_object and json_object['action'] == 'completed':
        if json_object['check_suite']['conclusion'] == 'success':
            # repo metadata
            repo_name = str(json_object['repository']['name'])
            # CI metadata
            check_suite = json_object['check_suite']
            check_suite_id = str(check_suite['id'])
            timestamp = str(check_suite['updated_at'])
            conclusion = str(check_suite['conclusion'])
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
            insertDeployPoint(repo_name, check_suite, timestamp, conclusion)
            with open('./data/aggregation.json', 'r+') as file:
                print("Aggregating data...")
                aggregated_json = json.load(file)
                file.seek(0)
                # appending the deploy point to the content array
                aggregated_json['content'].append(deploy_point)
                # sorting keys to maintain order
                json.dump(aggregated_json, file, indent=2, sort_keys=True)         
                print("Done...")       
            print("#####################################################################")
        else:
            print("#####################################################################")
            print("INFO: This seems to be a failed deployment")
            print("#####################################################################")
