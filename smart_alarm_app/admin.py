from ast import Add
from django.contrib import admin
from .models import CalendarEvent, Night, InsideTemp, OutsideTemp, LightValue, NoiseValue, PinValue, Address

# Register your models here.
admin.site.register(CalendarEvent)
admin.site.register(Night)
admin.site.register(InsideTemp)
admin.site.register(OutsideTemp)
admin.site.register(LightValue)
admin.site.register(NoiseValue)
admin.site.register(PinValue)
admin.site.register(Address)