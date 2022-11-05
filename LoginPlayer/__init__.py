import logging
import json

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Login player')

    ## Local Setup
    client = cosmos.cosmos_client.CosmosClient(config.settings['db_URI'], config.settings['db_key'] )

    db_client = client.get_database_client(config.settings['db_id'])

    players_container = db_client.get_container_client(config.settings['players_container'])

    ## Cloud Setup
    # client = cosmos.cosmos_client.CosmosClient(os.environ['db_URI'], os.environ['db_key'] )

    # db_client = client.get_database_client(os.environ['db_id'])

    # players_container = db_client.get_container_client(os.environ['players_container'])

    submitted = req.get_json()

    if len(submitted['username']) > 16 or len(submitted['username']) < 4 or len(submitted['password']) > 24 or len(submitted['password']) < 8:
        return func.HttpResponse(body=json.dumps({"result": False , "msg": "Username or password incorrect"}),
            status_code = 403)

    try:
        resp = players_container.read_item(item=submitted['username'], partition_key=submitted['username'])

        if resp['password'] == submitted['password']:
            return func.HttpResponse(body=json.dumps({"result" : True, "msg": "OK" }),
                status_code = 200)
        else:
            return func.HttpResponse(body=json.dumps({"result": False , "msg": "Username or password incorrect"}),
                status_code = 403)
    except Exception as e:
        return func.HttpResponse(body=json.dumps({"result": False , "msg": "Username or password incorrect"}),
                status_code = 403)
