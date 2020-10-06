import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_
from flask import Flask, jsonify


engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement
station = Base.classes.station


app = Flask(__name__)
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    result =  session.query(measurement.date, measurement.prcp).order_by(measurement.date).all()
    
    prcp_date_list = []

    for date, prcp in result:
        new_dict = {}
        new_dict[date] = prcp
        prcp_date_list.append(new_dict)

    session.close()

    return jsonify(prcp_date_list)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = {}

    result = session.query(station.station, station.name).all()
    for s,name in result:
        stations[s] = name

    session.close()
 
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def TOBS():
    session = Session(engine)
    last_year = session.query(measurement.date).order_by(measurement.date.desc()).first()
    previous_year = (dt.datetime.strptime(last_year[0],'%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    result = session.query(measurement.date, measurement.tobs).filter(measurement.date >= previous_year).order_by(measurement.date).all()

    tobs_list = []

    for date, tobs in result:
        new_dict = {}
        new_dict[date] = tobs
        tobs_list.append(new_dict)

    session.close()

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temp_start(start):
    """TMIN, TAVG, and TMAX per date starting from a starting date.
    Args:
        start (string): A date string in the format %Y-%m-%d  
    Returns:
        TMIN, TAVE, and TMAX
    """

    session = Session(engine)
    return_list = []
    result =   session.query(measurement.date,func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(measurement.date >= start).group_by(measurement.date).all()

    for date, min, avg, max in result:
        new_dict = {}
        new_dict["Date"] = date
        new_dict["TMIN"] = min
        new_dict["TAVG"] = avg
        new_dict["TMAX"] = max
        return_list.append(new_dict)

    session.close()    

    return jsonify(return_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_range(start,end):
    """TMIN, TAVG, and TMAX per date for a date range.
    Args:
        start (string): A date string in the format %Y-%m-%d
        end (string): A date string in the format %Y-%m-%d   
    Returns:
        TMIN, TAVE, and TMAX
    """

    session = Session(engine)
    return_list = []
    result =   session.query(measurement.date,func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(and_(measurement.date >= start, measurement.date <= end)).group_by(measurement.date).all()

    for date, min, avg, max in result:
        new_dict = {}
        new_dict["Date"] = date
        new_dict["TMIN"] = min
        new_dict["TAVG"] = avg
        new_dict["TMAX"] = max
        return_list.append(new_dict)

    session.close()    

    return jsonify(return_list)

if __name__ == '__main__':
    app.run(debug=True)