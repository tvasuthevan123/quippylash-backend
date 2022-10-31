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

    submitted = req.get_json()

    if len(submitted['username']) > 16 or len(submitted['username']) < 4:
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "user does not exist"}),
            status_code = 400)

    if ('add_to_games_played' in submitted.keys() and submitted['add_to_games_played']<=0) or ('add_to_score' in submitted.keys() and submitted['add_to_score']<=0):
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "Value to add is <=0"}),
            status_code = 400)

    submitted['id'] = str(submitted['username'])
    del submitted['username']
    
    try:
        resp = list(players_container.query_items(
            query='SELECT c.id, c.password, c.games_played, c.total_score FROM c WHERE c.id=@id',
            parameters=[
                {'name':'@id',  'value':submitted['id']}
            ],
            enable_cross_partition_query=True
        ))
        
        if len(resp)==1:
            user_details = resp[0]
            if user_details['password'] == submitted['password']:
                if 'add_to_games_played' in submitted.keys():
                    user_details['games_played'] = submitted['add_to_games_played'] + user_details['games_played']
                if 'add_to_score' in submitted.keys():
                    user_details['total_score'] = submitted['add_to_score'] + user_details['total_score']
                players_container.upsert_item(user_details)
                return func.HttpResponse(body=json.dumps({"result" : True, "msg": "OK" }),
                status_code = 200)
            else:
                return func.HttpResponse(body=json.dumps({"result": False , "msg": "wrong password"}),
                status_code = 403)
        else:
            return func.HttpResponse(body=json.dumps({"result": False , "msg": "user does not exist"}),
                status_code = 403)
    except exceptions.CosmosHttpResponseError:
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "Unexpected error, try again"}),
            status_code = 500)
