from icalevents.icalevents import events as icalevents
import yaml as yml
import dhooks


class WebCalendar:
    def __init__(self, name, calendar_url, webhook_url, webhook_options = None, **kwargs):
        self.name = name
        self.url = calendar_url.replace('webcal://', 'https://')
        self.webhook = dhooks.Webhook(webhook_url)
        if webhook_options is None:
            webhook_options = {}
        self.webhook_options = webhook_options
        self.options = kwargs

    @staticmethod
    def from_dict(d):
        return WebCalendar(**d)
    
    @property
    def events(self):
        pass


if __name__ == '__main__':
    with open('config.yml', 'r') as f:
        config = yml.safe_load(f)

    for v in config.get('calendars', {}).values():
        cal = WebCalendar.from_dict(v)

    events = icalevents(url=cal.url)
    event = events[0]
    print(dir(event))
    print(event.description, event.time_left)