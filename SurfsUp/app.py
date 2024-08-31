# Import the dependencies.
from flask import Flask, jsonify, request
import datetime as dt
import numpy as np
import pandas as pd

# Import the SQL Alchemy dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
#engine = create_engine("sqlite:///Resources/hawaii.sqlite")
engine = create_engine("sqlite:///hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)
#Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`

Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end"
    )

recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
print(recent_date)

last_date = dt.datetime.strptime(recent_date[0], '%Y-%m-%d')
print(last_date)

first_date = session.query(measurement.date).order_by(measurement.date).first()
print(first_date)

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("This is the precipitation data for the last year")

    # Calculate the date 1 year ago from the last data point in the database
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    print(recent_date)

    # Query for the date and precipitation for the last year
    precipitation = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= '2016-08-23').all()
    print(precipitation)

    # Dict with date as the key and prcp as the value
    dict = {date: prcp for date, prcp in precipitation}
    return jsonify(dict)


@app.route("/api/v1.0/stations")
def stations():
    print("This is the list of stations")
    results = session.query(station.station).all()

    # Unravel results into a 1D array and convert to a list
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    print("This is the temperature data for the last year")

    # Calculate the date 1 year ago from last data point
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the primary station for all tobs from the last year
    results = session.query(measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(measurement.date >= prev_year).all()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))

    # Return the results
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    print("This is the temperature data for the given date range")
    """Return TMIN, TAVG, TMAX."""
    
    # Select statement
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
            filter(measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run()
    