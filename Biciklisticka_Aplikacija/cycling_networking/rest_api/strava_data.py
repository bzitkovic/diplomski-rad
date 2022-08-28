import requests
import json


def get_routes():
    auth_url = "https://www.strava.com/oauth/token"
    activities_url = "https://www.strava.com/api/v3/segments/starred"
    routes = []

    payload = {
        "client_id": "89543",
        "client_secret": "7ff0c05610a3dc39626903315ec86ad63e7de2d1",
        "refresh_token": "26494aa34db45bb55e5da780ffad671028038fb0",
        "grant_type": "refresh_token",
        "f": "json",
    }

    response = requests.post(auth_url, data=payload, verify=False)
    access_token = response.json()["access_token"]
    print(access_token)

    header = {"Authorization": "Bearer " + access_token}
    param = {"per_page": 200, "page": 1}
    routes_response = requests.get(activities_url, headers=header, params=param)

    parse_routes = json.loads(routes_response.text)

    for route in parse_routes:
        routes.append(route)

    return routes
