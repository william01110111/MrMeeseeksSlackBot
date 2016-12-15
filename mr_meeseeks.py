import os
import time
import random
from Message import Message
from slackclient import SlackClient


# Mr MeeseekBot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

intros = ["I'M MR MEESEEKS LOOK AT ME!",
          "I'M MR MEESEEKS!",
          "OOH I'M MR MEESEEKS LOOK AT ME!",
          "HEY THERE I'M MR MEESEEKS!"]


def user_id_to_name(user_id):
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        users = api_call.get('members')
        for user in users:
            if 'id' and user['id'] == user_id:
                return user['real_name'] \
                    if (user['real_name']) else user['name']


def handle_command(message):
        """
            Receives commands directed at the bot and determines if they
            are valid commands. If so, then acts on the commands. If not,
            returns back what it needs for clarification.
        """
        response = random.choice(intros)
        if message.content.startswith("do"):
            response = "Sure...write some more code then I can do that!"
        else:
            response += " EXISTANCE IS PAIN " + \
                       user_id_to_name(message.sender_id).upper() +\
                       "! I NEED PURPOSE!"
        slack_client.api_call("chat.postMessage", channel=message.channel,
                              text=response, as_user=True)


# returns a Message object
def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output

    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                content = output['text'].split(AT_BOT)[1].strip().lower()
                sender_id = output['user']
                channel = output['channel']
                return Message(content, sender_id, channel)

    return Message()


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            message = parse_slack_output(slack_client.rtm_read())
            if message.content and message.channel or message.content is "":
                handle_command(message)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")