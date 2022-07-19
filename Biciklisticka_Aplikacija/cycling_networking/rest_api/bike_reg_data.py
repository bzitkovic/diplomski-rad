import requests
import json
from .models import BikeEvent
import datetime
import time


def get_events(eventType, eventLocation, eventName, eventYear, eventDistance):
    url = ""

    if eventType != "":
        url += "eventtype=" + eventType + "&"
    if eventLocation != "":
        url += "loc=" + eventLocation + "&"
    if eventName != "":
        url += "name=" + eventName + "&"
    if eventYear != "":
        url += "year=" + eventYear + "&"
    if eventDistance != "":
        url += "distance=" + eventDistance

    response_API = requests.get(f"http://www.BikeReg.com/api/search?{url}")
    events = []

    data = response_API.text
    parse_json = json.loads(data)

    for event in parse_json["MatchingEvents"]:
        event_date = datetime.datetime.fromtimestamp(int(event["EventDate"].split("(")[1].split("-")[0][:-3])).strftime(
            "%d-%m-%Y %H:%M"
        )

        new_event = BikeEvent(
            name=event["EventName"],
            city=event["EventCity"],
            date=event_date,
            url=event["EventUrl"],
        )

        for category in event["Categories"]:
            new_event.entry_fee = category["EntryFee"]

        events.append(new_event)

    return events
