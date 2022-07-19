import requests
import polyline


def get_route(start_lon, start_lat, end_lon, end_lat):
    coordinates = "{},{};{},{}".format(start_lon, start_lat, end_lon, end_lat)
    api_url = "http://router.project-osrm.org/route/v1/bike/"
    r = requests.get(api_url + coordinates)

    if r.status_code != 200:
        return {}

    res = r.json()
    routes = polyline.decode(res["routes"][0]["geometry"])
    start_point = [res["waypoints"][0]["location"][1], res["waypoints"][0]["location"][0]]
    end_point = [res["waypoints"][1]["location"][1], res["waypoints"][1]["location"][0]]
    distance = res["routes"][0]["distance"]

    context = {"route": routes, "start_point": start_point, "end_point": end_point, "distance": distance}

    return context
