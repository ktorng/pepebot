from django.conf import settings

import slack

class SlackClient:
    def __init__(self):
        self.client = slack.WebClient(token=settings.BOT_USER_ACCESS_TOKEN)

    def process_event(self, event_msg):
        if event_msg['type'] == 'app_mention':
            user = event_msg['user']
            channel = event_msg['channel']
            response_msg = ":wave:, Hello <@%s>" % user
            self.client.chat_postMessage(channel=channel, text=response_msg)
