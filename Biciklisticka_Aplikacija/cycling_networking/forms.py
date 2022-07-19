from dataclasses import field
from click import DateTime
from django.conf import settings
from django.contrib.auth.forms import UserChangeForm
from django.forms import DateTimeInput, ModelForm, fields
from .models import User, Ride, Event
from django import forms
from django.core.files.images import get_image_dimensions


class UserForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control form-control-lg"

    name = forms.CharField(label="Ime")
    username = forms.CharField(label="Korisničko ime")
    email = forms.CharField(label="Email")
    bio = forms.Textarea()
    password = forms.CharField(widget=forms.PasswordInput(), label="Lozinka")
    avatar = forms.ImageField(widget=forms.FileInput(attrs={"class": "form-control-file"}), required=False)

    class Meta:
        model = User
        fields = [
            "name",
            "username",
            "email",
            "bio",
            "country",
            "password",
            "avatar",
        ]


class UserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            "name",
            "username",
            "email",
            "bio",
            "country",
            "avatar",
        )
        exclude = ("password",)


class DatePickerInput(forms.DateInput):
    input_type = "date"
    format = "%d/%m/%Y"


class DateTimePickerInputEvent(forms.DateTimeInput):
    input_type = "datetime-local"
    input_formats = "%d-%m-%Y %H:%M"


class RideForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control form-control-lg"

    title = forms.CharField(label="Naziv vožnje")
    description = forms.CharField(widget=forms.Textarea, label="Opis vožnje", required=False)
    ride_date = forms.DateField(widget=DatePickerInput, label="Datum vožnje", required=False)
    ride_image = forms.ImageField(
        label="Slika vožnje", widget=forms.FileInput(attrs={"class": "form-control-file"}), required=False
    )

    class Meta:
        model = Ride
        exclude = (
            "start_latitude",
            "start_longitude",
            "end_latitude",
            "end_longitude",
            "cyclist",
        )


class EventForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control form-control-lg"

    name = forms.CharField(label="Naziv događaja")
    city = forms.CharField(label="Grad održavanja")
    date = forms.DateTimeField(widget=DateTimePickerInputEvent, label="Datum i vrijeme događaja")
    entry_fee = forms.CharField(label="Kotizacija")
    url = forms.CharField(label="Web stranica događaja (neobavezno)", required=False)
    start_latitude = forms.FloatField(label="Startna geo. dužina")
    start_longitude = forms.FloatField(label="Startna geo. širina")
    end_latitude = forms.FloatField(label="Ciljna geo. dužina")
    end_longitude = forms.FloatField(label="Ciljna geo. širina")

    class Meta:
        model = Event
        exclude = ("cyclist",)

        # fields = [
        #     "name",
        #     "city",
        #     "date",
        #     "entry_fee",
        #     "url",
        #     "start_latitude",
        #     "start_longitude",
        #     "end_latitude",
        #     "end_longitude",
        # ]
