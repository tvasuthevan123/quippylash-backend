import azure.cosmos as cosmos
import config
import os

def getContainer(name, local=True):
    dbConfig = config.settings if local==True else os.environ

    client = cosmos.cosmos_client.CosmosClient(dbConfig['db_URI'], dbConfig['db_key'] )

    db_client = client.get_database_client(dbConfig['db_id'])

    return db_client.get_container_client(dbConfig[name])