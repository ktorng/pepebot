import re
import threading
from django.conf import settings
from enum import Enum

import slack
import logging
import json

from actions.api.frankerfacez import FrankerfacezClient
from actions.api.openai_image import OpenAIImageClient
from actions.utils.slack import (
    get_app_mention_text,
    get_image_block,
    get_button_element,
    get_action_block,
    get_section_with_image,
)

logger = logging.getLogger(__name__)


class MessageActionType(Enum):
    add_emoji = "add_emoji"
    remove_emoji = "remove_emoji"


class SlackClient:
    def __init__(self):
        self.client = slack.WebClient(token=settings.BOT_USER_ACCESS_TOKEN)
        self.user_client = slack.WebClient(token=settings.SLACK_USER_ACCESS_TOKEN)

    def process_event(self, event_msg):
        if event_msg["type"] == "app_mention":
            logger.info("Received app mention: %s", event_msg)
            channel = event_msg["channel"]

            text = get_app_mention_text(event_msg)
            if not text:
                return self.handle_unknown_message(channel)

            logger.info("Received app mention text: '%s'", text)

            r = re.compile("^generate (.*)", re.IGNORECASE)
            match = re.match(r, text)

            if match:
                description = match.groups()[0]
                # start new thread for image processing
                x = threading.Thread(
                    target=self.generate_openai_image, args=[channel, description]
                )
                x.start()
            else:
                self.handle_unknown_message(channel)

    def generate_openai_image(self, channel, description):
        openai_image_client = OpenAIImageClient()

        self.client.chat_postMessage(
            channel=channel,
            text="Generating image... please wait (can take ~30s)",
        )

        url = openai_image_client.generate_image(description)

        if url:
            blocks = []
            blocks.append(
                get_section_with_image(
                    text="Here's a generated image for _{0}_".format(description),
                    text_type="mrkdwn",
                    image_url=url,
                    image_alt_text=description,
                )
            )
            self.client.chat_postMessage(channel=channel, blocks=blocks)
        else:
            self.handle_unknown_error(channel)

    def search_frankerfacez(self, channel, text):
        # get first emoji result
        frankerfacez = FrankerfacezClient()
        emotes = frankerfacez.get_emotes({"q": text})
        results = emotes.get("emoticons", [])
        first_result = results[0] if results else None

        blocks = []
        if first_result:
            emoji_url = first_result["urls"]["2"]
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
            remove_button = get_button_element(
                text="Remove emoji", action_id="remove_emoji", value=json_value
            )

            blocks.append(get_action_block(elements=[add_button, remove_button]))
            blocks.append(get_image_block(image_url=emoji_url, alt_text=emoji_name))

        self.client.chat_postMessage(channel=channel, blocks=blocks)

    def process_message_action(self, payload):
        logger.info("Received message_action action payload: %s", payload)

        action = payload["actions"][0]
        channel = payload["container"]["channel_id"]
        action_id = MessageActionType[action["action_id"]]
        value = json.loads(action["value"])
        print(action_id, MessageActionType.add_emoji)

        if action_id is MessageActionType.add_emoji:
            name = value["name"]
            url = value["url"]

            return self.add_emoji(channel, name, url)
        if action_id is MessageActionType.remove_emoji:
            name = value["name"]

            return self.remove_emoji(channel, name)

    def handle_unknown_message(self, channel):
        self.client.chat_postMessage(
            channel=channel,
            text="I did not understand your request. Please try something else.",
        )

    def handle_unknown_error(self, channel):
        self.client.chat_postMessage(
            channel=channel,
            text="Something went wrong. Please try again later.",
        )

    def add_emoji(self, channel, name, url):
        """
        Add a custom reaction to this workspace
        """
        logger.info("Adding emoji: %s", name)
        cookies = json.dumps(
            {
                "d": "xoxd-OpwRR+FBa3R5AYpeJe55FpHIcCihrgyWg81UXurb/q0fi9cz38aJA+NXVFpAWMWZn7u5d9O2Lg2SO7JR0D1Iep+e4d5aT/GuWQh4aak8t/ffbe3WPwbhZfNVirAPhJxEUASJcbwORhT4xggXqBzs1qK79DfQFDMRvZxBeavAi6Ff4W3cZAu5kw=="
            }
        )
        response = self.user_client.api_call(
            api_method="emoji.add",
            json=json.dumps({"name": name, "url": url}),
            headers={
                "Cookie": cookies,
            },
        )
        logger.info("[API][Response] Add emoji: %s", name)
        assert response["ok"]
        self.client.chat_postMessage(
            channel=channel,
            text="Emoji `{name}` has been added. :{name}:".format(name=name),
        )

    def remove_emoji(self, channel, name):
        """
        Remove a custom reaction from this workspace
        """
        try:
            logger.info("Removing emoji: %s", name)
            response = self.client.api_call(
                api_method="admin.emoji.remove",
                json=json.dumps({"name": name}),
            )
            assert response["ok"]
            self.client.chat_postMessage(
                channel=channel,
                text="Emoji `{name}` has been removed.".format(name=name),
            )
        except:
            self.handle_unknown_error(channel)
