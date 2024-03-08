import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
database_engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(database_engine, reflect=True)

# Save a reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available API routes."""
    return (
        f"Welcome to the Hawaii Weather Data API!<br/><br/>"
        f"Available Routes:<br/>"
        f"- Precipitation for the Last Year: <a href=\"/api/v1.0/precipitation\">/api/v1.0/precipitation<a><br/>"
        f"- Active Weather Stations: <a href=\"/api/v1.0/stations\">/api/v1.0/stations<a><br/>"
        f"- Temperature Observations for Station USC00519281: <a href=\"/api/v1.0/tobs\">/api/v1.0/tobs<a><br/>"
        f"- Min, Average & Max Temperatures for a Given Date Range: /api/v1.0/trip/yyyy-mm-dd/yyyy-mm-dd<br/>"
        f"<b>Note:</b> If no end date is provided, the default end date is 2017-08-23.<br/>"
    )

@app.route("/api/v1.0/precipitation")
def get_precipitation():
    """Return a JSON list of precipitation data for the last year."""
    session = Session(database_engine)
    last_year_precipitation = session.query(Measurement.date, func.sum(Measurement.prcp)).\
        filter(Measurement.date >= '2016-08-23').\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()
    session.close()

    precipitation_dict = {date: prcp for date, prcp in last_year_precipitation}
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def get_stations():
    """Return a JSON list of active weather stations."""
    session = Session(database_engine)
    active_stations = session.query(Station.station).distinct().all()
    session.close()

    station_list = [station for (station,) in active_stations]
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def get_tobs():
    """Return a JSON list of temperature observations for the last year."""
    session = Session(database_engine)
    last_year_tobs = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= '2016-08-23', Measurement.station == 'USC00519281').\
        order_by(Measurement.date).all()
    session.close()

    tobs_dict = {date: tobs for date, tobs in last_year_tobs}
    return jsonify(tobs_dict)

@app.route("/api/v1.0/trip/<start_date>/<end_date>")
def get_trip_temps(start_date, end_date='2017-08-23'):
    """Return a JSON list of min, avg, and max temperatures for a given date range."""
    session = Session(database_engine)
    trip_temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
    session.close()

    trip_stats = [{"Min": min_temp, "Average": avg_temp, "Max": max_temp} for min_temp, avg_temp, max_temp in trip_temps]
    return jsonify(trip_stats)

if __name__ == '__main__':
    app.run(debug=True)

