from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import CalendarEvent, LightValue, Night, InsideTemp, NoiseValue, OutsideTemp, PinValue, Address
from django.contrib.auth.models import User, auth
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone
from dateutil import parser
from .scripts import generateCSV, predReview
from .utils import get_temp_plot, get_hum_plot, get_noise_plot, get_light_plot

#REST
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import InsideTempSerializer, OutsideTempSerializer, LightSerializer, NoiseSerializer, ActiveSerializer, NightSerializer
from smart_alarm_app import serializers

#this makes all nonlog users go away
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    if request.method == 'POST':
        #načtu věci z formuláře
        lon = request.POST['lon']
        lat = request.POST['lat']
        date_str = request.POST['today']
        wake_up_str = request.POST['wakeup']
        user = request.POST['user']
        google = (request.POST['google']).lower()
        ignore = request.POST.get('googleignore', '') == 'on'
        drunk = request.POST.get('drunk', '') == 'on'
        tired = request.POST.get('tired', '') == 'on'

        date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        if wake_up_str != 'None': 
            wakeup = datetime.strptime(wake_up_str, '%Y-%m-%d %H:%M:%S')

        #pokud lokace nebyla povolena, načtou se data z defaultní adresy
        if lon == "" or lat == "":
            try:
                address = Address.objects.filter(user=request.user).get()
                lon = address.lon
                lat = address.lat
            except Address.DoesNotExist:
                return redirect('address')

        #algoritmus, určující přibližnou dobu probuzení
        if google == 'none' or ignore == True:
            wake_up = date + timedelta(hours=8)
            google = 'none'
        else:
            try: 
                that_event = CalendarEvent.objects.filter(user=user).get(name__contains=google)
                event_time = that_event.minutes
                wake_up = wakeup - timedelta(minutes=event_time)
            except CalendarEvent.DoesNotExist:
                #wake_up = date + timedelta(hours=8)
                return redirect('settings/addEvent')
        
        #kontrola, jestli neexistuje jiný active budík
        already_active = Night.objects.filter(active=True).count()
        if already_active > 0:
            return redirect('index')
        else:
            #vytvoření nové noci
            new_night = Night.objects.create(lon=lon, lat=lat, date=date,wake_up=wake_up, user=user, google=google, drunk=drunk, tired=tired)
            new_night.save()
        wake_up_hours = wake_up.strftime("%d %b, %Y %H:%M:%S")
        return render(request,'index.html',{'night':new_night, 'wake_up': wake_up_hours}) 
    else:
        #pokud existuje nějaká last night
        if Night.objects.filter(user=request.user).exists():
            last_night = Night.objects.filter(user=request.user).last()
            if last_night.review_sleep is None and last_night.active is False:
                response = redirect('review')
                response['Location'] += '?night='+ str(last_night.id)
                return response
        if Night.objects.filter(active=True).exists():
            #načtu si aktivní noc
            night = Night.objects.get(active=True)
            user = request.user.is_authenticated
            #Zjistím, jestli už nemá být budík vyplý
            
            #zkouška vypnutí téhle části
            if night.wake_up > timezone.now():
                go_sleep_hours = night.date
                wake_up_hours = night.wake_up.strftime("%d %b, %Y %H:%M:%S")
                
                #vyhledání google eventu
                cal_event = night.google
                if cal_event == 'None':
                    event_time = 0
                else:
                    try: 
                        that_event = CalendarEvent.objects.filter(user=user).get(name__contains=cal_event)
                        event_time = that_event.minutes
                    except CalendarEvent.DoesNotExist:
                        event_time = 'nenalezeno, doplň do tabulky'
                return render(request,'index.html',{'night':night, 'go_sleep':go_sleep_hours, 'wake_up': wake_up_hours, 'event':event_time})
            else: 
                return redirect('stopPin')
        else:
            from .scripts import googleCalendar
            googleCalendar.main()
            night = ''
            googleevent = ''
            with open('static/google.json', 'r') as f:
                event = json.load(f)
                if event['summary'] != 'no-event':
                    event_start_time = str(parser.isoparse(event['start']['dateTime']).replace(tzinfo=None))
                    googleevent = {'summary':event['summary'], 'start': event_start_time}
                else:
                    googleevent = {'summary':'None', 'start':'None'}
            return render(request,'index.html',{'night':night, 'event':googleevent})

