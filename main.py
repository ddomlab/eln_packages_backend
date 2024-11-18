import autofill
import slack.slackbot as slackbot
try:
    autofill.autofill(300, info=True, label=True, image=True, size=5)
except Exception as e:
    slackbot.send_message(f"Error in autofill: {e}")
    raise e