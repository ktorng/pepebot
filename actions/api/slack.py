from django.conf import settings

import slack
import logging

from actions.api.frankerfacez import FrankerfacezClient
from actions.utils.slack import get_app_mention_text, get_image_block

logger = logging.getLogger(__name__)


class SlackClient:
    def __init__(self):
        self.client = slack.WebClient(token=settings.BOT_USER_ACCESS_TOKEN)
        self.frankerfacez = FrankerfacezClient()

    def process_event(self, event_msg):
        if event_msg["type"] == "app_mention":
            logger.info("Received app mention: %s", event_msg)
            user = event_msg["user"]
            channel = event_msg["channel"]

            text = get_app_mention_text(event_msg)
            if not text:
                return self.handle_unknown_message(channel)

            logger.info("Received app mention text: %s", text)

            emotes = self.frankerfacez.get_emotes({"q": text})
            results = emotes.get("emoticons", [])
            first_result = results[0] if results else None

            blocks = [
                get_image_block(first_result["urls"]["4"], first_result["name"])
                if first_result
                else None,
            ]
            self.client.chat_postMessage(channel=channel, blocks=blocks)

    def handle_unknown_message(self, channel):
        self.client.chat_postMessage(
            channel=channel,
            text="I did not understand your request. Please try something else.",
        )
