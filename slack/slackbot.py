import requests
import json
# headers and authentication token
headers = {
    'Authorization' : json.loads(open('/slack/token.json').read())['slack_bot_token'],
    'Content-Type': 'application/json'
}
# channel id of the channel where the bot will post
json_data = {
    'channel' : 'C07SSMMU9E1',
    'text' : 'hello world'
}

response = requests.post('https://slack.com/api/chat.postMessage', headers=headers, json=json_data)