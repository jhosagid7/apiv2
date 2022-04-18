from typing import Any
from pyparsing import Literal
import pytz
import re
import logging

from datetime import datetime, timedelta
from django.utils import timezone
from breathecode.admissions.models import Cohort, CohortTimeSlot, TimeSlot
from breathecode.utils.datetime_interger import DatetimeInteger

from .models import Organization, Venue, Event, Organizer
from .utils import Eventbrite
from django.db.models import QuerySet

logger = logging.getLogger(__name__)

status_map = {
    'draft': 'DRAFT',
    'live': 'ACTIVE',
    'completed': 'COMPLETED',
    'started': 'ACTIVE',
    'ended': 'ACTIVE',
    'canceled': 'DELETED',
}


def sync_org_venues(org):
    if org.academy is None:
        raise Exception('First you must specify to which academy this organization belongs')

    client = Eventbrite(org.eventbrite_key)
    result = client.get_organization_venues(org.eventbrite_id)

    for data in result['venues']:
        create_or_update_venue(data, org, force_update=True)

    return True


def create_or_update_organizer(data, org, force_update=False):
    if org.academy is None:
        raise Exception('First you must specify to which academy this organization belongs')

    organizer = Organizer.objects.filter(eventbrite_id=data['id']).first()

    try:
        if organizer is None:
            organizer = Organizer(name=data['name'],
                                  description=data['description']['text'],
                                  eventbrite_id=data['id'],
                                  organization=org)
            organizer.save()

        elif force_update == True:
            organizer.name = data['name']
            organizer.description = data['description']['text']
            organizer.save()

    except Exception as e:
        print('Error saving organizer eventbrite_id: ' + str(data['id']) + ' skipping to the next', e)

    return organizer


def create_or_update_venue(data, org, force_update=False):
    if not org.academy:
        logger.error(f'The organization {org} not have a academy assigned')
        return

    venue = Venue.objects.filter(eventbrite_id=data['id'], academy__id=org.academy.id).first()

    if venue and not force_update:
        return

    kwargs = {
        'title': data['name'],
        'street_address': data['address']['address_1'],
        'country': data['address']['country'],
        'city': data['address']['city'],
        'state': data['address']['region'],
        'zip_code': data['address']['postal_code'],
        'latitude': data['latitude'],
        'longitude': data['longitude'],
        'eventbrite_id': data['id'],
        'eventbrite_url': data['resource_uri'],
        'academy': org.academy,
        # 'organization': org,
    }

    try:
        if venue is None:
            Venue(**kwargs).save()

        elif force_update == True:
            for attr in kwargs:
                setattr(venue, attr, kwargs[attr])

            venue.save()

    except:
        logger.error(f'Error saving venue eventbrite_id: {data["id"]} skipping to the next')

    return venue


def export_event_description_to_eventbrite(event: Event) -> None:
    if not event:
        logger.error(f'Event is not being provided')
        return

    if not event.eventbrite_id:
        logger.error(f'Event {event.id} not have the integration with eventbrite')
        return

    if not event.organization:
        logger.error(f'Event {event.id} not have a organization assigned')
        return

    if not event.description:
        logger.warning(f'The event {event.id} not have description yet')
        return

    eventbrite_id = event.eventbrite_id
    client = Eventbrite(event.organization.eventbrite_key)

    payload = {
        'modules': [{
            'type': 'text',
            'data': {
                'body': {
                    'type': 'text',
                    'text': event.description,
                    'alignment': 'left',
                },
            },
        }],
        'publish':
        True,
        'purpose':
        'listing',
    }

    try:
        structured_content = client.get_event_description(eventbrite_id)
        result = client.create_or_update_event_description(eventbrite_id,
                                                           structured_content['page_version_number'], payload)

        if not result['modules']:
            error = 'Could not create event description in eventbrite'
            logger.error(error)

            event.eventbrite_sync_description = error
            event.eventbrite_sync_status = 'ERROR'
            event.save()

        else:
            event.eventbrite_sync_description = timezone.now()
            event.eventbrite_sync_status = 'SYNCHED'
            event.save()

    except Exception as e:
        error = str(e)
        logger.error(error)

        event.eventbrite_sync_description = error
        event.eventbrite_sync_status = 'ERROR'
        event.save()


def export_event_to_eventbrite(event: Event, org: Organization):
    if not org.academy:
        logger.error(f'The organization {org} not have a academy assigned')
        return

    timezone = org.academy.timezone
    client = Eventbrite(org.eventbrite_key)
    now = get_current_iso_string()

    data = {
        'event.name.html': event.title,
        'event.description.html': event.description,
        'event.start.utc': re.sub(r'\+00:00$', 'Z', event.starting_at.isoformat()),
        'event.end.utc': re.sub(r'\+00:00$', 'Z', event.ending_at.isoformat()),
        # 'event.summary': event.excerpt,
        'event.capacity': event.capacity,
        'event.online_event': event.online_event,
        'event.url': event.eventbrite_url,
        'event.currency': event.currency,
    }

    if event.eventbrite_organizer_id:
        data['event.organizer_id'] = event.eventbrite_organizer_id

    if timezone:
        data['event.start.timezone'] = timezone
        data['event.end.timezone'] = timezone

    try:
        if event.eventbrite_id:
            client.update_organization_event(event.eventbrite_id, data)

        else:
            result = client.create_organization_event(org.eventbrite_id, data)
            event.eventbrite_id = str(result['id'])

        event.eventbrite_sync_description = now
        event.eventbrite_sync_status = 'SYNCHED'

        export_event_description_to_eventbrite(event)

    except Exception as e:
        event.eventbrite_sync_description = f'{now} => {e}'
        event.eventbrite_sync_status = 'ERROR'

    event.save()
    return event


