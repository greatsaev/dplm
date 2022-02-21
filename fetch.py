import json
import requests
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta  # python-dateutil pkg

import sqlite3

db_file = "stringency.db"

start_date = datetime.strptime('2022-01-01', '%Y-%m-%d').date()
countries = ["RUS", "ARG", "LKA", "USA", "MEX", "ITA", "CHL", "CZE", "SWE", "ISR"]
# print(date.today()-relativedelta(days=1))
current_date = date.today() - relativedelta(days=2) # 2-3 days latency in source


def create_db():
    # TODO: check if db file exists
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    for i in countries:
        c.execute(
            '''CREATE TABLE IF NOT EXISTS %s 
            ([date] TEXT, [confirmed] INTEGER, [deaths] INTEGER, [stringency_actual] REAL, [stringency] REAL)''' % i)
    conn.commit()
    conn.close()


def make_request(country, request_date):
    url = f"https://covidtrackerapi.bsg.ox.ac.uk/api/v2/stringency/actions/{country}/{request_date}"
    response = requests.get(url)
    if 'Data unavailable' in response.text:
        return 1
    else:
        return response.json()["stringencyData"]


create_db()
while current_date >= start_date:
    print(current_date)

    for i in countries:
        # TODO: Check in db before request
        try:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            # Update by country:
            c.execute('SELECT * FROM %s WHERE date=?' % i, (current_date,))
            result = c.fetchone()
            if result is None:
                print(f"{current_date} not found in {i}")
                data = make_request(i, current_date)
                if data == 1:
                    print("No data")
                else:
                    c.execute(
                        'INSERT INTO %s(date,confirmed,deaths,stringency_actual,stringency) VALUES (?,?,?,?,?)' % i,
                        (data["date_value"], data["confirmed"], data["deaths"], data["stringency_actual"], data["stringency"]))
            else:
                print(f"{current_date} already in db for {i}")
            conn.commit()
            conn.close()
        except Exception as e:
            print("Error " + str(e))

        #url = f"https://covidtrackerapi.bsg.ox.ac.uk/api/v2/stringency/actions/{i}/{current_date}"
        #response = requests.get(url)
        #data = response.json()["stringencyData"]
        #print(json.dumps(response.json()["stringencyData"], indent=4))
        # try:
        #     conn = sqlite3.connect(db_file)
        #     c = conn.cursor()
        #     date = data["date_value"]
        #     confirmed = data["confirmed"]
        #     deaths = data["deaths"]
        #     stringency_actual = data["stringency_actual"]
        #     stringency = data["stringency"]
        #     c.execute('SELECT * FROM all_in_one WHERE date=? AND code=?', (date, i))
        #     result = c.fetchone()
        #     if result is None:
        #         c.execute(
        #             'INSERT INTO all_in_one(date,code,confirmed,deaths,stringency_actual,stringency) VALUES (?,?,?,?,?,?)',
        #             (date, i, confirmed, deaths, stringency_actual, stringency))
        #     else:
        #         print("already in db")
        #     conn.commit()
        #     conn.close()
        # except Exception as e:
        #     print(e)

    current_date = current_date - relativedelta(days=1)  # go to previous day
# print(response.json()['data'])
# print(json.dumps(response.json(), indent=4))
