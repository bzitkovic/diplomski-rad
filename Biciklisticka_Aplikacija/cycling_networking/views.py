import os
from unicodedata import name
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .countries import getCountries
from .forms import RideForm, UserForm, UserChangeForm, EventForm
from .models import User, Ride, Event
from .getRoute import get_route
import folium
from friendship.models import Friend, Follow, Block, FriendshipRequest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .rest_api.bike_reg_data import get_events
from .rest_api.strava_data import get_routes
from django.views.decorators.cache import cache_page
from geopy.geocoders import Nominatim


def home(request):
    return render(request, "home.html")


@login_required(login_url="loginPage")
def profile(request):
    user = request.user
    loggedUser = True
    rides = user.ride_set.all()
    friend_requests_users_id = []
    friend_requests_users = []
    page = request.GET.get("page", 1)
    friend_requests = Friend.objects.unread_requests(user=request.user)
    # number of items per page
    paginator = Paginator(rides, 2)

    try:
        rides = paginator.page(page)
    except PageNotAnInteger:
        rides = paginator.page(1)
    except EmptyPage:
        rides = paginator.page(paginator.num_pages)

    if request.GET.get("id"):
        loggedUser = False
        user = User.objects.get(id=request.GET.get("id"))
        rides = user.ride_set.all()

    for friend_request in friend_requests:
        friend_requests_users_id.append(int(str(friend_request).split("#")[1].split(" ")[0]))

    for user_id in friend_requests_users_id:
        friend_requests_users.append(User.objects.get(id=user_id))

    if "searchRides" in request.POST:
        if request.POST["searchRides"] == "":
            user_id = request.user.id
            user = User.objects.get(id=user_id)

            rides = user.ride_set.all().filter(title__contains=request.POST["searchRides"])

        else:
            user_id = request.user.id
            user2 = User.objects.get(id=user_id)

            rides = user2.ride_set.all().filter(
                title__contains=request.POST["searchRides"]
            ) or user2.ride_set.all().filter(title__contains=request.POST["searchRides"])

        paginator = Paginator(rides, 2)
        try:
            rides = paginator.page(page)
        except PageNotAnInteger:
            rides = paginator.page(1)
        except EmptyPage:
            rides = paginator.page(paginator.num_pages)

    context = {"user": user, "loggedUser": loggedUser, "friend_request_users": friend_requests_users, "rides": rides}
    return render(request, "profile.html", context)


@login_required(login_url="loginPage")
def updateProfile(request):
    if request.method == "POST":
        if request.FILES.get("avatar") != None:
            try:
                request.user.avatar.delete()
            except Exception as e:
                print("Exception in removing old profile image: ", e)
        form = UserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            storage = messages.get_messages(request)
            storage.used = True
            messages.success(request, "Profil uspješno ažuriran!")
            return redirect("profile")

    user = User.objects.get(id=request.user.id)
    form = UserForm(instance=user)
    form.fields.pop("password")

    context = {"form": form}

    return render(request, "update_profile.html", context)


def about(request):
    return render(request, "about.html")


def loginPage(request):
    page = "loginPage"

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)

        except:
            pass

        user = authenticate(request, username=username, password=password)

        if user != None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Username or password does not exist!")

    context = {"page": page}
    return render(request, "login_register.html", context)


def register(request):
    page = "register"
    form = UserForm()

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES)

        if form.is_valid():
            newUser = form.save(commit=False)
            newUser.username = newUser.username.lower()
            if newUser.bio == "":
                newUser.bio = "Not yet set."

            User.objects.create_user(
                username=newUser.username,
                name=newUser.name,
                password=newUser.password,
                email=newUser.email,
                bio=newUser.bio,
                avatar=newUser.avatar,
                country=newUser.country,
            )

            return redirect("home")
        else:
            messages.warning(request, "Dogodila se pogreška prilikom registracije!")

    context = {"page": page, "form": form}
    return render(request, "login_register.html", context)


def logoutUser(request):
    logout(request)
    return redirect("home")


