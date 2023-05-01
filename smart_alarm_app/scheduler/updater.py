from dataclasses import replace
from sched import scheduler
from apscheduler.schedulers.background import BackgroundScheduler
from smart_alarm_app.views import ExternalWeatherApi, SetSong, SetNightLength, PredReviewValue

def start():
    scheduler = BackgroundScheduler()
    #Třídy
    weather = ExternalWeatherApi()
    setPredSong = SetSong()
    setlengthnight = SetNightLength()
    predTonightReview = PredReviewValue()
    #Jednotlivé úkoly
    scheduler.add_job(weather.save_outside_data, "interval", minutes=30,replace_existing=True)
    scheduler.add_job(setlengthnight.set_length_night, "interval", minutes=10,replace_existing=True)
    scheduler.add_job(setPredSong.set_song_by_pred, "interval", minutes=1,replace_existing=True)
    scheduler.add_job(predTonightReview.pred_review, "interval", minutes=1,replace_existing=True)
    scheduler.start()
