from icalevents.icalevents import events as icalevents
from datetime import timedelta
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
        fix_apple = self.options.get('icloud', False)
        return icalevents(
            self.url, 
            fix_apple=fix_apple
        )
    
    def format_timedelta(timedelta):
        fields = [
            'days',
            'hours',
            'minutes'
        ]

        return ', '.join(['{} {}'.format(
            getattr(timedelta, field),
            field
        ) for field in fields])

    def format_event_content(self, event):
        context = {
            'calendar': self.name,
            'title': event.summary,
            'description': event.description,
            'time_until': WebCalendar.format_timedelta(event.time_until())
        }
        with open('webhook-template.md', 'r') as f:
            read = f.read()
        for field, content in context.items():
            read = read.replace('{{ %s }}' % field, content)
        return read
    
    def send(self, event):
        self.webhook.send(
            self.format_event_content(event),
            **self.webhook_options
        )


if __name__ == '__main__':
    with open('config.yml', 'r') as f:
        config = yml.safe_load(f)
    timedeltas = [timedelta(**delta) for delta in config.get('alert_time_remaining', [])]
    
    for v in config.get('calendars', {}).values():
        cal = WebCalendar.from_dict(v)
        for event in cal.events:
            pass