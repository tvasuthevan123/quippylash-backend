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

    if len(prompt_info['text']) > 100 or len(prompt_info['text']) < 20:
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "prompt length is <20 or >100 characters"}),
            status_code = 400)

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
            existing_prompt_text = list(prompts_container.query_items(
                query='SELECT * FROM c WHERE c.username=@username AND c.text=@text AND c.id!=@id',
                parameters=[
                    {'name':'@username',  'value':prompt_info['username']},
                    {'name':'@text',  'value':prompt_info['text']},
                    {'name':'@id',  'value':str(prompt_info['id'])}
                ],
                enable_cross_partition_query=True
            ))

            existing_prompt_id = list(prompts_container.query_items(
                query='SELECT * FROM c WHERE c.username=@username AND c.id=@id',
                parameters=[
                    {'name':'@username',  'value':prompt_info['username']},
                    {'name':'@id',  'value':str(prompt_info['id'])}
                ],
                enable_cross_partition_query=True
            ))

            if len(existing_prompt_id) == 0:
                return func.HttpResponse(body=json.dumps({"result" : False, "msg": "prompt id does not exist" }),
                status_code = 200)
            elif len(existing_prompt_text) != 0:
                return func.HttpResponse(body=json.dumps({"result" : False, "msg": "This user already has a prompt with the same text" }),
                status_code = 200)
            else:
                prompt_info['id'] = str(prompt_info['id'])
                del prompt_info['password']
                prompts_container.upsert_item(prompt_info)
                return func.HttpResponse(body=json.dumps({"result" : True, "msg": "OK" }),
                status_code = 409)
        else:
            return func.HttpResponse(body=json.dumps({"result": False , "msg": "bad username or password"}),
                status_code = 403)
    except Exception as e:
        repr(e)
