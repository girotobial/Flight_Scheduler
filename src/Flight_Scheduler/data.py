import sqlalchemy as sqa
from pydantic.dataclasses import dataclass
from sqlalchemy.orm import registry  # type: ignore

mapper_registry = registry()


@mapper_registry.mapped
@dataclass
class Aircraft:
    __table__ = sqa.Table(
        "Aircraft",
        mapper_registry.metadata,
        sqa.Column("aircraft", sqa.String, primary_key=True),
        sqa.Column("fullName", sqa.String),
        sqa.Column("aircraftFamily", sqa.String),
        sqa.Column("aircraftClass", sqa.Integer),
        sqa.Column("propulsion", sqa.Integer),
    )

    aircraft: str
    fullName: str
    aircraftFamily: str
    aircraftClass: int
    propulsion: int


@mapper_registry.mapped
@dataclass
class Airline:
    __table__ = sqa.Table(
        "Airline",
        mapper_registry.metadata,
        sqa.Column("airline", sqa.String, primary_key=True),
        sqa.Column("airlineFullName", sqa.String),
    )

    airline: str
    airlineFullName: str


@mapper_registry.mapped
@dataclass
class Airport:
    __table__ = sqa.Table(
        "Airport",
        mapper_registry.metadata,
        sqa.Column("airportCode", sqa.String, primary_key=True),
        sqa.Column("summerTime", sqa.String),
        sqa.Column("winterTime", sqa.String),
        sqa.Column("city", sqa.String),
        sqa.Column("country", sqa.String),
        sqa.Column("fullName", sqa.String),
    )

    airportCode: str
    summerTime: str
    winterTime: str
    city: str
    state: str
    country: str
    fullName: str


@mapper_registry.mapped
@dataclass
class Flight:
    __table__ = sqa.Table(
        "Flight",
        mapper_registry.metadata,
        sqa.Column("flightId", sqa.Integer, primary_key=True),
        sqa.Column("airline", sqa.String, sqa.ForeignKey("Airlines.airline")),
        sqa.Column("flightNum", sqa.Integer),
        sqa.Column("summer", sqa.Integer),
        sqa.Column("year", sqa.Integer),
        sqa.Column("flightComment", sqa.String),
    )

    flightId: int
    airline: str
    flightNum: int
    summer: int
    year: int
    flightComment: str


@mapper_registry.mapped
@dataclass
class Leg:
    __tablename__ = "Leg"
    __table__ = sqa.Table(
        "Leg",
        mapper_registry.metadata,
        sqa.Column("LegID", sqa.Integer, primary_key=True),
        sqa.Column("flightID", sqa.Integer),
        sqa.Column("origin", sqa.String, sqa.ForeignKey("Airport.airportCode")),
        sqa.Column("destination", sqa.String, sqa.ForeignKey("Airport.airportCode")),
        sqa.Column("departureTime", sqa.Integer),
        sqa.Column("arrivalTime", sqa.Integer),
        sqa.Column("duration", sqa.Integer),
        sqa.Column("registration", sqa.String),
        sqa.Column("details", sqa.String),
        sqa.Column("aircraft", sqa.String, sqa.ForeignKey("Aircraft.aircraft")),
    )

    legID: int
    flightId: int
    origin: str
    destination: str
    departureTime: int
    arrivalTime: int
    duration: int
    registration: str
    details: str
    aircraft: str