def sync_org_events(org):
    if not org.academy:
        logger.error(f'The organization {org} not have a academy assigned')
        return

    client = Eventbrite(org.eventbrite_key)
    result = client.get_organization_events(org.eventbrite_id)

    try:

        for data in result['events']:
            update_or_create_event(data, org)

        org.sync_status = 'PERSISTED'
        org.sync_desc = f"Success with {len(result['events'])} events..."
        org.save()

    except Exception as e:
        if org:
            org.sync_status = 'ERROR'
            org.sync_desc = 'Error: ' + str(e)
            org.save()
        raise e

    events = Event.objects.filter(sync_with_eventbrite=True, eventbrite_sync_status='PENDING')
    for event in events:
        export_event_to_eventbrite(event, org)

    return True


# use for mocking purpose
def get_current_iso_string():
    from django.utils import timezone

    return str(timezone.now())


def update_event_description_from_eventbrite(event: Event) -> None:
    if not event:
        logger.error(f'Event is not being provided')
        return

    if not event.eventbrite_id:
        logger.error(f'Event {event.id} not have the integration with eventbrite')
        return

    if not event.organization:
        logger.error(f'Event {event.id} not have a organization assigned')
        return

    eventbrite_id = event.eventbrite_id
    client = Eventbrite(event.organization.eventbrite_key)

    try:
        data = client.get_event_description(eventbrite_id)
        event.description = data['modules'][0]['data']['body']['text']
        event.eventbrite_sync_description = timezone.now()
        event.eventbrite_sync_status = 'PERSISTED'
        event.save()

    except:
        error = f'The event {eventbrite_id} is coming from eventbrite not have a description'
        logger.warning(error)
        event.eventbrite_sync_description = error
        event.eventbrite_sync_status = 'ERROR'


def update_or_create_event(data, org):
    if data is None:  #skip if no data
        logger.warn('Ignored event')
        return False

    if not org.academy:
        logger.error(f'The organization {org} not have a academy assigned')
        return

    now = get_current_iso_string()

    if data['status'] not in status_map:
        raise Exception('Uknown eventbrite status ' + data['status'])

    event = Event.objects.filter(eventbrite_id=data['id'], organization__id=org.id).first()
    try:
        venue = None
        if 'venue' in data and data['venue'] is not None:
            venue = create_or_update_venue(data['venue'], org)
        organizer = None
        if 'organizer' in data and data['organizer'] is not None:
            organizer = create_or_update_organizer(data['organizer'], org, force_update=True)
        else:
            print('Event without organizer', data)

        kwargs = {
            'title': data['name']['text'],
            'description': data['description']['text'],
            'excerpt': data['description']['text'],
            'starting_at': data['start']['utc'],
            'ending_at': data['end']['utc'],
            'capacity': data['capacity'],
            'online_event': data['online_event'],
            'eventbrite_id': data['id'],
            'eventbrite_url': data['url'],
            'status': status_map[data['status']],
            'eventbrite_status': data['status'],
            'currency': data['currency'],
            'organization': org,
            # organizer: organizer,
            'venue': venue,
        }

        if event is None:
            event = Event(**kwargs)
            event.sync_with_eventbrite = True

        else:
            for attr in kwargs:
                setattr(event, attr, kwargs[attr])

        if 'published' in data:
            event.published_at = data['published']

        if 'logo' in data and data['logo'] is not None:
            event.banner = data['logo']['url']

        if not event.url:
            event.url = event.eventbrite_url

        # look for the academy ownership based on organizer first
        if organizer is not None and organizer.academy is not None:
            event.academy = organizer.academy

        elif org.academy is not None:
            event.academy = org.academy

        event.eventbrite_sync_description = now
        event.eventbrite_sync_status = 'PERSISTED'
        event.save()

        update_event_description_from_eventbrite(event)

    except Exception as e:
        if event is not None:
            event.eventbrite_sync_description = f'{now} => {e}'
            event.eventbrite_sync_status = 'ERROR'
            event.save()
        raise e

    return event


def publish_event_from_eventbrite(data, org: Organization) -> None:
    if not data:  #skip if no data
        logger.debug('Ignored event')
        raise ValueError('data is empty')

    now = get_current_iso_string()

    try:
        if not Event.objects.filter(eventbrite_id=data['id'], organization__id=org.id).count():
            raise Warning(f'The event with the eventbrite id `{data["id"]}` doesn\'t exist in breathecode '
                          'yet')

        kwargs = {
            'status': 'ACTIVE',
            'eventbrite_status': data['status'],
            'eventbrite_sync_description': now,
            'eventbrite_sync_status': 'PERSISTED'
        }

        Event.objects.filter(eventbrite_id=data['id'], organization__id=org.id).update(**kwargs)
        logger.debug(f'The event with the eventbrite id `{data["id"]}` was saved')

    except Warning as e:
        logger.error(f'{now} => {e}')
        raise e

    except Exception as e:
        logger.exception(f'{now} => the body is coming from eventbrite has change')
        raise e


