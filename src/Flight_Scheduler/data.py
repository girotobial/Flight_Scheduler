from __future__ import annotations

from dataclasses import field
from typing import List

import sqlalchemy as sqa
from pydantic.dataclasses import dataclass
from sqlalchemy.orm import registry, relationship  # type: ignore

mapper_registry = registry()


@mapper_registry.mapped
@dataclass
class Family:
    """A group of aircraft types e.g Lockheed Constellation"""

    __table__ = sqa.Table(
        "Family",
        mapper_registry.metadata,
        sqa.Column("id", sqa.Integer, primary_key=True),
        sqa.Column("name", sqa.String),
    )

    id: int = field(init=False, repr=False)
    name: str
    types: List[Type] = field(default_factory=list, repr=False)

    __mapper_args__ = {
        "properties": {"types": relationship("Type", back_populates="family")}
    }


@mapper_registry.mapped
@dataclass
class Type:
    __table__ = sqa.Table(
        "Type",
        mapper_registry.metadata,
        sqa.Column("id", sqa.Integer, primary_key=True),
        sqa.Column("icao_code", sqa.String),
        sqa.Column("name", sqa.String),
        sqa.Column("family_id", sqa.Integer, sqa.ForeignKey("Family.id")),
        sqa.Column("propulsion", sqa.Integer),
    )

    id: int = field(init=False, repr=False)
    icao_code: str
    name: str
    family_id: int = field(repr=False)
    propulsion: int

    family: Family

    __mapper_args__ = {
        "properties": {"family": relationship("Family", back_populates="types")}
    }


@mapper_registry.mapped
@dataclass
class Aircraft:
    __table__ = sqa.Table(
        "Aircraft",
        mapper_registry.metadata,
        sqa.Column("id", sqa.Integer, primary_key=True),
        sqa.Column("registration", sqa.String),
        sqa.Column("type_id", sqa.Integer, sqa.ForeignKey("Type.id")),
    )

    id: int = field(init=False, repr=False)
    registration: str
    type_id: int = field(repr=False)

    type_: Type
    legs: List[Leg] = field(default_factory=list)

    __mapper_args__ = {
        "properties": {
            "type_": relationship("Type"),
            "legs": relationship("Leg"),
        }
    }


@mapper_registry.mapped
@dataclass
class Airline:
    __table__ = sqa.Table(
        "Airline",
        mapper_registry.metadata,
        sqa.Column("id", sqa.Integer, primary_key=True),
        sqa.Column("icao_code", sqa.String),
        sqa.Column("name", sqa.String),
    )

    id: int = field(init=False, repr=False)
    icao_code: str
    name: str

    flights: List[Flight] = field(default_factory=list)

    __mapper_args__ = {
        "properties": {
            "flights": relationship("Flight", back_populates="airline"),
        }
    }


@mapper_registry.mapped
@dataclass
class Airport:
    __table__ = sqa.Table(
        "Airport",
        mapper_registry.metadata,
        sqa.Column("id", sqa.Integer, primary_key=True),
        sqa.Column("icao_code", sqa.String),
        sqa.Column("summer_timezone", sqa.String),
        sqa.Column("winter_timezone", sqa.String),
        sqa.Column("city", sqa.String),
        sqa.Column("state", sqa.String),
        sqa.Column("country", sqa.String),
        sqa.Column("name", sqa.String),
    )

    id: int = field(init=False, repr=False)
    icao_code: str
    name: str
    summer_timezone: str
    winter_timezone: str
    city: str
    state: str
    country: str


@mapper_registry.mapped
@dataclass
class Flight:
    __table__ = sqa.Table(
        "Flight",
        mapper_registry.metadata,
        sqa.Column("id", sqa.Integer, primary_key=True),
        sqa.Column("number", sqa.Integer),
        sqa.Column("summer", sqa.Integer),
        sqa.Column("year", sqa.Integer),
        sqa.Column("comment", sqa.String),
        sqa.Column("airline_id", sqa.String, sqa.ForeignKey("Airline.id")),
    )

    id: int = field(init=False, repr=False)
    number: int
    summer: int
    year: int
    comment: str
    airline_id: int = field(repr=False)

    airline: Airline
    legs: List[Leg] = field(default_factory=list)

    __mapper_args__ = {
        "properties": {
            "airline": relationship("Airline", back_populates="flights"),
            "legs": relationship("Leg", back_populates="flight"),
        }
    }


@mapper_registry.mapped
@dataclass
class Leg:
    __table__ = sqa.Table(
        "Leg",
        mapper_registry.metadata,
        sqa.Column("id", sqa.Integer, primary_key=True),
        sqa.Column("flight_id", sqa.Integer, sqa.ForeignKey("Flight.id")),
        sqa.Column("departure_time", sqa.Integer),
        sqa.Column("arrival_time", sqa.Integer),
        sqa.Column("duration", sqa.Integer),
        sqa.Column("details", sqa.String),
        sqa.Column("origin_id", sqa.Integer, sqa.ForeignKey("Airport.id")),
        sqa.Column("destination_id", sqa.Integer, sqa.ForeignKey("Airport.id")),
        sqa.Column("aircraft_id", sqa.Integer, sqa.ForeignKey("Aircraft.id")),
    )

    id: int = field(init=False, repr=False)
    flight_id: int = field(repr=False)
    origin_id: int = field(repr=False)
    destination_id: int = field(repr=False)
    departure_time: int
    arrival_time: int
    duration: int
    details: str
    aircraft_id: int = field(repr=False)

    origin: Airport
    destination: Airport
    aircraft: Aircraft
    flight: Flight = field(repr=False)

    __mapper_args__ = {
        "properties": {
            "flight": relationship("Flight", back_populates="legs"),
            "origin": relationship("Airport", foreign_keys="Leg.origin_id"),
            "destination": relationship("Airport", foreign_keys="Leg.destination_id"),
            "aircraft": relationship("Aircraft", back_populates="legs"),
        }
    }