#Vypnutí budíku
@login_required
def stopalarm(request):
    if Night.objects.filter(active=True).exists():
        #načtu si aktivní noc
        night = Night.objects.get(active=True)
        night.wake_up = datetime.now()
        night.active = True
        night.save()
        response = redirect('review')
        response['Location'] += '?night='+ str(night.id)
        return response
    else:
        return redirect('index')

#Zadání PINu pro vypnutí
@login_required
def stopPin(request):
    if request.method == 'POST':
        night =  Night.objects.get(active=True)
        formpincode = request.POST['pincode']
        dbpin = PinValue.objects.get(user=request.user)

        #Validace formuláře jestli v něm něco je
        if not formpincode:
            return redirect('stopPin')
        #Validace jestli jsou PINy stejné
        if dbpin.pincode == int(formpincode):
            return redirect('review')
        else:
            return render(request, 'stopPin.html',{'alert':"Zadaný PIN je nesprávný",'night':night})
    else:
        if Night.objects.filter(active=True).exists():
            night =  Night.objects.get(active=True)
            return render(request, 'stopPin.html', {'night':night})
        else:
            return redirect('index')

#Správa uživatele
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if not username or not email or not password or not password2:
            return redirect('register')

        if password2 == password:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email already registered')
                return redirect('register')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username already used')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                new_pin = '1234'
                pin_profile = PinValue.objects.create(user=user, pincode=new_pin)
                pin_profile.save()
                return redirect('login')
        else:
            messages.info(request, 'Passwords are not the same')
            return redirect('register')
    else:
        return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            next = request.GET.get('next', '/')
            return redirect(next)
        else:
            messages.info(request, 'Credentials invalid')
            return redirect('login')

    else:
        return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

#Výpis všech nocí
@login_required
def history(request):
    nights = Night.objects.filter(user=request.user).order_by('-wake_up')
    return render(request, 'history.html',{'nights':nights})

#Výpis jedné noci
@login_required
def night(request, pk):
    id = pk
    try:
        night = Night.objects.get(id=id)
    except Night.DoesNotExist:
        return redirect('history')
    #Pokud noc už skončila a není přidáno hodnocení, chceme uživatele donutit hodnocení zadat
    if night.review_sleep is None and night.wake_up < datetime.now():
        #return redirect('review.html/'+ {{night.id}})
        response = redirect('review')
        response['Location'] += '?night='+ str(id)
        #response = redirect('stopPin')
        return response
    elif night.review_sleep is None and night.wake_up > datetime.now():
        return redirect('index')
    else:
        tempValues = InsideTemp.objects.values_list('temp', flat=True)
        humValues = InsideTemp.objects.values_list('hum', flat=True)
        timeValues = InsideTemp.objects.values_list('date', flat=True)
        #once I used
        temps = InsideTemp.objects.filter(night_id = id)
        outsideTemp = OutsideTemp.objects.filter(night_id = id)
        light = LightValue.objects.filter(night_id = id)
        noise = NoiseValue.objects.filter(night_id = id)
        temp_chart = get_temp_plot(id)
        hum_chart = get_hum_plot(id)
        noise_chart = get_noise_plot(id)
        light_chart = get_light_plot(id)
        return render(request, 'night.html',{'night': night, 'temps': temps, 'tempVals': tempValues, 'humVals': humValues,
        'timeVals':timeValues, 'outsideTemp': outsideTemp, 'light':light, 'noise':noise, 'temp_chart': temp_chart, 'hum_chart': hum_chart, 'noise_chart':noise_chart, 'light_chart': light_chart})

