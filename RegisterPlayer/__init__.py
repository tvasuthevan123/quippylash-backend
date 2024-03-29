import logging
import json

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import connector

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Adding player to cloud DB')

    players_container = connector.getContainer('players_container', local=True)

    user_details = req.get_json()

    if len(user_details['username']) > 16 or len(user_details['username']) < 4:
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "Username less than 4 characters or more than 16 characters"}),
            status_code = 400)

    if len(user_details['password']) > 24 or len(user_details['password']) < 8:
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "Password less than 8 characters or more than 24 characters"}),
            status_code = 400)

    user_details['id'] = str(user_details['username'])
    del user_details['username']
    user_details['games_played']=0
    user_details['total_score']=0   



    try:
        players_container.create_item(user_details)
        return func.HttpResponse(body=json.dumps({"result" : True, "msg": "OK" }),
            status_code = 201)
    except exceptions.CosmosHttpResponseError:
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "Username already exists"}),
            status_code = 409)