@login_required(login_url="loginPage")
def users(request):
    users = User.objects.all()
    user_friends = Friend.objects.friends(request.user)[:5]
    user_friends_request = Friend.objects.unread_requests(user=request.user)
    loggedUser = request.user

    if "searchUsers" in request.POST:
        users = users.filter(username__contains=request.POST["searchUsers"]) or users.filter(
            name__contains=request.POST["searchUsers"]
        )
        for friend in user_friends:
            users = users.filter(~Q(username=friend.username))
        for friend in user_friends_request:
            users = users.filter(~Q(id=int(str(friend).split("#")[1].split(" ")[0])))

    if loggedUser in users:
        try:
            users = users.filter(~Q(username=loggedUser.username))
            for friend in user_friends:
                users = users.filter(~Q(username=friend.username))
            for friend in user_friends_request:
                users = users.filter(~Q(id=int(str(friend).split("#")[1].split(" ")[0])))

            users = users.filter(country__contains=loggedUser.country).order_by("id")[:5]

        except:
            pass

    if "searchFriends" in request.POST:
        user_friends = Friend.objects.friends(request.user)

        for friend in user_friends[:]:
            if (
                request.POST["searchFriends"] not in friend.username
                and request.POST["searchFriends"] not in friend.name
            ):
                user_friends.remove(friend)
        if len(user_friends) > 1:
            user_friends = user_friends[:5]

    context = {"users": users, "friends": user_friends}

    return render(request, "users.html", context)


@login_required(login_url="loginPage")
def showMap(request):
    return render(request, "show_map.html")


@login_required(login_url="loginPage")
def showRoute(request, lat1, long1, lat2, long2):
    form = RideForm()
    ride = Ride()

    if request.method == "POST":
        form = RideForm(request.POST, request.FILES)
        if form.is_valid():
            newRide = form.save(commit=False)
            current_user = User.objects.get(id=request.user.id)

            Ride.objects.create(
                title=newRide.title,
                start_latitude=lat1,
                start_longitude=long1,
                end_latitude=lat2,
                end_longitude=long2,
                description=newRide.description,
                ride_date=newRide.ride_date,
                ride_image=newRide.ride_image,
                cyclist=current_user,
            )

            return redirect("home")

    figure = folium.Figure()
    lat1, long1, lat2, long2 = float(lat1), float(long1), float(lat2), float(long2)
    route = get_route(long1, lat1, long2, lat2)

    m = folium.Map(location=[(route["start_point"][0]), (route["start_point"][1])], zoom_start=10)
    m.add_to(figure)

    folium.PolyLine(route["route"], weight=8, color="blue", opacity=0.6).add_to(m)
    folium.Marker(location=route["start_point"], icon=folium.Icon(icon="play", color="green")).add_to(m)
    folium.Marker(location=route["end_point"], icon=folium.Icon(icon="stop", color="red")).add_to(m)
    figure.render()

    if request.GET.get("id"):
        ride_id = request.GET.get("id", "")
        ride = Ride.objects.get(id=ride_id)
        form = RideForm(instance=ride)

        if ride.cyclist_id != request.user.id:
            form.fields["title"].disabled = True
            form.fields["description"].disabled = True
            form.fields["ride_date"].disabled = True
            form.fields["ride_image"].disabled = True

    context = {"map": figure, "coors": [lat1, long1, lat2, long2], "form": form, "ride": ride}
    return render(request, "show_route.html", context)


def updateRide(request):
    ride_id = request.GET.get("id", "")
    ride = Ride.objects.get(id=ride_id)

    if request.method == "POST":
        if request.FILES.get("ride_image") != None:
            try:
                ride.ride_image.delete()
            except Exception as e:
                print("Exception in removing old ride image: ", e)
        form = RideForm(request.POST, request.FILES, instance=ride)
        if form.is_valid():
            form.save()
            storage = messages.get_messages(request)
            storage.used = True
            messages.success(request, "Vožnja uspješno ažurirana!")
            return redirect("profile")

    return render(request, "profile.html")


def deleteRide(request):
    ride_id = request.GET.get("id", "")

    if ride_id != None:
        ride = Ride.objects.get(id=ride_id)
        ride.delete()
        messages.success(request, "Vožnja uspješno izbrisana!")
        return redirect("profile")


