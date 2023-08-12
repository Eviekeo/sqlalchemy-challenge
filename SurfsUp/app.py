# import dependencies
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Set up the database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(autoload_with=engine)


# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
app = Flask(__name__)

#################################################
# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"        
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date one year from the last date in data set.
    prior_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    PY_prcp = session.query(measurement.date, measurement.prcp).filter(measurement.date >= prior_year).order_by(measurement.date).all()

    # Close the session
    session.close()
    
    # Store the query results in a dictionary
    precip = {date: prcp for date, prcp in PY_prcp}

    return jsonify(precip)
   

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve a list of all the stations
    stations = session.query(station.station).all()

    # Close the session
    session.close()   

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(stations)) 

    return jsonify(all_stations)   

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve dates and temperature observations of the most-active station for the previous year of data
    most_active = session.query(measurement.tobs).filter(measurement.date >= '2016, 8, 18').\
    filter(measurement.station == 'USC00519281').order_by(measurement.tobs).all()

    # Close the session
    session.close()   

    # Convert list of tuples into normal list
    most_active_list = list(np.ravel(most_active)) 

    return jsonify(most_active_list)   

@app.route("/api/v1.0/<start>")  
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Create a start variable with the accepted format
    start = dt.datetime.strptime(start, "%m-%d-%Y")

    # Perform a query to filter based on the start
    start_temps = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
    filter(measurement.date >= start).all()
  
    # Close the session
    session.close()  

    # Convert list of tuples into normal list
    s_temps = list(np.ravel(start_temps))
    return jsonify(s_temps)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Create a start and end variable with the accepted format
    start = dt.datetime.strptime(start, "%m-%d-%Y")
    end = dt.datetime.strptime(end, "%m-%d-%Y")

    # Perform a query to filter based on the start and end dates
    s_e_temps = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
    filter(measurement.date >= start).filter(measurement.date <= end).all()
    
    # Convert list of tuples into normal list
    temps_list = list(np.ravel(s_e_temps))
    
    # Close the session
    session.close()  

    return jsonify(temps_list)


   
# Define main behaviour
if __name__ == "__main__":
   app.run(debug=True)