from django.urls import path, include
from . import views

#REST
from .views import ArduinoRest

urlpatterns = [
    path('', views.index, name = 'index'),
    path('login',views.login, name='login'),
    path('register',views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('settings', views.settings, name='settings'),
    path('settings/addEvent', views.addEvent, name='addEvent'),
    path('settings/deleteEvent/<int:pk>', views.deleteEvent, name='deleteEvent'),
    path('settings/editEvent/<int:pk>', views.editEvent, name='editEvent'),
    path('history', views.history, name='history'),
    path('night/<int:pk>', views.night, name='night'),
    path('review', views.review, name='review'),
    path('stop-alarm',views.stopalarm,name='stopalarm'),
    path('stop-pin',views.stopPin,name="stopPin"),
    path('pincode', views.pincode, name='pincode'),
    path('csvtry', views.csvTry, name="csvtry"),
    path('address', views.predefAddress, name="address"),
    #REST
    path('api-auth/', include('rest_framework.urls')),
    path('arduino', ArduinoRest.as_view(), name='active_rest')
]