#Hodnocení poslední noci
@login_required
def review(request):
    user = request.user
    if request.method == 'GET':
        id = request.GET.get('night', '')
        if id != '' and Night.objects.filter(id=id, user=user).exists():
            that_night = Night.objects.get(id=id)
            return render(request, 'review.html',{'night':that_night})
        elif id == '' and Night.objects.filter(user=user).exists:
            last_missing = Night.objects.filter(user=user).last()
            return render(request, 'review.html',{'night':last_missing})
        else:
            return redirect('index') 
    elif request.method == 'POST':
        review_sleep = request.POST['review_sleep']
        id = request.POST['id']
        generateCSV.main(id)
        Night.objects.filter(id=id).update(review_sleep=review_sleep,active=False)
        return redirect('history')
    else:
        return redirect('index')

#Část nastavení předvolby Eventů
@login_required
def settings(request):
    pcode = PinValue.objects.filter(user=request.user).get()
    calendar_events = CalendarEvent.objects.filter(user=request.user)
    try:
        address = (Address.objects.filter(user=request.user).get()).address
    except Address.DoesNotExist:
        address = 'Nebyla nastavena'
    return render(request, 'settings.html',{'events':calendar_events, 'pincode':pcode.pincode, 'address':address})

@login_required
def addEvent(request):
    if request.method == 'POST':
        name = (request.POST['name']).lower()
        minutes = request.POST['minutes']
        user = request.POST['user']
        ignore = request.POST.get('bad_weather', '') == 'on'

        if not name and not minutes:
            return render(request, 'addEvent.html', {'error': 'Doplňte chybějící hodnoty'})
        if not name:
            return render(request, 'addEvent.html', {'error': 'Doplňte jméno události', 'minutes': minutes})
        if not minutes:
            return render(request, 'addEvent.html', {'event_name': name, 'error': 'Doplňte čas před probuzením'})

        if CalendarEvent.objects.filter(name=name, user=user).exists():
            CalendarEvent.objects.filter(name=name, user=user).update(name=name, minutes=minutes, bad_weather=ignore)
            return redirect('settings')
        else:
            new_event = CalendarEvent.objects.create(name=name, minutes=minutes, user=user, bad_weather=ignore)
            new_event.save()
            return redirect('settings')

    else:
        googleevent = ''
        user = request.user.is_authenticated
        with open('static/google.json', 'r') as f:
            event = json.load(f)
            number = CalendarEvent.objects.filter(name__contains=(event['summary']).lower()).count()
            if number == 0 and event['summary'] != 'no-event':
                googleevent = event['summary']
        return render(request, 'addEvent.html',{'event_name': googleevent, 'number':number})

@login_required
def editEvent(request,pk):
    id = pk
    user = request.user.username
    if request.method == 'POST':
        if CalendarEvent.objects.filter(id=id).exists():
            name = (request.POST['name']).lower()
            minutes = request.POST['minutes']
            ignore = request.POST.get('bad_weather', '') == 'on'
            if not name or not minutes:
                return redirect('settings')
            CalendarEvent.objects.filter(id=id).update(name=name, minutes=minutes, bad_weather=ignore)
            return redirect('settings')
    else:
        if CalendarEvent.objects.filter(id=id,user=user).exists():
            event = CalendarEvent.objects.get(id=id)
            return render(request, 'editEvent.html', {'event': event})
        else:
            return redirect('settings')

@login_required
def deleteEvent(request,pk):
    id = pk
    if CalendarEvent.objects.filter(id=id).exists():
        CalendarEvent.objects.filter(id=id).delete()
        return redirect('settings')
    else:
        return redirect('addEvent') 

#Editace pincodu (defaultně nastaven na 0000)
@login_required
def pincode(request):
    user = request.user
    if request.method == 'POST':
        pcode = PinValue.objects.get(user=user)
        code = (request.POST['code'])
        if len(str(code)) == 4:
            PinValue.objects.filter(user=user).update(pincode=code)
        return redirect('settings')
    else:
        if PinValue.objects.filter(user=user).exists():
            pcode = PinValue.objects.get(user=user)
            return render(request, 'pincode.html', {'pincode': pcode.pincode})
        else:
            return redirect('settings')

