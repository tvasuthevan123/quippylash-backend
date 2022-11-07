import logging
import json
import random

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import connector

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Get prompts by text')

    prompts_container = connector.getContainer('prompts_container', local=True)


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
