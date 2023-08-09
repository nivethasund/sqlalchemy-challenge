# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session=Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

def year_date():
    recent_date= session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    past_date = recent_date - dt.timedelta(days=365)

    return(past_date)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date>year_date).all()
    
    session.close()

    prcp_dict = {}

    for date, precip in precipitation:
        prcp_dict[date]=precip
    
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    
    station_list = session.query(Station.station).all()

    session.close()

    all_stations = list(np.ravel(station_list))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def temp():
    
    temp = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date>year_date).all()
    
    session.close()

    tobs_list = []

    for date, temperature in temp:
        tobs_dict={}
        tobs_dict["date"]=date
        tobs_dict["temp"]=temperature
        tobs_list.append(tobs_dict)
    
    return jsonify(tobs_list)

if __name__ == '__main__':
    app.run(debug=True)
