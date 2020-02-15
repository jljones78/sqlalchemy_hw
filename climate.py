import datetime as dt
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# set up db and create session
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# initialize flask
app = Flask(__name__)

# define routes
@app.route("/")

# return all available endpoints
def home():
    return (
        f"available endpoints:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/'start-date'<br/>"
        f"/api/v1.0/'start-date'/'end-date'<br/>"
    )


@app.route("/api/v1.0/precipitation")
# convert the query results to a dict and return as json
def precipitation():
    prcp = (
        session.query(Measurement.prcp, Measurement.date)
        .order_by(Measurement.date)
        .all()
    )
    prcp_df = pd.DataFrame(prcp).dropna()
    precip_dict = prcp_df.to_dict()
    Session.close(session)
    return jsonify(precip_dict)


@app.route("/api/v1.0/stations")
# return a json list of stations from the dataset
def stations():
    stations = session.query(Measurement.station).group_by(Measurement.station).all()
    stations_df = pd.DataFrame(stations)
    stations_dict = stations_df.to_dict()
    Session.close(session)
    return jsonify(stations_dict)


@app.route("/api/v1.0/tobs")
# query for the dates and temperature observations from a year from the last data point
# return a json list of the tobs for the previous year
def tobs():
    last_date = session.query(func.max(Measurement.date)).all()[0][0]
    last_date_dt = dt.datetime.strptime(last_date, "%Y-%m-%d")
    first_date_dt = last_date_dt - dt.timedelta(days=365)
    last12_temp = (
        session.query(Measurement.tobs, Measurement.date)
        .filter(Measurement.date > first_date_dt)
        .order_by(Measurement.date)
        .all()
    )
    last12_temp_df = pd.DataFrame(last12_temp).dropna().set_index("date")
    tobs_dict = last12_temp_df.to_dict()
    Session.close(session)
    return jsonify(tobs_dict)


@app.route("/api/v1.0/<startdate>")
# return a json list of the min temp, avg temp, max temp for all dates greater than and equal to the start date
def start_date(startdate):
    min_avg_max = (
        session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs),
        )
        .filter(Measurement.date >= startdate)
        .all()
    )
    min_avg_max_dict = {
        "date": startdate,
        "tmin": min_avg_max[0][0],
        "tavg": min_avg_max[0][1],
        "tmax": min_avg_max[0][2],
    }
    Session.close(session)
    return jsonify(min_avg_max_dict)


@app.route("/api/v1.0/<startdate>/<enddate>")
# return a json list of the min temp, avg temp, max temp for dates between the start and end date inclusive
def start_end_date(startdate, enddate):
    min_avg_max = (
        session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs),
        )
        .filter(Measurement.date >= startdate)
        .filter(Measurement.date <= enddate)
        .all()
    )
    min_avg_max_dict = {
        "date_range": f"{startdate} - {enddate}",
        "tmin": min_avg_max[0][0],
        "tavg": min_avg_max[0][1],
        "tmax": min_avg_max[0][2],
    }
    Session.close(session)
    return jsonify(min_avg_max_dict)


if __name__ == "__main__":
    app.run(debug=True)
