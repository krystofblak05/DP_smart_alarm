import psycopg2
import csv
def main(id):
    conn = psycopg2.connect(database="smart_alarm", user="postgres", password="heslo", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT TO_CHAR(DATE_TRUNC('minute', l.date::timestamp), 'HH24:MI:SS') as datum, n.id, l.light_val, noi.noise_val, ins.temp, ins.hum from smart_alarm_app_night n left join smart_alarm_app_lightvalue l on l.night_id_id = n.id left join smart_alarm_app_noisevalue noi on noi.night_id_id = l.night_id_id and DATE_TRUNC('minute', noi.date::timestamp)=DATE_TRUNC('minute', l.date::timestamp) left join smart_alarm_app_insidetemp ins on ins.night_id_id = l.night_id_id and DATE_TRUNC('minute', ins.date::timestamp)=DATE_TRUNC('minute', l.date::timestamp) where n.id=" + str(id) + " order by l.date ")
    results = cur.fetchall()
    cur.close()
    conn.close()
    with open('static/csv/' + str(id) +'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['datum', 'id_night', 'light', 'noise','temp', 'hum'])
        for row in results:
            writer.writerow(row)
def allnights(user):
    conn = psycopg2.connect(database="smart_alarm", user="postgres", password="heslo", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT n.id, avg(l.light_val) as light, avg(noi.noise_val) as noise, avg(ins.temp) as temp, avg(ins.hum) as hum, (n.wake_up - n.date) as duration, n.drunk, n.tired, n.review_sleep from smart_alarm_app_night n left join smart_alarm_app_lightvalue l on l.night_id_id = n.id left join smart_alarm_app_noisevalue noi on noi.night_id_id = n.id left join smart_alarm_app_insidetemp ins on ins.night_id_id = n.id where n.user = 'admin' group by n.id order by n.id")
    results = cur.fetchall()
    cur.close()
    conn.close()
    with open('static/csv/allnights.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'light', 'noise','temp', 'hum', 'duration', 'drunk', 'tired','review_sleep'])
        for row in results:
            writer.writerow(row)

def onenight(id):
    conn = psycopg2.connect(database="smart_alarm", user="postgres", password="heslo", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT n.id, avg(l.light_val) as light, avg(noi.noise_val) as noise, avg(ins.temp) as temp, avg(ins.hum) as hum, (n.wake_up - n.date) as duration, n.drunk, n.tired, n.review_sleep from smart_alarm_app_night n left join smart_alarm_app_lightvalue l on l.night_id_id = n.id left join smart_alarm_app_noisevalue noi on noi.night_id_id = n.id left join smart_alarm_app_insidetemp ins on ins.night_id_id = n.id where n.id=" + str(id) + " group by n.id order by n.id")
    results = cur.fetchall()
    cur.close()
    conn.close()
    with open('static/csv/onenight.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'light', 'noise','temp', 'hum', 'duration', 'drunk', 'tired','review_sleep'])
        for row in results:
            writer.writerow(row)