def addFriend(request):
    friend_to_accept_id = request.GET.get("id", "")
    friend_to_accept = User.objects.get(id=friend_to_accept_id)

    try:
        Friend.objects.add_friend(
            request.user,
            friend_to_accept,
        )
    except:
        messages.error(request, "Zahtjev je već poslan!")

    return redirect("users")


def acceptFriendRequest(request):
    friend_to_accept_id = request.GET.get("id", "")
    friend_to_accept = User.objects.get(id=friend_to_accept_id)

    friend_request = FriendshipRequest.objects.get(
        from_user=friend_to_accept,
        to_user=request.user,
    )
    friend_request.accept()

    messages.success(request, "Korisnik uspješno prihvaćen!")

    return redirect("profile")


def removeFriendRequest(request):
    friend_to_remove_id = request.GET.get("id", "")
    friend_to_remove = User.objects.get(id=friend_to_remove_id)

    friend_request = FriendshipRequest.objects.get(
        from_user=friend_to_remove,
        to_user=request.user,
    )
    friend_request.reject()
    friend_request.cancel()
    Friend.objects.remove_friend(request.user, friend_to_remove)

    messages.success(request, "Korisnik uspješno odbijen!")

    return redirect("profile")


def removeFriend(request):
    friend_to_remove_id = request.GET.get("id", "")
    friend_to_remove = User.objects.get(id=friend_to_remove_id)

    Friend.objects.remove_friend(
        request.user,
        friend_to_remove,
    )

    messages.success(request, "Prijateljstvo uspješno uklonjeno!")

    return redirect("users")


@cache_page(60 * 15)
def events(request):
    eventType = ""
    eventLocation = ""
    eventName = ""
    eventYear = ""
    eventDistance = ""

    events = get_events(
        eventType,
        eventLocation,
        eventName,
        eventYear,
        eventDistance,
    )
    user_events = Event.objects.all()

    for user_event in user_events:
        events.append(user_event)

    page = request.GET.get("page", 1)

    if request.POST:
        eventType = request.POST["eventType"]
        eventLocation = request.POST["eventLocation"]
        eventName = request.POST["eventName"]
        eventYear = request.POST["eventYear"]
        eventDistance = request.POST["eventDistance"]

        if eventType == "" and eventLocation == "" and eventName == "" and eventYear == "" and eventDistance == "":
            return redirect("events")

        events.clear()
        events = get_events(
            eventType,
            eventLocation,
            eventName,
            eventYear,
            eventDistance,
        )

        for user_event in user_events:
            if eventName in user_event.name:
                events.append(user_event)

    paginator = Paginator(events, 9)
    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)
    except EmptyPage:
        events = paginator.page(paginator.num_pages)

    context = {"events": events}

    return render(request, "events.html", context)


def userEvents(request):
    events = request.user.event_set.all()

    if request.POST:
        events = events.filter(name__contains=request.POST["eventName"])

    context = {"events": events}

    return render(request, "user_events.html", context)


def newEvent(request):
    form = EventForm(request.POST)

    if form.is_valid():
        newEvent = form.save(commit=False)

        Event.objects.create(
            name=newEvent.name,
            city=newEvent.city,
            date=newEvent.date,
            entry_fee=newEvent.entry_fee,
            url=newEvent.url,
            start_latitude=newEvent.start_latitude,
            start_longitude=newEvent.start_longitude,
            end_latitude=newEvent.end_latitude,
            end_longitude=newEvent.end_longitude,
            cyclist=request.user,
        )

        return redirect("userEvents")

    context = {"form": form}

    return render(request, "new_event.html", context)


def updateEvent(request):
    event_id = request.GET.get("id", "")
    event = Event.objects.get(id=event_id)
    form = EventForm(instance=event)

    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            storage = messages.get_messages(request)
            storage.used = True
            messages.success(request, "Događaj uspješno ažuriran!")
            return redirect("userEvents")

    context = {"form": form}

    return render(request, "update_event.html", context)


def deleteEvent(request):
    event_id = request.GET.get("id", "")

    if event_id != None:
        event = Event.objects.get(id=event_id)
        event.delete()
        messages.success(request, "Događaj uspješno izbrisan!")
        return redirect("userEvents")


