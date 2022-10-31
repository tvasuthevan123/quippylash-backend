import logging
import json 

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Adding new user to db (RegisterPlayer)')

    ## Local Setup
    client = cosmos.cosmos_client.CosmosClient(config.settings['db_URI'], config.settings['db_key'] )

    db_client = client.get_database_client(config.settings['db_id'])

    players_container = db_client.get_container_client(config.settings['players_container'])

    username = req.params.get('username')
    pwd = req.params.get('pwd')



    return func.HttpResponse(
        body=json.dumps({}),
        status_code=200
    )
