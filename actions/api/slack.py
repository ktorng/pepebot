from django.conf import settings

import slack
import logging

from actions.api.frankerfacez import FrankerfacezClient
from actions.utils.slack import get_app_mention_text

logger = logging.getLogger(__name__)

class SlackClient:
    def __init__(self):
        self.client = slack.WebClient(token=settings.BOT_USER_ACCESS_TOKEN)
        self.frankerfacez = FrankerfacezClient()

    def process_event(self, event_msg):
        if event_msg['type'] == 'app_mention':
            logger.info('Received app mention: %s', event_msg)
            user = event_msg['user']
            channel = event_msg['channel']

            text = get_app_mention_text(event_msg)
            if not text:
                self.handle_unknown_message(channel)
                return

            logger.info('Received app mention text: %s', text)

            emotes = self.frankerfacez.get_emotes({
                'q': text
            })

            response_msg = ":wave:, Hello <@%s>" % user
            self.client.chat_postMessage(channel=channel, text=response_msg)

    def handle_unknown_message(self, channel):
            self.client.chat_postMessage(channel=channel, text='I did not understand your request. Please try something else.')
