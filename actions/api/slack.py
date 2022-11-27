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
            response_msg = ":wave:, Hello <@%s>" % user
            self.client.chat_postMessage(channel=channel, text=response_msg)
