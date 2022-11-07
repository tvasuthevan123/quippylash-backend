import logging
import json
import random

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Get prompts by text')

    ## Local Setup
    client = cosmos.cosmos_client.CosmosClient(config.settings['db_URI'], config.settings['db_key'] )

    db_client = client.get_database_client(config.settings['db_id'])

    prompts_container = db_client.get_container_client(config.settings['prompts_container'])

    ## Cloud Setup
    # client = cosmos.cosmos_client.CosmosClient(os.environ['db_URI'], os.environ['db_key'] )

    # db_client = client.get_database_client(os.environ['db_id'])

    # players_container = db_client.get_container_client(os.environ['players_container'])

    requested = req.get_json()
            
    try:
        if(requested['word']!=""):
            user_prompts = list(prompts_container.query_items(
                query='SELECT c.id, c.text, c.username FROM c WHERE RegexMatch(c.text, @regex, @case)=true',
                parameters=[
                    {'name':'@regex',  'value':"(?<![^\\W_])"+ requested['word'] +"(?![^\\W_])"},
                    {'name':'@case', 'value': ('i', '')[requested['exact']]}
                ],
                enable_cross_partition_query=True
            ))
            return func.HttpResponse(body=json.dumps(user_prompts), status_code = 200)
        else:
            all_prompts = list(map(
            lambda x: {
                'id': x['id'], 
                'username': x['username'], 
                'text': x['text']
            },
            prompts_container.read_all_items()))
            return func.HttpResponse(body=json.dumps(all_prompts), status_code=200)
    except exceptions.CosmosHttpResponseError:
        return func.HttpResponse(body=json.dumps([]),
            status_code = 500)
