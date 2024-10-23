import requests
import json
# channel ID of the eln_bot channel, can be found by clicking "view channel details"
DEFAULT_CHANNEL: str = 'C0784B6DH45'
BOT_TOKEN: str = ""
with open('slack/slack_bot_token') as file:
    BOT_TOKEN = file.read()

# headers and authentication token
headers: dict = {
    'Authorization' : 'Bearer ' + BOT_TOKEN,
    'Content-Type': 'application/json'
}

json_data: dict = { #initialize the json data
    'channel' : '',
    'text' : ''
}
# Very simple bot. Sends a message in its designated channel when called. 
def send_message(message: str, channel: str = DEFAULT_CHANNEL):
    json_data['text'] = message # set the text field to the given message
    json_data['channel'] = channel # set the channel field to the given channel, default channel for this bot is eln_bot
    response = requests.post('https://slack.com/api/chat.postMessage', headers=headers, json=json_data)