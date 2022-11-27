def get_app_mention_text(event_msg):
    if not event_msg or elements not in event_msg:
        return None
    elements = event_msg['elements']

    for i, el in enumerate(elements):
        if el['type'] == 'user':
            next_el = elements[i+1]
            if next_el['type'] == 'text':
                return next_el['text'].strip()
