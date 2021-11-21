#import dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify
from dateutil.relativedelta import relativedelta

#Set up Database
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station


#Create Flask
app = Flask(__name__)

#Define routes
@app.route("/")
def home():
    return (
        f"Welcome to my API! <br>"
        f"Available Routes: <br>"
        f"/api/v1.0/precipitation <br>"
        f"/api/v1.0/stations <br>"
        f"/api/v1.0/tobs <br>"
        f"/api/v1.0/start/ <br>"
        f"/api/v1.0/start/end <br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date_obj = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    target_date = last_date_obj - relativedelta(years = 1)

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= target_date.strftime('%Y-%m-%d')).all()

    session.close()

    prcp_list = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_list.append(prcp_dict)
    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    results = session.query(Measurement.station).group_by(Measurement.station).all()

    session.close()

    stations = list(np.ravel(results))

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date_obj = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    target_date = last_date_obj - relativedelta(years = 1)

    most_active = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).first()

    results = session.query(Measurement.tobs).filter((Measurement.date >= target_date.strftime('%Y-%m-%d')) & (Measurement.station == most_active[0])).all()

    session.close()

    tobs = list(np.ravel(results))

    return jsonify(tobs)

#Return JSON list of min temp, avg temp and max temp for a given start or start-end range
#When given start only, calculate tmin, tavg and tmax for all dates greater than and equal to the start date
@app.route("/api/v1.0/start/<start>")
def start_date(start):
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start).all()

    session.close()

    temp_list = list(np.ravel(results))

    return jsonify(temp_list)


#When given start and end date, calculate tmin, tavg and tmax for dates between the start and end date inclusive
@app.route("/api/v1.0/start/end/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter((Measurement.date >= start) & (Measurement.date <= end)).all()

    session.close()

    temp_list = list(np.ravel(results))

    return jsonify(temp_list)

#Run statement
if __name__ == "__main__":
    app.run(debug=True)