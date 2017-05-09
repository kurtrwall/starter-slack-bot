import os
import time
from slackclient import SlackClient
from bot_commands import handle_command

# starterbot's ID as an environment variable
BOT_ID = os.environ.get('BOT_ID')
BOT_CHANNEL = os.environ.get('BOT_CHANNEL')

# constants
AT_BOT = '<@' + BOT_ID + '>:'

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def is_bot_channel(output):
    return output and 'channel' in output and BOT_CHANNEL in output['channel']


def parse_slack_output(slack_rtm_output):
    '''
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    '''
    output_list = slack_rtm_output

    if output_list and len(output_list) > 0:
        for output in output_list:

            if output and 'user' in output and output['user'] == BOT_ID:
                return None, None

            if output and 'text' in output and output['text']:
                if output['text'].startswith(AT_BOT):
                    # return text after the @ mention, whitespace removed
                    return output['text'].split(AT_BOT)[1].strip().lower(), output['channel']

                elif output['text'].startswith(AT_BOT[:-1]):
                    # return text after the @ mention (with no colon), whitespace removed
                    return output['text'].split(AT_BOT[:-1])[1].strip().lower(), output['channel']

                elif is_bot_channel(output) and output['text'].strip().lower():
                    # return text if talking directly to bot, whitespace removed
                    return output['text'].strip().lower(), output['channel']

    return None, None


if __name__ == '__main__':
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print('Bot connected and running!')
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                response = handle_command(command, channel)
                slack_client.api_call('chat.postMessage', channel=channel,
                                      text=response, as_user=True)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print('Connection failed. Invalid Slack token or bot ID?')

