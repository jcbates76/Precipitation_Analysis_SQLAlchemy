# app.py file

# Dependencies and Setup
from unicodedata import name
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

#################################################
# Route - Home Page
#################################################
@app.route("/")
def welcome():
    """Home page."""
    return (
        f"Available Routes:<br/>"
        F"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start_date><br/>"
        f"/api/v1.0/<start_date>/<end_date><br/>"
    )

#################################################
# Route - Precipitation
#################################################
@app.route("/api/v1.0/precipitation")

def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a dictionary of precipitation by date."""
    # Find the latest date in the data set
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()

    # Determine the date to provide 12 months of data
    query_date = dt.datetime.strptime(latest_date[0], '%Y-%m-%d') - dt.timedelta(days = 366)
    
    # Run the query to pull date and preceipitation for the last 12 months.
    results = session.query(measurement.date, measurement.prcp)\
    .filter(measurement.date >= query_date, measurement.prcp >=0)\
    .order_by('date')\
    .all()

    # Close the session    
    session.close()

    # Create a dictionary from the row data of the query
    precipitation = []

    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict['date'] = date
        precipitation_dict['prcp'] = prcp
        precipitation.append(precipitation_dict)

    # Return the dictionary
    return jsonify(precipitation)

#################################################
# Route - Stations
#################################################
@app.route("/api/v1.0/stations")

def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations."""
    # Query a list of stations.
    sel = [measurement.station, station.station, station.name, func.count(measurement.station)]

    station_results = session.query(*sel)\
        .filter(measurement.station == station.station)\
        .group_by(measurement.station)\
        .order_by(func.count(measurement.station).desc())\
        .all()

    # Close the session
    session.close()
    
    # Create a dictionary from the row data of the query
    stations = []

    for station_id_m, station_id_s, station_name, obs_count in station_results:
        station_dict = {}
        station_dict['station_id'] = station_id_m
        station_dict['station_name'] = station_name
        station_dict['obs_count'] = obs_count
        stations.append(station_dict)

    # Return the dictionary
    return jsonify(stations)


#################################################
# Route - Temperature
#################################################
@app.route("/api/v1.0/tobs")
def temperature():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Temperature Observations for Most Active Station"""
    # Run a query to determine the count of temperature observations by station
    station_results = session.query(measurement.station, func.count(measurement.tobs))\
    .group_by(measurement.station)\
    .order_by(func.count(measurement.station).desc()).all()

    # Determine the station ID with the most temperature observations
    active_station = station_results[0].station

    # Find the latest date in the data set
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()

    # Determine the date to provide 12 months of data
    query_date = dt.datetime.strptime(latest_date[0], '%Y-%m-%d') - dt.timedelta(days = 366)

    # Query the database for the tobs data given the date and station criteria
    tobs_results = session.query(measurement.date, measurement.tobs)\
    .filter(measurement.date >= query_date, measurement.station == active_station).all()

    # Close the session
    session.close()
    
    # Create a dictionary from the row data of the query
    tobs_list = []

    for date, tobs in tobs_results:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        tobs_list.append(tobs_dict)

    # Return the dictionary
    return jsonify(tobs_list)

#################################################
# Route - Min/Max/Avg Temp w/ Start Date
#################################################

@app.route("/api/v1.0/<start_date>")
def temp_start_date(start_date):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Create the query to calculate the min, max and average temp observation
    """Calculate the min, max, and average temperature
    the start date is provided by the user, or a 404 if not."""
    start_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs))\
        .filter(measurement.date >= start_date)\
        .all()

    # Close the session
    session.close()

    # Create a dictionary of the results
    start_list = []

    for min, avg, max in start_results:
        start_dict = {}
        start_dict['TMIN'] = min
        start_dict['TAVG'] = avg
        start_dict['TMAX'] = max
        start_list.append(start_dict)

    return jsonify(start_list)

#################################################
# Route - Min/Max/Avg Temp w/ Start & End Date
#################################################

@app.route("/api/v1.0/<start_date>/<end_date>")
def temp_start_end_date(start_date, end_date):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Create the query to calculate the min, max and average temp observation
    """Calculate the min, max, and average temperature
    the start date and end date is provided by the user, or a 404 if not."""
    start_end_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs))\
        .filter(measurement.date >= start_date)\
        .filter(measurement.date <= end_date)\
        .all()

    # Close the session
    session.close()

    # Create a dictionary of the results
    start_end_list = []

    for min, avg, max in start_end_results:
        start_end_dict = {}
        start_end_dict['TMIN'] = min
        start_end_dict['TAVG'] = avg
        start_end_dict['TMAX'] = max
        start_end_list.append(start_end_dict)

    return jsonify(start_end_list)

if __name__ == '__main__':
    app.run(debug=True)
