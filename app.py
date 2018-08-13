from flask import Flask, render_template, redirect, jsonify
import datetime as dt
import numpy as np
import pandas as pd
import time 
from datetime import timedelta
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
#################################################
# Database Setup
#################################################
engine = create_engine('sqlite:///Resources/hawaii.sqlite', connect_args={'check_same_thread': False})
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
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
    """Welcome to Surfs Up."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"<br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")

def precipitation():
    #Query for the dates and temperature observations from the last year.
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    # Find the start date of last year
    start_date = last_date - dt.timedelta(days=365)
    # Formatting the start date
    start_date = start_date.strftime("%Y-%m-%d")
    
    #Query to retreive the precipitation from last year
    prcp=session.query(measurement.date,measurement.prcp).\
            filter(measurement.date>=start_date).\
            order_by(measurement.date.desc()).all()
    
    # Create a list to store each date as a dictionary
    precip_list=[]
    for x in prcp:
        precip_value={"Date": x[0], "Precipitation": x[1]}
        precip_list.append(precip_value)
        
    # Return the jsonify list
    return jsonify(precip_list)

@app.route("/api/v1.0/stations")
def stations_list():
    print("Retrieving the list of stations ............")
    # Query to retrieve the station id and station name
    station_result = session.query(station.name,station.station).all()

    # Create a list to store the result in dictionary format
    station_list = []
    for stat in station_result:
        stat_id={"Name":stat[0], "Station": stat[1]}
        station_list.append(stat_id)

    # Return the jsonify list
    return jsonify(station_list)

### /api/v1.0/tobs

#### Return a json list of Temperature Observations (tobs) for the previous year

@app.route("/api/v1.0/tobs")
def temp_prev_year():
    print("Retrieving Temperature Observation for the previous year")
    
    # Retrieve the start and end dates
    # Query to retrieve the last date in Measurement DB
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    # Converting end date into datetime format
    end_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')

    # Calculate the first date based on the end date
    first_date="%d-%d-%d"%(end_date.year-1,end_date.month,end_date.day)
    # Convert the start date into datetime format
    start_date=dt.datetime.strptime(first_date, '%Y-%m-%d').strftime("%Y-%m-%d")
    # Convert the end date into  datetime format
    end_date=end_date.strftime("%Y-%m-%d")

    # Use the start date and end date calculated to query for the previous year data.
    prev_year_temp=session.query(measurement.date,measurement.tobs).\
                    filter(measurement.date>=start_date, measurement.date<=end_date).\
                    order_by(measurement.date.desc()).all()

    # Create a list to store the temp in dictionary format
    temp_list = []
    for row in prev_year_temp:
        temp = {"Date":row[0], "Temp": row[1]}
        temp_list.append(temp)

    # Return the jsonify list
        return jsonify(temp_list)

### /api/v1.0/start and /api/v1.0/start/end

#### -Return a json list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

#### -When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

#### -When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>")
def temp_analysis_start(start):
    print("Retrieving the Temperature of hawaii from the start date")
    # Query to get the tmin, tavg and tmax starting from the start date
    temp_calc_results = session.query(func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)).\
                            filter(measurement.date>=start).order_by(measurement.date.desc()).all()
        
    # Converting the tuple to a list
    temp_calc_results = list(np.ravel(temp_calc_results))
    
    # Storing the result in a dictionary list
    temp_result1=[{"Start Date": start , "TMIN":temp_calc_results[0],\
                  "TAVG" : temp_calc_results[1] , "TMAX" : temp_calc_results[2]}]
    
    # Return the jsonify list
    return jsonify(temp_result1)

@app.route("/api/v1.0/<start>/<end>")
def temp_analysis_start_end(start,end):
    print("Retrieving the Temperature from the given start date to the end date.")
    # Query to get the tmin, tavg and tmax starting from the start date
    temp_calc_results = session.query(func.min(measurement.tobs),func.avg(measurement.Tobs),func.max(measurement.Tobs)).\
                            filter(measurement.date>=start,measurement.date<=end).\
                            order_by(measurement.date.desc()).all()
        
    # Converting the series to a list
    temp_calc_results = list(np.ravel(temp_calc_results))
    
    # Storing the result in a dictionary list
    temp_result2=[{"Start Date": start , "End Date" : end , "TMIN":temp_calc_results[0],\
                  "TAVG" : temp_calc_results[1] , "TMAX" : temp_calc_results[2]}]
    
    # Return the jsonify list
    return jsonify(temp_result2)
if __name__ == '__main__':
    app.run(debug=True)