import sqlalchemy as sqa
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Aircraft(Base):
    __tablename__ = "Aircraft"

    aircraft = sqa.Column(sqa.String, primary_key=True)
    fullName = sqa.Column(sqa.String)
    aircraftFamily = sqa.Column(sqa.String)
    aircraftClass = sqa.Column(sqa.Integer)
    propulsion = sqa.Column(sqa.Integer)


class Airline(Base):
    __tablename__ = "Airline"

    airline = sqa.Column(sqa.String, primary_key=True)
    airlineFullName = sqa.Column(sqa.String)


class Airport(Base):
    __tablename__ = "Airport"

    airportCode = sqa.Column(sqa.String, primary_key=True)
    summerTime = sqa.Column(sqa.String)
    winterTime = sqa.Column(sqa.String)
    city = sqa.Column(sqa.String)
    state = sqa.Column(sqa.String)
    country = sqa.Column(sqa.String)
    fullName = sqa.Column(sqa.String)


class Flight(Base):
    __tablename__ = "Flight"

    flightId = sqa.Column(sqa.Integer, primary_key=True)
    airline = sqa.Column(sqa.String, sqa.ForeignKey("Airlines.airline"))
    flightNum = sqa.Column(sqa.Integer)
    summer = sqa.Column(sqa.Integer)
    year = sqa.Column(sqa.Integer)
    flightComment = sqa.Column(sqa.String)


class Leg(Base):
    __tablename__ = "Leg"

    legID = sqa.Column(sqa.Integer, primary_key=True)
    flightId = sqa.Column(sqa.Integer)
    origin = sqa.Column(sqa.String, sqa.ForeignKey("Airport.airportCode"))
    destination = sqa.Column(sqa.String, sqa.ForeignKey("Airport.airportCode"))
    departureTime = sqa.Column(sqa.Integer)
    arrivalTime = sqa.Column(sqa.Integer)
