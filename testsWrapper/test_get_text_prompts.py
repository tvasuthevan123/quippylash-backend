import unittest
import json
import requests
import wrapper 

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config
#Important for the import name to match the case of the Function folder
from LoginPlayer import main

# Local setup
client = cosmos.cosmos_client.CosmosClient(config.settings['db_URI'], config.settings['db_key'] )

db_client = client.get_database_client(config.settings['db_id'])

prompts_container = db_client.get_container_client(config.settings['prompts_container'])

request_url = config.settings['cloud_URI'] + 'prompts/getText/'

class TestFunction(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls) -> None:
        try:
            prompts_container.create_item({"id": "0" , "text" : "What Program you would never code in JavaScript", "username": "py_luis"})
            prompts_container.create_item({"id": "1" , "text" : "What is the funniest programming language?", "username": "js_oli"})
            prompts_container.create_item({"id": "2" , "text" : "How many lines your shorter program has?", "username": "perl_les"})
        except Exception as e:
            # print(repr(e))
            pass

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            prompts_container.delete_item(item="0", partition_key="0")
            prompts_container.delete_item(item="1", partition_key="1")
            prompts_container.delete_item(item="2", partition_key="2")
        except Exception as e:
            # print(repr(e))
            pass

    def test_get_text_prompts__case_insensitive(self):
        payload ={
            "word": "program",
            "exact": True
        }

        # resp = requests.post(
        #     # Request URL (Use config)
        #     request_url,
        #     headers={'x-functions-key' : config.settings['APP_KEY']},
        #     json=payload
        # )

        get_response = list(wrapper.prompts_getText(payload, local=True))
        expected_response = [{"id": "2" , "text" : "How many lines your shorter program has?", "username": "perl_les"}]

        self.assertEqual(expected_response, get_response)

        payload ={
            "word": "Program",
            "exact": True
        }

        # resp = requests.post(
        #     # Request URL (Use config)
        #     request_url,
        #     headers={'x-functions-key' : config.settings['APP_KEY']},
        #     json=payload
        # )

        get_response = wrapper.prompts_getText(payload, local=True)
        expected_response = [{"id": "0" , "text" : "What Program you would never code in JavaScript", "username": "py_luis"}]

        self.assertEqual(expected_response, get_response)

        payload ={
            "word": "language",
            "exact": True
        }

        # resp = requests.post(
        #     # Request URL (Use config)
        #     request_url,
        #     headers={'x-functions-key' : config.settings['APP_KEY']},
        #     json=payload
        # )

        get_response = list(wrapper.prompts_getText(payload, local=True))
        expected_response = [{"id": "1" , "text" : "What is the funniest programming language?", "username": "js_oli"}]

        self.assertEqual(expected_response, get_response)



    def test_get_text_prompts__case_sensitive(self):
        payload ={
            "word": "program",
            "exact": False
        }

        # resp = requests.post(
        #     # Request URL (Use config)
        #     request_url,
        #     headers={'x-functions-key' : config.settings['APP_KEY']},
        #     json=payload
        # )

        get_response = list(wrapper.prompts_getText(payload, local=True))
        expected_response = [
            {"id": "0" , "text" : "What Program you would never code in JavaScript", "username": "py_luis"},
            {"id": "2" , "text" : "How many lines your shorter program has?", "username": "perl_les"}
        ]

        self.assertEqual(expected_response, get_response)

        payload ={
            "word": "progrAmMIng",
            "exact": False
        }

        # resp = requests.post(
        #     # Request URL (Use config)
        #     request_url,
        #     headers={'x-functions-key' : config.settings['APP_KEY']},
        #     json=payload
        # )

        get_response = list(wrapper.prompts_getText(payload, local=True))
        expected_response = [
            {"id": "1" , "text" : "What is the funniest programming language?", "username": "js_oli"}
        ]

        self.assertEqual(expected_response, get_response)

