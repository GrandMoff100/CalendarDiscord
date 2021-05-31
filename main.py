from icalevents.icalevents import events as icalevents
from datetime import timedelta, datetime
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
    
    def format_timedelta(delta):
        hours = (delta.seconds - delta.seconds % 3600)
        fields = {
            'Days': delta.days,
            'Hours': hours // 3600,
            'Minutes': (delta.seconds - hours - delta.seconds % 60) // 60
        }
        return ', '.join(['{} {}'.format(field, data) for field, data in fields.items() if data > 0])
        

    def format_event_content(self, event):
        context = {
            'calendar': self.name,
            'title': event.summary,
            'description': event.description,
            'time_until': WebCalendar.format_timedelta(event.time_left())
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
    
    alert_ats = [timedelta(**delta) for delta in config.get('alert_time_remaining', [])]
    
    for v in config.get('calendars', []):
        cal = WebCalendar.from_dict(v)
        for event in cal.events:
            #for alert_at in alert_ats:
            #    now = datetime.now()
            #    if now + timedelta(minutes=6) >= now + alert_at >= now:
            cal.send(event)