def get_app_mention_text(event_msg):
    try:
        elements = event_msg["blocks"][0]["elements"][0]["elements"]
        print(elements)
        for i, el in enumerate(elements):
            if el["type"] == "user":
                next_el = elements[i + 1]
                if next_el["type"] == "text":
                    return next_el["text"].strip()
    except:
        return None


def get_image_block(image_url, alt_text):
    return {
        "type": "image",
        "image_url": image_url,
        "alt_text": "alt_text",
    }


def get_action_block(elements):
    return {
        "type": "actions",
        "elements": elements,
    }


def get_button_element(text, action_id, value):
    return {
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": text,
        },
        "value": value,
        "action_id": action_id,
    }
