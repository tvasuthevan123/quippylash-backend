import logging
import json

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Edit prompt')

    ## Local Setup
    client = cosmos.cosmos_client.CosmosClient(config.settings['db_URI'], config.settings['db_key'] )

    db_client = client.get_database_client(config.settings['db_id'])

    players_container = db_client.get_container_client(config.settings['players_container'])
    prompts_container = db_client.get_container_client(config.settings['prompts_container'])

    ## Cloud Setup
    # client = cosmos.cosmos_client.CosmosClient(os.environ['db_URI'], os.environ['db_key'] )

    # db_client = client.get_database_client(os.environ['db_id'])

    # players_container = db_client.get_container_client(os.environ['players_container'])

    prompt_info = req.get_json()

    if len(prompt_info['password']) > 24 or len(prompt_info['password']) < 8 or len(prompt_info['username']) > 16 or len(prompt_info['username']) < 4:
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "bad username or password"}),
            status_code = 400) 

    try:
        resp = list(players_container.query_items(
            query='SELECT c.password FROM c WHERE c.id=@id',
            parameters=[
                {'name':'@id',  'value':prompt_info['username']}
            ],
            enable_cross_partition_query=True
        ))

        if len(resp)==1 and resp[0]['password'] == prompt_info['password']:
            existing_prompt = list(prompts_container.query_items(
                query='SELECT * FROM c WHERE c.id=@id',
                parameters=[
                    {'name':'@id',  'value':str(prompt_info['id'])}
                ],
                enable_cross_partition_query=True
            ))

            if len(existing_prompt) == 0:
                return func.HttpResponse(body=json.dumps({"result" : False, "msg": "prompt id does not exist" }),
                status_code = 404)
            elif len(existing_prompt) != 0 and existing_prompt[0]['username'] != prompt_info['username']:
                return func.HttpResponse(body=json.dumps({"result" : False, "msg": "access denied" }),
                status_code = 403)
            else:
                prompts_container.delete_item(item=str(prompt_info['id']), partition_key=str(prompt_info['id']))
                return func.HttpResponse(body=json.dumps({"result" : True, "msg": "OK" }),
                status_code = 200)
        else:
            return func.HttpResponse(body=json.dumps({"result": False , "msg": "bad username or password"}),
                status_code = 403)
    except Exception as e:
        repr(e)
