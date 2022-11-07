import logging
import json

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import connector

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Login player')

    players_container = connector.getContainer('players_container', local=True)

    submitted = req.get_json()

    if len(submitted['username']) > 16 or len(submitted['username']) < 4 or len(submitted['password']) > 24 or len(submitted['password']) < 8:
        return func.HttpResponse(body=json.dumps({"result": False , "msg": "Username or password incorrect"}),
            status_code = 403)

    try:
        resp = players_container.read_item(item=submitted['username'], partition_key=submitted['username'])

        if resp['password'] == submitted['password']:
            return func.HttpResponse(body=json.dumps({"result" : True, "msg": "OK" }),
                status_code = 200)
        else:
            return func.HttpResponse(body=json.dumps({"result": False , "msg": "Username or password incorrect"}),
                status_code = 403)
    except Exception as e:
        return func.HttpResponse(body=json.dumps({"result": False , "msg": "Username or password incorrect"}),
                status_code = 403)
