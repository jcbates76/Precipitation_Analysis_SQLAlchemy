# app.py file

# Dependencies and Setup
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
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

#################################################
# Route - Precipitation
#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a dictionary of precipitation by date."""
    # Query precipitation by date
    results = session.query(measurement.date, measurement.prcp)\
        .filter(measurement.date >= "2016-08-23").all()

    session.close()

    # Create a dictionary from the row data
    precipitation = []

    for date, prcp in results:
        precipitation_dict = {}
        # ASK - DO I CHANGE THIS TO HAVE THE DATE AS THEY KEY AND JUST RETURN THE prcp AS THE VALUE OF THAT DATE?
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
    results = session.query(measurement.station).group_by(measurement.station)\
        .order_by(measurement.station.desc()).all()

    session.close()

    # Convert list of tuples into a normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


#################################################
# Route - Temperature
#################################################
@app.route("/api/v1.0/tobs")
def temperature():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations."""
    # Query a list of stations.
    tobs_results = session.query(measurement.tobs)\
        .filter(measurement.date >= "2016-08-23", measurement.station == "USC00519281").all()

    session.close()

    # Convert list of tuples into a normal list
    tobs_result_list = list(np.ravel(tobs_results))

    return jsonify(tobs_result_list)





if __name__ == '__main__':
    app.run(debug=True)
