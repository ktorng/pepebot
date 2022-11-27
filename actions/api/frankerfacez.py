import requests
import logging

logger = logging.getLogger(__name__)

BASE_URL = 'https://api.frankerfacez.com/v1'

class FrankerfacezClient:
    def __init__(self):
        pass

    def get_emotes(param_overrides):
        logger.info('Getting frankerfacez emotes for: %s', param_overrides)
        params = {
            'sensitive': 'false',
            'high_dpi': 'off',
            **param_overrides,
        }
        r = requests.get(BASE_URL + '/emotes', params=params)
        response = r.json()
        logger.info('Received frankerfaces get emote response: %s', response)