def datetime_in_range(start: datetime, end: datetime, current: datetime):
    """
    Check if a datetime is in the range.

    Usages:

    ```py
    from django.utils import timezone
    from datetime import timedelta

    utc_now = timezone.now()
    start = utc_now - timedelta(days=1)
    end = utc_now + timedelta(days=1)

    datetime_in_range(start, end, utc_now)  # returns 0, the datetime is in the range

    utc_now = utc_now - timedelta(days=2)
    datetime_in_range(start, end, utc_now)  # returns -1, the datetime is less than start

    utc_now = utc_now + timedelta(days=4)
    datetime_in_range(start, end, utc_now)  # returns 1, the datetime is greater than start
    ```
    """

    if current < start:
        return -1

    if current > end:
        return 1

    return 0


def update_timeslots_out_of_range(start: datetime, end: datetime, timeslots: QuerySet[TimeSlot]):
    """
    Get a list of timeslots in the range.

    Usages:

    ```py
    from django.utils import timezone
    from datetime import timedelta

    start = utc_now - timedelta(days=1)
    end = utc_now + timedelta(days=1)
    queryset = ...

    update_timeslots_out_of_range(start, end, queryset)  # returns a list of timeslots
    ```
    """

    lists = []

    for timeslot in timeslots:
        starting_at = DatetimeInteger.to_datetime(timeslot.timezone, timeslot.starting_at)
        ending_at = DatetimeInteger.to_datetime(timeslot.timezone, timeslot.ending_at)
        delta = ending_at - starting_at

        n1 = datetime_in_range(start, end, starting_at)
        n2 = datetime_in_range(start, end, ending_at)

        less_than_start = n1 == -1 or n2 == -1
        greater_than_end = n2 == 1 or n2 == 1

        if not timeslot.recurrent and (less_than_start or greater_than_end):
            continue

        if less_than_start:
            starting_at = fix_datetime_weekday(start, starting_at, next=True)
            ending_at = starting_at + delta

        elif greater_than_end:
            ending_at = fix_datetime_weekday(end, ending_at, prev=True)
            starting_at = ending_at - delta

        lists.append({
            **vars(timeslot),
            'starting_at': starting_at,
            'ending_at': ending_at,
        })

    return sorted(lists, key=lambda x: (x['starting_at'], x['ending_at']))


def fix_datetime_weekday(current: datetime,
                         timeslot: datetime,
                         prev: bool = False,
                         next: bool = False) -> datetime:
    if not prev and not next:
        raise Exception('You should provide a prev or next argument')

    days = 0
    weekday = timeslot.weekday()
    postulate = datetime(year=current.year,
                         month=current.month,
                         day=current.day,
                         hour=timeslot.hour,
                         minute=timeslot.minute,
                         second=timeslot.second,
                         tzinfo=timeslot.tzinfo)

    while True:
        if prev:
            res = postulate - timedelta(days=days)
            if weekday == res.weekday():
                return res

        if next:
            res = postulate + timedelta(days=days)
            if weekday == res.weekday():
                return res

        days = days + 1


RECURRENCY_TYPE = {
    'DAILY': 'day',
    'WEEKLY': 'week',
    'MONTHLY': 'month',
}


def get_cohort_description(timeslot: CohortTimeSlot) -> str:
    description = ''

    if timeslot.recurrent:
        description += f'every {RECURRENCY_TYPE[timeslot.recurrency_type]}, '

    localtime = pytz.timezone(timeslot.cohort.academy.timezone)

    starting_at = localtime.localize(timeslot.starting_at)
    ending_at = localtime.localize(timeslot.ending_at)

    starting_weekday = starting_at.strftime('%A').upper()
    ending_weekday = ending_at.strftime('%A').upper()

    if starting_weekday == ending_weekday:
        description += f'{starting_weekday}'

    else:
        description += f'{starting_weekday} and {ending_weekday} '

    starting_hour = starting_at.strftime('%I:%M %p')
    ending_hour = ending_at.strftime('%I:%M %p')
    description += f'from {starting_hour} to {ending_hour}'

    return description.capitalize()


def get_ical_cohort_description(item: Cohort):
    description = ''
    # description = f'{description}Url: {item.url}\n'

    if item.name:
        description = f'{description}Name: {item.name}\n'

    if item.academy:
        description = f'{description}Academy: {item.academy.name}\n'

    if item.language:
        description = f'{description}Language: {item.language.upper()}\n'

    if item.private:
        description = f'{description}Private: {"Yes" if item.private else "No"}\n'

    if item.remote_available:
        description = f'{description}Online: {"Yes" if item.remote_available else "No"}\n'

    # TODO: add private url to meeting url

    return description
