from django.conf import settings

import slack
import logging
import json

from actions.api.frankerfacez import FrankerfacezClient
from actions.utils.slack import (
    get_app_mention_text,
    get_image_block,
    get_button_element,
    get_action_block,
)

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

            # get first emoji result
            emotes = self.frankerfacez.get_emotes({"q": text})
            results = emotes.get("emoticons", [])
            first_result = results[0] if results else None

            blocks = []
            if first_result:
                emoji_url = first_result["urls"]["4"]
                emoji_name = first_result["name"]
                json_value = json.dumps(
                    {
                        "url": emoji_url,
                        "name": emoji_name,
                    }
                )
                add_button = get_button_element(
                    text="Add emoji", action_id="add_emoji", value=json_value
                )

                blocks.append(get_action_block(elements=[add_button]))
                blocks.append(get_image_block(image_url=emoji_url, alt_text=emoji_name))

            self.client.chat_postMessage(channel=channel, blocks=blocks)

    def process_message_action(self, payload):
        logger.info("Received message_action action: %s", payload["actions"])

    def handle_unknown_message(self, channel):
        self.client.chat_postMessage(
            channel=channel,
            text="I did not understand your request. Please try something else.",
        )
