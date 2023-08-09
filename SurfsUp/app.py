# Import the dependencies required
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

# Defining a function that allows me to call back to the date value that is 12 months before the most recent date in our data
def year_date():
    recent_date= session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    recent_datetime = dt.datetime.strptime(recent_date, '%Y-%m-%d')
    past_datetime = recent_datetime - dt.timedelta(days=365)

    return past_datetime

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
        f"<br/>"
        f"The following routes will provide a JSON list containing the minimum, average and maximum temperatures for a specific station<br/>"
        f"Replace the values for 'start-date' and 'end-date' with a date format of YYYY-MM-DD in order to retrieve the above mentioned values in a JSON list<br/>"
        f"/api/v1.0/start-date<br/>"
        f"/api/v1.0/start-date/end-date<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Using the previously defined function to retrieve the preceiptation data for the past 12 months
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date>year_date()).all()
    
    session.close()

    # Creating a precipitation dictionary to hold dates as keys, and the precipitation as values in the dictionary. The for loop collects this data.
    # A JSON list is returned with date, precipitation data
    prcp_dict = {}

    for date, precip in precipitation:
        prcp_dict[date]=precip
    
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    
    # Querying all the necessary data from the Stations table
    station_list = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    # Beginning a for loop to record each of the values for the respective columns in the Stations table, in the form of a dictionary.
    # A JSON list is then generated presenting all the information for each station
    all_stations=[]

    for record in station_list:
        station_dict = {}
        station_dict["station"]=record[0]
        station_dict["name"]=record[1]
        station_dict["latitude"]=record[2]
        station_dict["longitude"]=record[3]
        station_dict["elevation"]=record[4]
        all_stations.append(station_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def temp():
    
    # Our previous year_date function is called once again to run through similar steps as that of the stations route.
    temp = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date>year_date()).all()
    
    session.close()

    tobs_list = []

    # In the assignment it wasn't specified to present the date and temperature in a key, value format. So they are presented differently here.
    for date, temperature in temp:
        tobs_dict={}
        tobs_dict["date"]=date
        tobs_dict["temp"]=temperature
        tobs_list.append(tobs_dict)
    
    return jsonify(tobs_list)

# Creating both routes that will employ the same function
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
# Creating a function where the end date is an optional addition by the user. By default, the value for the end date is None
def temp_range(start, end=None):
    # Creating a JOIN to collect information requested for a specific station.
    sel = [Station.name, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # Experimenting with a try, except and finally functions to navigate the user to provide dates that exist within our data
    try:
        # Convert start and end to datetime objects
        start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
        if end is not None:
            end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
        
        # Validate if the dates are within the desired range and create lists of the results to later jsonify
        if (end is None or start_date <= end_date):
            # Assigning a variable to the initial query so as to not raise errors later
            query_result = session.query(*sel).filter(Station.station == Measurement.station)
            if end is None:
                start_date_result = query_result.filter(Measurement.date >= start).all()
                result = list(np.ravel(start_date_result))
            else:
                date_range_result = query_result.filter(Measurement.date >= start).\
                    filter(Measurement.date <= end).all()
                result = list(np.ravel(date_range_result))

            return jsonify(result)

        # This else conditional indicated that the dates provided are not ascending from start date to end date
        else:
            return jsonify({"error": "Invalid date range. End date should be after or equal to start date."})

    # When the user renders the date in a format different than what is indicated in the home page, this error message will pop up
    except Exception:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."})
    
    # Using finally to eventually close out the session
    finally:
        session.close()


if __name__ == '__main__':
    app.run(debug=True)
