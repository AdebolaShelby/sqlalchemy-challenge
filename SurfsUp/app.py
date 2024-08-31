# Import the dependencies.
from flask import Flask, jsonify
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
#engine = create_engine("sqlite:///hawaii.sqlite")

# Create path to sqlite
database_path = "../Resources/hawaii.sqlite"

# Create engine to hawaii.sqlite
engine = create_engine(f"sqlite:///{database_path}")





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

recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()


last_date = dt.datetime.strptime(recent_date[0], '%Y-%m-%d')


first_date = session.query(Measurement.date).order_by(Measurement.date).first()


@app.route("/api/v1.0/precipitation")
def precipitation():
    """return This is the precipitation data for the last year"""

    # Calculate the date 1 year ago from the last data point in the database
    #year_ago = last_date - dt.timedelta(days=365)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= '2016-08-23').all()


    # Dict with date as the key and prcp as the value
    dict = {date: prcp for date, prcp in precipitation}
    return jsonify(dict)


@app.route("/api/v1.0/stations")
def stations():
    print("This is the list of stations")
    results = session.query(Station.station).all()

    # Unravel results into a 1D array and convert to a list
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    """return This is the temperature data for the last year"""

    # Calculate the date 1 year ago from last data point
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the primary station for all tobs from the last year
 
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))

    # Return the results
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
def stats(start=None):
    print("This is the temperature data for the given date range")
    """Return TMIN, TAVG, TMAX."""

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        tmin = session.query(func.min(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
        tavg = session.query(func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
        tmax = session.query(func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
        
        # Unravel results into a 1D array and convert to a list
        list_tmin = list(np.ravel(tmin))
        list_tavg = list(np.ravel(tavg))
        list_tmax = list(np.ravel(tmax))
        temps = list_tmin, list_tavg, list_tmax
        return jsonify(temps=temps)
    # calculate TMIN, TAVG, TMAX with start and stop
    tmin_start_end = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    tavg_start_end = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    tmax_start_end = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()


    # Unravel results into a 1D array and convert to a list
    list_tmin_start_end = list(np.ravel(tmin_start_end))
    list_tavg_start_end = list(np.ravel(tavg_start_end))
    list_tmax_start_end = list(np.ravel(tmax_start_end))
    temps = list_tmin_start_end, list_tavg_start_end, list_tmax_start_end
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    print("This is the temperature data for the given date range")
    """Return TMIN, TAVG, TMAX."""

    query = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).\
        group_by(Measurement.date).all()
    
    
    # Select statement
    
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        tmin = session.query(func.min(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
        tavg = session.query(func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
        tmax = session.query(func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
        
        # Unravel results into a 1D array and convert to a list
        list_tmin = list(np.ravel(tmin))
        list_tavg = list(np.ravel(tavg))
        list_tmax = list(np.ravel(tmax))
        temps = list_tmin, list_tavg, list_tmax
        return jsonify(temps=temps)
    # calculate TMIN, TAVG, TMAX with start and stop
    tmin_start_end = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    tavg_start_end = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    tmax_start_end = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()


    # Unravel results into a 1D array and convert to a list
    list_tmin_start_end = list(np.ravel(tmin_start_end))
    list_tavg_start_end = list(np.ravel(tavg_start_end))
    list_tmax_start_end = list(np.ravel(tmax_start_end))
    temps = list_tmin_start_end, list_tavg_start_end, list_tmax_start_end

if __name__ == '__main__':
    app.run()
    