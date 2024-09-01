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

# Create path to sqlite
database_path = "../Resources/hawaii.sqlite"

# Create engine to hawaii.sqlite
engine = create_engine(f"sqlite:///{database_path}")


# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

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
        f"<strong>Welcome to the Hawaii Climate Analysis API!</strong><br/>"
        f"<i>Available Routes:</i>"
        f"<li>/api/v1.0/precipitation</li>"
        f"<li>/api/v1.0/stations</li>"
        f"<li>/api/v1.0/tobs</li>"
        f"<li>/api/v1.0/temp/<start></li>"
        f"<li>/api/v1.0/temp/<start>/<end></li>"
    )

recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
last_date = dt.datetime.strptime(recent_date[0], '%Y-%m-%d')
first_date = session.query(Measurement.date).order_by(Measurement.date).first()


@app.route("/api/v1.0/precipitation")
def precipitation():
    """return This is the precipitation data for the last year"""

    # Calculate the date 1 year ago from the last data point in the database
    year_ago = last_date - dt.timedelta(days=365)
    #recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

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
def start_date(start):

    # set start date
    start_date = '2016-10-23'

    # create session link from Python to the DB
    session = Session(engine)

    # query TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    session.close()

    # crate a json list of the results
    tmin_tavg_tmax = []
    for min, avg, max in results:
        tmin_tavg_tmax_dict = {}
        tmin_tavg_tmax_dict["Min Temp"] = min
        tmin_tavg_tmax_dict["Avg Temp"] = avg
        tmin_tavg_tmax_dict["Max Temp"] = max
        tmin_tavg_tmax.append(tmin_tavg_tmax_dict)


    return jsonify(tmin_tavg_tmax)



@app.route("/api/v1.0/temp/<start>/<end>")
def start_end_date(start, end):
    
        # set start date
        start_date= '2016-08-23'
        end_date = '2017-08-23'
    
        # create session link from Python to the DB
        session = Session(engine)
    
        # query TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).\
            filter(Measurement.date <= end_date).all()
        session.close()
    
        # crate a json list of the results
        tmin_tavg_tmax = []
        for min, avg, max in results:
            tmin_tavg_tmax_dict = {}
            tmin_tavg_tmax_dict["Min Temp"] = min
            tmin_tavg_tmax_dict["Avg Temp"] = avg
            tmin_tavg_tmax_dict["Max Temp"] = max
            tmin_tavg_tmax.append(tmin_tavg_tmax_dict)
    
    
        return jsonify(tmin_tavg_tmax)


if __name__ == "__main__":
    app.run(debug=True)



