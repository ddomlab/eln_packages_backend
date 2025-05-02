import autofill
import slack.slackbot as slackbot
from datetime import date
from check_peroxides import check_all_classes

today = date.today.strftime("%m-%d")
try:
    autofill.autofill(300, info=True, label=True, image=True, size=5)
except Exception as e: 
    # catch ALL exceptions and send them to the slack bot channel--generally bad practice but useful here.
    slackbot.send_message(f"Error in autofill: {e}", channel="C07SSMMU9E1")
    raise e
try:
    if today in ["05-01", "11-01"]:
        check_all_classes()
except Exception as e:
    slackbot.send_message(f"Error in check_peroxides: {e}", channel="C07SSMMU9E1")
    raise e