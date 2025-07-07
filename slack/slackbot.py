import requests
from pathlib import Path

# channel ID of the eln_bot channel, can be found by clicking "view channel details"
DEFAULT_CHANNEL: str = "C093HPVRLKD"
BOT_TOKEN: str = ""
current_dir: Path = Path(__file__).parent
BOT_TOKEN_PATH: str = str(current_dir / "slack_bot_token")
with open(BOT_TOKEN_PATH) as file:
    BOT_TOKEN = file.read().rstrip()

# headers and authentication token
headers: dict = {
    "Authorization": "Bearer " + BOT_TOKEN,
    "Content-Type": "application/json",
}

json_data: dict = {  # initialize the json data
    "channel": "",
    "text": "",
}


# Very simple bot. Sends a message in its designated channel when called.
def send_message(message: str, channel: str = DEFAULT_CHANNEL):
    json_data["text"] = message  # set the text field to the given message
    json_data["channel"] = (
        channel  # set the channel field to the given channel, default channel for this bot is eln_bot
    )
    requests.post(
        "https://slack.com/api/chat.postMessage", headers=headers, json=json_data
    )

if __name__ == "__main__":
    # Test the bot by sending a message to the default channel
    send_message("Hello from the ELN bot! This is a test message.")
    print("Message sent successfully.")