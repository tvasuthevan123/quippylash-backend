import logging
import json
import random

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import connector

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Get prompts')

    prompts_container = connector.getContainer('prompts_container', local=True)

    requested = req.get_json()
            
    try:
        if 'prompts' in requested.keys():
            all_prompts = list(map(
                lambda x: {
                    'id': x['id'], 
                    'username': x['username'], 
                    'text': x['text']
                },
                prompts_container.read_all_items()))
            n = requested['prompts'] 
            if n >= len(all_prompts):
                return func.HttpResponse(body=json.dumps(all_prompts),
                    status_code = 200)
            elif n > 0:
                return_prompts = []
                while n > 0:
                    return_prompts.append(all_prompts.pop(random.randint(0, len(all_prompts)-1)))
                    n=n-1
                return func.HttpResponse(body=json.dumps(return_prompts),
                    status_code = 200)
            else:
                raise Exception('Required info unavailable')
        elif 'players' in requested.keys():
            usernames = requested['players']
            returned_prompts = []
            for username in usernames:
                user_prompts = list(prompts_container.query_items(
                    query='SELECT c.id, c.username, c.text FROM c WHERE c.username=@username',
                    parameters=[
                        {'name':'@username',  'value':username}
                    ],
                    enable_cross_partition_query=True
                ))
                returned_prompts.extend(user_prompts)
            return func.HttpResponse(body=json.dumps(returned_prompts),
                status_code = 200)
        else:
            return func.HttpResponse(body=json.dumps([]),
                status_code = 200)
    except exceptions.CosmosHttpResponseError:
        return func.HttpResponse(body=json.dumps([]),
            status_code = 500)
    except Exception as e:
        logging.info(repr(e))
        return func.HttpResponse(body=json.dumps([]),
            status_code = 500)
