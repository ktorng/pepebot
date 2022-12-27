from django.conf import settings

import openai


class OpenAIImageClient:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.client = openai.Image

    def generate_image(self, description: str) -> str:
        """
        Parameters:
        description (str): Prompt to feed DALL-E for generating the image

        Returns:
        str: URL of generated image
        """
        response = openai.Image.create(
            prompt=description,
            n=1,
            size="256x256",
        )

        return response["data"][0]["url"]
