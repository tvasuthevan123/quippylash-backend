import logging
import json
import uuid


import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import connector

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Adding player to cloud DB')

    prompts_container = connector.getContainer('prompts_container', local=True)
    players_container = connector.getContainer('players_container', local=True)

    prompt_info = req.get_json()

    if len(prompt_info['text']) > 100 or len(prompt_info['text']) < 20:
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "prompt length is <20 or > 100 characters"}),
            status_code = 400)

    if len(prompt_info['password']) > 24 or len(prompt_info['password']) < 8 or len(prompt_info['username']) > 16 or len(prompt_info['username']) < 4:
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "bad username or password"}),
            status_code = 400) 



    try:
        resp = players_container.read_item(item=prompt_info['username'], partition_key=prompt_info['username'])

        if resp['password'] == prompt_info['password']:
            existing_prompt = list(prompts_container.query_items(
                query='SELECT * FROM c WHERE c.username=@username AND c.text=@text',
                parameters=[
                    {'name':'@username',  'value':prompt_info['username']},
                    {'name':'@text',  'value':prompt_info['text']}
                ],
                enable_cross_partition_query=True
            ))  
            if len(existing_prompt) == 0:
                del prompt_info['password']
                prompt_info['id'] = str(hash(uuid.uuid4()))
                prompts_container.create_item(prompt_info)
                return func.HttpResponse(body=json.dumps({"result" : True, "msg": "OK" }),
                status_code = 200)
            else:
                return func.HttpResponse(body=json.dumps({"result" : False, "msg": "This user already has a prompt with the same text" }),
                status_code = 409)
        else:
            return func.HttpResponse(body=json.dumps({"result": False , "msg": "bad username or password"}),
                status_code = 403)
    except Exception as e:
        return func.HttpResponse(body=json.dumps({"result": False , "msg": "bad username or password"}),
                status_code = 403)
