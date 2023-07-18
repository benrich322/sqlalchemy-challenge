# Import the dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime, timedelta
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn = engine.connect()

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
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
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>"
        #f"/api/v1.0/<start>/<end>"
    )
@app.route("/api/v1.0/precipitation")
def names():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a dict of the precipitation analysis"""

    # Create empty list for the loop
    date_list = []
    # Create a list of all the measurement dates
    for row in session.query(measurement.date).all():
        date_value = row[0]
        date_list.append(date_value)

    # Find most recent date in list
    most_recent_date = max(date_list, key=lambda x: x)

    # Calculate the date one year from the last date in data set
    most_recent_date_format = datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_from_last_date = most_recent_date_format + timedelta(days=-365)
    result = one_year_from_last_date.strftime("%Y-%m-%d")

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date > result).\
    order_by(measurement.date).all()

    # Convert the query results from your precipitation analysis to a dictionary using date as the key and prcp as the value.
    precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        precipitation.append(precipitation_dict)

    # Close Session
    session.close()

    # Return the JSON representation of the dictionary
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
     # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations from the dataset"""

    # Create empty list for the loop
    session_list = []

    # Create a list of all the stations
    for row in session.query(station.station).all():
        station_value = row[0]
        session_list.append(station_value)

    # Close Session
    session.close()

    # Return the JSON representation of the list
    return jsonify(session_list)

@app.route("/api/v1.0/tobs")
def most_active_station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature observations for the previous year for the most active station"""    

    # Find the most active station
    most_active_stations = session.query(measurement.station,func.count(measurement.tobs)).\
    group_by(measurement.station).\
    order_by(func.count(measurement.tobs).desc()).all()

    # Identify the id of the most active station
    most_active_station_id = most_active_stations[0][0]

    # Create empty list for the loop
    date_list_most_active_station = []

    # Query the dates for the most active station
    date_most_active_station = session.query(measurement.date).\
    filter(measurement.station == most_active_station_id).all()

    # Create a list of the dates for the most active station
    for row in date_most_active_station:
        date_value = row[0]
        date_list_most_active_station.append(date_value)

    # Find most recent date
    most_recent_date = max(date_list_most_active_station, key=lambda x: x)

    # Calculate the date one year from the last date in data set.
    most_recent_date_format = datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_from_last_date = most_recent_date_format + timedelta(days=-365)
    result = one_year_from_last_date.strftime("%Y-%m-%d")

    # Perform a query to retrieve the temperature observations for the previous year for the most active station
    temperature_observation = session.query(measurement.station, measurement.date, measurement.tobs).\
    filter(measurement.date > result, measurement.station == most_active_station_id).\
    order_by(measurement.date).all()

    # Create empty list for the loop
    most_active_station_list = []

    # Create a list of the dates for the temperature observations for the previous year
    for row in temperature_observation:
        row_list = list(row)
        most_active_station_list.append(row_list)

    # Close Session
    session.close()

    # Return the JSON representation of the list
    return jsonify(most_active_station_list)

@app.route("/api/v1.0/<start>")
def test(start_date):
     
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of the minimum temperature, the average temperature,
    and the maximum temperature for a specified start range, or a 404 if not."""

    date_values = session.query(measurement.date, func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).\
    filter(measurement.date == start_date).\
    group_by(measurement.date).all()

    date_list_test = []
    for row in date_list_test:
        search_term = row["date"].replace(" ", "")

        if search_term == start_date:
            return jsonify(row)

    return jsonify({"error": "date not found."}), 404
#@app.route("/api/v1.0/<start>/<end>")

if __name__ == "__main__":
    app.run(debug=True)