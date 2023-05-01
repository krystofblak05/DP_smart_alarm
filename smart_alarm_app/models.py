from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

class CalendarEvent(models.Model):
    name = models.CharField(max_length=1000000)
    minutes = models.IntegerField()
    user = models.CharField(max_length=100000)
    bad_weather = models.BooleanField(default=False)

class Night(models.Model):
    lon = models.FloatField(null=True)
    lat = models.FloatField(null=True)
    date = models.DateTimeField(default=datetime.now, blank=True)
    wake_up = models.DateTimeField(default=datetime.now, blank=True)
    active = models.BooleanField(default=True)
    user = models.CharField(max_length=1000000)
    review_sleep = models.FloatField(null=True, blank=True)
    pred_review = models.FloatField(null=True, blank=True)
    music = models.IntegerField(default=0)
    google = models.CharField(null=True, blank=True,max_length=1000000)
    drunk = models.BooleanField(default=False)
    tired = models.BooleanField(default=False)
    bad_weather = models.BooleanField(default=False) #hodnota pro cron zkoumající předpověď počasí

class InsideTemp(models.Model):
    night_id = models.ForeignKey(Night, related_name="inside_values", on_delete=models.CASCADE)
    temp = models.FloatField()
    hum = models.FloatField()
    date = models.DateTimeField(default=datetime.now, blank=True)

    def time_posted(self):
        return self.date.strftime('%Y')

class OutsideTemp(models.Model):
    night_id = models.ForeignKey(Night,related_name="outside_values", on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.now, blank=True)
    temp_now = models.IntegerField()
    hum_now = models.IntegerField()
    pressure_now = models.IntegerField()
    pred = models.CharField(null=True, blank=True,max_length=1000)
    temp = models.FloatField()
    timestemp = models.DateTimeField(default=datetime.now, blank=True)
    pred_next = models.CharField(null=True, blank=True,max_length=1000)
    temp_next = models.FloatField()
    timestemp_next = models.DateTimeField(default=datetime.now, blank=True)


class LightValue(models.Model):
    night_id = models.ForeignKey(Night, related_name="light_values", on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.now, blank=True)
    light_val = models.IntegerField()

class NoiseValue(models.Model):
    night_id = models.ForeignKey(Night, related_name="noise_values", on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.now, blank=True)
    noise_val = models.IntegerField()

class PinValue(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    pincode = models.IntegerField()

class Address(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    lat = models.FloatField(null=True)
    lon = models.FloatField(null=True)
    address = models.CharField(max_length=100000)
