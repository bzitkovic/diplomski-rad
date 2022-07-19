from django.contrib import admin

from cycling_networking.views import events
from .models import User, Ride, Event


admin.site.register(User)
admin.site.register(Ride)
admin.site.register(Event)