#Práce s defaultní polohou
import requests
@login_required
def predefAddress(request):
    user = request.user
    if request.method == 'POST':
        address = request.POST['address']
        if not address or address == 'Není vyplněna':
            return redirect('address')
        url = 'https://api.geoapify.com/v1/geocode/search'
        params = {
            'text': address,
            'format': 'json',
            'apiKey': '7e3ff67541ed4274bfbf18e5c2288c7c'
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            lon = data['results'][0]['lon']
            lat = data['results'][0]['lat']
            if Address.objects.filter(user=user).exists():
                Address.objects.filter(user=user).update(lon=lon, lat=lat,address=address)
            else:
                new_address = Address.objects.create(user=user, address=address, lon=lon, lat=lat)
                new_address.save()
            address_object = {'address': address, 'lat': lat, 'lon': lon}
            return render(request, 'address.html', {'data': address_object})
        else:
            return HttpResponse('Error: ' + str(response.status_code))
    else:
        if Address.objects.filter(user=user).exists():
            address = Address.objects.filter(user=user).get()
        else:
            address = {'address':'Není vyplněna', 'lat':100, 'lon': 100}
        return render(request, 'address.html', {'data':address})

#Stránka pro generování CSV All Nights
@login_required
def csvTry(request):
    user = "admin"
    generateCSV.allnights(user)
    return render(request, 'csvTry.html')

#Poloha a počasí
from django.http import HttpResponse, JsonResponse
import json, urllib.request

#REST
class ArduinoRest(APIView):
    permission_classes = (IsAuthenticated, ) #bude požadován token

    def get(self, request, *args, **kwargs):
        querySet = Night.objects.filter(active=True)
        if querySet.exists():
            serializer = ActiveSerializer(querySet, many=True)
            serialized_data = serializer.data[0]
            music = int(serialized_data['music'])
            wake_up_string = serialized_data['wake_up'] 
            wake_up = datetime.fromisoformat(wake_up_string)
            now = datetime.now()
            to_end = (wake_up - now) // timedelta(seconds=1)

            hours = str(int(to_end / 3600))
            minutes = str(int((to_end % 3600) / 60))
            if len(minutes) == 1:
                    minutes = "0" + minutes
            tte = int(hours + minutes)
            return Response({"active": True, "song": music, "to_end": tte})
        else:
            return Response({"active": False})

    def post(self, request, *args, **kwargs):
        if not Night.objects.filter(active=True).exists():
            return Response({'error': 'Neexistuje aktivní noc!'}, status=status.HTTP_404_NOT_FOUND)
        active_night = Night.objects.get(active=True)
        data = {
            'night_id': active_night.id,
            'date': datetime.now(),
            'noise_val': request.data.get('noise_val'),
            'light_val': request.data.get('light_val'),
            'temp': request.data.get('temp'), 
            'hum': request.data.get('hum'),
        }
        serializer_noise = NoiseSerializer(data=data)
        serializer_inside = InsideTempSerializer(data=data)
        serializer_light = LightSerializer(data=data)
        if serializer_noise.is_valid() and serializer_inside.is_valid() and serializer_light.is_valid():
            serializer_noise.save()
            serializer_inside.save()
            serializer_light.save()
            return Response({'status': 'Data inserted successfully!'}, status=status.HTTP_201_CREATED)
        return Response({'error': 'Invalid input data!'}, status=status.HTTP_400_BAD_REQUEST)

#External weather API schduler
from rest_framework import viewsets
import requests
class ExternalWeatherApi(viewsets.ModelViewSet):
    serializer_class = OutsideTempSerializer

    def get_queryset(self):
        data = OutsideTemp.objects.all()
        return data

    def _get_current_data(self):
        active_night = Night.objects.get(active=True)
        url = 'http://api.openweathermap.org/data/2.5/weather?lat='+str(active_night.lat)+'&lon='+str(active_night.lon)+'&appid=6a4fa4ab06be0480008a42e5b6385dfe'
        api_request = requests.get(url)

        try:
            api_request.raise_for_status()
            return api_request.json()
        except:
            return None

    def _get_forcast_data(self):
        active_night = Night.objects.get(active=True)
        url = 'http://api.openweathermap.org/data/2.5/forecast?lat='+str(active_night.lat)+'&lon='+str(active_night.lon)+'&appid=6a4fa4ab06be0480008a42e5b6385dfe'
        api_request = requests.get(url)

        try:
            api_request.raise_for_status()
            return api_request.json()
        except:
            return None

    def save_outside_data(self):
        if Night.objects.filter(active=True).exists():
            active_night = Night.objects.get(active=True)
            weather_f_data = self._get_forcast_data()
            weather_c_data = self._get_current_data()
            if weather_f_data is not None:
                try:
                    outside_value = OutsideTemp.objects.create(night_id=active_night,date=datetime.now(),
                    temp_now=round((weather_c_data['main']['temp']- 273.15), 2),
                    hum_now=weather_c_data['main']['humidity'],
                    pressure_now=weather_c_data['main']['pressure'],
                    pred=weather_f_data['list'][0]['weather'][0]['main'],
                    temp=round((weather_f_data['list'][0]['main']['temp']- 273.15), 2),
                    timestemp=weather_f_data['list'][0]['dt_txt'],
                    pred_next=weather_f_data['list'][1]['weather'][0]['main'],
                    temp_next=round((weather_f_data['list'][1]['main']['temp']- 273.15), 2),
                    timestemp_next=weather_f_data['list'][1]['dt_txt'])
                    outside_value.save()
                except:
                    pass
        else:
            pass

#task that one minute before the alarm sets the music that supposed to be played
class SetSong(viewsets.ModelViewSet):
    def set_song_by_pred(self):
        if not Night.objects.filter(active=True).exists():
            return

        active_night = Night.objects.get(active=True)
        now = datetime.now()
        to_end = (active_night.wake_up - now) // timedelta(seconds=1)
        if 0 <= to_end < 60:
            if 0 <= active_night.pred_review < 2.5:
                Night.objects.filter(active=True).update(music=3)
            elif 2.5 <= active_night.pred_review <= 3.5:
                Night.objects.filter(active=True).update(music=2)
            else:
                Night.objects.filter(active=True).update(music=1)

#task that 15 minutes before planned wake up checks weather and event settings
class SetNightLength(viewsets.ModelViewSet):
    def set_length_night(self):
        #Zjisti zda existuje aktivní noc a případně ji načti
        if not Night.objects.filter(active=True).exists():
            return
        active_night = Night.objects.get(active=True)
        #Zjisti, zda je event v db
        if not CalendarEvent.objects.filter(name=active_night.google).exists():
            return
        event = CalendarEvent.objects.get(name=active_night.google)
        #Zjisti, zda má event TRUE u bad_weather a jestli už nebylo u noci s délkou manipulováno
        if not event.bad_weather or active_night.bad_weather:
            return
        #Zjistit kolik zbývá do konce
        now = datetime.now()
        to_end = (active_night.wake_up - now) // timedelta(seconds=1)
        #Načti poslední hodnotu předpovědi počasí
        last_outside = OutsideTemp.objects.last()
        #Pokud zbývá méně než 15 minut a prší, uprav čas probuzení
        if 60 <= to_end < 900 and last_outside.pred_next == 'Rain':
            new_wake_up = active_night.date + timedelta(hours=8)
            Night.objects.filter(id=active_night.id).update(bad_weather=True, wake_up=new_wake_up)


#task that runs script that predict value
class PredReviewValue(viewsets.ModelViewSet):
    def pred_review(self):
        #zjisti, zda existuje noc, případně ji načti
        if not Night.objects.filter(active=True).exists():
            return
        active_night = Night.objects.get(active=True)
        #pokud již byla predikce udělána, skonči
        if active_night.pred_review:
            return
        #zjisti kolik zbývá do konce měření
        now = datetime.now()
        to_end = (active_night.wake_up - now) // timedelta(seconds=1)
        if 180 <= to_end < 240:
            predReview.main()
        elif 300 <= to_end < 360:
            generateCSV.onenight(active_night.id)