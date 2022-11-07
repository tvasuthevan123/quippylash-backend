import logging
import json

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Update player')

    ## Local Setup
    client = cosmos.cosmos_client.CosmosClient(config.settings['db_URI'], config.settings['db_key'] )

    db_client = client.get_database_client(config.settings['db_id'])

    players_container = db_client.get_container_client(config.settings['players_container'])

    ## Cloud Setup
    # client = cosmos.cosmos_client.CosmosClient(os.environ['db_URI'], os.environ['db_key'] )

    # db_client = client.get_database_client(os.environ['db_id'])

    # players_container = db_client.get_container_client(os.environ['players_container'])

    top_parameter = req.get_json()['top']

    if top_parameter <= 0:
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "user does not exist"}),
            status_code = 400)
    
    try:
        all_users = list(players_container.query_items(
            query='SELECT c.id as username, c.games_played, c.total_score FROM c',
            enable_cross_partition_query=True
        ))
        
        all_users.sort(key=lambda x: (-x.get('total_score', -1), x.get('username', None)))

        return func.HttpResponse(body=json.dumps(all_users[0:top_parameter]),
            status_code = 200)
    except exceptions.CosmosHttpResponseError:
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "Unexpected error, try again"}),
            status_code = 500)
