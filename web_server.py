from flask import Flask, render_template, session, redirect
from flask_wtf import FlaskForm
from wtforms import DateField
from wtforms.validators import DataRequired
from wtforms import validators, SubmitField

from datetime import date, datetime

import sqlite3

db_file = "stringency.db"

app = Flask(__name__)
app.config['SECRET_KEY'] = '#$%^&*'

# Get last date available in DB:
conn = sqlite3.connect(db_file)
c = conn.cursor()
c.execute('SELECT * FROM all_in_one WHERE date=(SELECT max(date) FROM all_in_one);')
last_date_str = c.fetchone()[0]
last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
conn.close()
requested_date = last_date_str


class DateForm(FlaskForm):
    dt = DateField('Pick a Date', format='%Y-%m-%d', default=last_date, validators=(validators.DataRequired(),))
    submit = SubmitField('Submit')


@app.route('/', methods=['post', 'get'])
def home():
    global requested_date
    form = DateForm()
    if form.validate_on_submit():
        session['date'] = str(form.dt.data)
        requested_date = str(form.dt.data)
        #return redirect('show_all')
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute('SELECT * FROM all_in_one WHERE date=? ORDER BY deaths', (requested_date,))
        data = c.fetchall()
        conn.close()
        return render_template('index.html', date=str(date.today()), db_date=last_date, form=form, data=data)

    try:

        conn = sqlite3.connect(db_file)
        c = conn.cursor()
       # c.execute('SELECT * FROM all_in_one WHERE date=? ORDER BY deaths', (last_date_str,))
        c.execute('SELECT * FROM all_in_one WHERE date=? ORDER BY deaths', (requested_date,))
        data = c.fetchall()
        conn.close()
        return render_template('index.html', date=str(date.today()), db_date=last_date, form=form, data=data)
    except Exception as e:
        print(e)


@app.route('/show_all')
def show_all():
    try:
        if session['date'] is not None:
            print('333')
        print('11')
        request_date = session['date']
        print(request_date)
        print('111')
        print(type(request_date))

        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute('SELECT * FROM all_in_one WHERE date=? ORDER BY deaths', (session['date'],))
        data = c.fetchall()
        conn.close()
        return render_template('all_in_one.html', data=data)
    except Exception as e:
        print(e)


# @app.route('/show_all')
# def show_all():
#     try:
#         conn = sqlite3.connect(db_file)
#         c = conn.cursor()
#         c.execute('SELECT * FROM all_in_one ORDER BY date DESC')
#         data = c.fetchall()
#         conn.close()
#         return render_template('all_in_one.html', data=data)
#     except Exception as e:
#         print(e)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, threaded=True)
