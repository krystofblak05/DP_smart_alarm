from rest_framework import serializers
from django.contrib.auth.models import User
from datetime import datetime
from smart_alarm_app.models import CalendarEvent, InsideTemp, OutsideTemp, LightValue, NoiseValue, Night
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'name', #bacha musí tam být čárka!!!
        )

class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = (
            'name','minutes','user' #bacha musí tam být čárka!!!
        )

class InsideTempSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsideTemp
        fields = (
            'night_id', 'temp', 'hum', 'date'
        )

class OutsideTempSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutsideTemp
        fields = (
            'night_id', 'date', 'temp_now','hum_now','pressure_now',
            'pred','temp','timestemp','pred_next','temp_next','timestemp_next'
        )

class NoiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoiseValue
        fields = (
            'night_id', 'date', 'noise_val'
        )

class LightSerializer(serializers.ModelSerializer):
    class Meta:
        model = LightValue
        fields = (
            'night_id', 'date', 'light_val'
        )

class BasicSerializer(serializers.ModelSerializer):
    
    light_values = LightSerializer(many=True)
    noise_values = NoiseSerializer(many=True)
    inside_values = InsideTempSerializer(many=True)
    outside_values = OutsideTempSerializer(many=True)
    
    class Meta:
        model = Night
        fields = ['id','date', 'user', 'wake_up','active', 'light_values','noise_values','inside_values','outside_values']

class ActiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Night
        fields = (
            'id', 'active', 'wake_up','music'
        )

class NightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Night
        fields = (
            'id', 'date', 'wake_up','active','user','music','drunk','tired'
        )