import autofill
import slack.slackbot as slackbot
try:
    autofill.autofill(300, info=True, label=True, image=True, size=5)
except Exception as e: 
    # catch ALL exceptions and send them to the slack bot channel--generally bad practice but useful here.
    slackbot.send_message(f"Error in autofill: {e}", channel="C07SSMMU9E1")
    raise e