from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("profile", views.profile, name="profile"),
    path("login", views.loginPage, name="loginPage"),
    path("register", views.register, name="register"),
    path("logout", views.logoutUser, name="logout"),
    path("about", views.about, name="about"),
    path("users", views.users, name="users"),
    path("<str:lat1>,<str:long1>,<str:lat2>,<str:long2>", views.showRoute, name="showRoute"),
    path("showmap", views.showMap, name="showmap"),
    path("updateRide", views.updateRide, name="updateRide"),
    path("deleteRide", views.deleteRide, name="deleteRide"),
    path("updateProfile", views.updateProfile, name="updateProfile"),
    path("addFriend", views.addFriend, name="addFriend"),
    path("removeFriendRequest", views.removeFriendRequest, name="removeFriendRequest"),
    path("acceptFriendRequest", views.acceptFriendRequest, name="acceptFriendRequest"),
    path("removeFriend", views.removeFriend, name="removeFriend"),
    path("events", views.events, name="events"),
    path("userEvents", views.userEvents, name="userEvents"),
    path("newEvent", views.newEvent, name="newEvent"),
    path("updateEvent", views.updateEvent, name="updateEvent"),
    path("deleteEvent", views.deleteEvent, name="deleteEvent"),
    path("routes", views.routes, name="routes"),
    path("exploreRoute", views.exploreRoute, name="exploreRoute"),
    path("closeRoutes", views.closeRoutes, name="closeRoutes"),
]