@cache_page(60 * 15)
def routes(request):
    page = request.GET.get("page", 1)
    countries = getCountries()

    try:
        routes = get_routes()
    except:
        messages.error(request, "Servis trenutno nedostupan!")
        return redirect("home")

    if request.POST:
        routeName = request.POST["routeName"]
        routeCountry = request.POST["routeCountry"]
        routeElevationHigh = request.POST["routeElevationHigh"]
        routeClimbCategory = request.POST["routeClimbCategory"]

        if routeName == "" and routeCountry == "" and routeElevationHigh == "" and routeClimbCategory == "":
            return redirect("routes")
        else:
            temp_routes = routes[:]
            routes.clear()

            for route in temp_routes:

                try:
                    float(routeElevationHigh)
                except:
                    routeElevationHigh = 0.0
                # print(routeName in route["name"])
                # print(routeCountry in route["country"])
                # print(route["elevation_high"] <= float(routeElevationHigh))
                # print(route["climb_category"] <= int(routeClimbCategory))
                if routeElevationHigh == 0.0:
                    if (
                        routeName in route["name"]
                        and routeCountry in route["country"]
                        and route["climb_category"] <= int(routeClimbCategory)
                    ):
                        routes.append(route)

                elif (
                    routeName in route["name"]
                    and routeCountry in route["country"]
                    and route["elevation_high"] <= float(routeElevationHigh)
                    and route["climb_category"] <= int(routeClimbCategory)
                ):
                    routes.append(route)

    paginator = Paginator(routes, 9)
    try:
        routes = paginator.page(page)
    except PageNotAnInteger:
        routes = paginator.page(1)
    except EmptyPage:
        routes = paginator.page(paginator.num_pages)

    context = {"routes": routes, "countries": countries}
    return render(request, "routes.html", context)


@cache_page(60 * 15)
def exploreRoute(request):
    route_id = request.GET.get("id", "")
    lat1 = 0.0
    long1 = 0.0
    lat2 = 0.0
    long2 = 0.0

    try:
        routes = get_routes()
    except:
        messages.error(request, "Servis trenutno nedostupan!")
        return redirect("routes")

    for s_route in routes:
        if s_route["id"] == int(route_id):
            strava_route = s_route
            lat1 = s_route["start_latlng"][0]
            long1 = s_route["start_latlng"][1]
            lat2 = s_route["end_latlng"][0]
            long2 = s_route["end_latlng"][1]

    figure = folium.Figure()
    lat1, long1, lat2, long2 = float(lat1), float(long1), float(lat2), float(long2)

    route = get_route(long1, lat1, long2, lat2)

    map = folium.Map(location=[(route["start_point"][0]), (route["start_point"][1])], zoom_start=10)
    map.add_to(figure)

    folium.PolyLine(route["route"], weight=8, color="blue", opacity=0.6).add_to(map)
    folium.Marker(location=route["start_point"], icon=folium.Icon(icon="play", color="green")).add_to(map)
    folium.Marker(location=route["end_point"], icon=folium.Icon(icon="stop", color="red")).add_to(map)
    figure.render()

    context = {"map": figure, "coors": [lat1, long1, lat2, long2], "route": strava_route}

    return render(request, "explore_route.html", context)


def closeRoutes(request):
    geolocator = Nominatim(user_agent="Kotur")
    routes = []

    if request.POST:
        placeName = request.POST["placeName"]
        location = geolocator.geocode(placeName)

        if placeName == "":
            return redirect("closeRoutes")

        try:
            routes = get_routes()
        except:
            messages.error(request, "Servis trenutno nedostupan!")
            return redirect("home")

        temp_routes = routes[:]
        routes.clear()

        for route_loop in temp_routes:
            if (
                abs(location.latitude - route_loop["start_latlng"][0]) < 0.5
                and abs(location.longitude - route_loop["start_latlng"][1]) < 0.5
            ):
                routes.append(route_loop)

        print(location.latitude, location.longitude)

    context = {"routes": routes}
    return render(request, "close_routes.html", context)
