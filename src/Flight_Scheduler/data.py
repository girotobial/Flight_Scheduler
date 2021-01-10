from __future__ import annotations

import os
from dataclasses import field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import sqlalchemy as sqa
from pydantic.dataclasses import dataclass
from sqlalchemy.orm import aliased, registry, relationship, sessionmaker  # type: ignore

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

    def to_dict(self):
        return {"name": self.name, "types": [type_.to_dict() for type_ in self.types]}


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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "icao_code": self.icao_code,
            "name": self.name,
            "propulsion": self.propulsion,
            "family": self.family.name,
        }

    def to_tuple(self) -> Tuple[str, str, int, str]:
        return (self.icao_code, self.name, self.propulsion, self.family.name)


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
    legs: List[Leg] = field(default_factory=list, repr=False)

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

    flights: List[Flight] = field(default_factory=list, repr=False)

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
    legs: List[Leg] = field(default_factory=list, repr=False)

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


class Database:
    def __init__(self, file_path: Union[str, os.PathLike]):
        self.file_path = self._enforce_path(file_path)
        self.engine = sqa.create_engine(f"sqlite://{file_path}")

    @staticmethod
    def _enforce_path(file_path: Union[str, os.PathLike]) -> os.PathLike:
        return Path(file_path)

    def __enter__(self) -> Database:
        Session = sessionmaker(self.engine)
        self.session = Session()
        self.session.begin()
        return self

    def __exit__(self, *args) -> None:
        self.session.close()

    def start(self) -> None:
        self.__enter__()

    def stop(self) -> None:
        self.__exit__()

    def types(
        self, data_type: Optional[str] = "tuple"
    ) -> Union[List[tuple], List[dict], None]:
        """Aircraft types in the database

        Parameters
        ----------
        data_type : str, optional
            output type of the , by default "tuple"

        Returns
        -------
        List[chosen data type]
            contents of the types table

        Raises
        ------
        ValueError
            if data_type is not valid
        """
        results = self.session.query(Type).all()

        DATA_TYPES = ["tuple", "dict"]
        if data_type not in DATA_TYPES:
            raise ValueError(
                f"Unknown data_type '{data_type}', should be one of {DATA_TYPES}"
            )

        if data_type == "tuple":
            return [type_.to_tuple() for type_ in results]

        if data_type == "dict":
            return [type_.to_dict() for type_ in results]

        return None

    def flights(
        self,
        departures: Optional[List[str]] = None,
        destinations: Optional[List[str]] = None,
        airlines: Optional[List[str]] = None,
    ) -> List[Tuple[int, int, str, str]]:
        """Queries the database for a list of flights filtered on the arguments

        Parameters
        ----------
        departures : List[str], optional
            Icao codes of departure airfields e.g ['EGLL'], by default None
        destinations : List[str], optional
            ICAO codes of destination airfields e.g ['LSZH'], by default None
        airlines : List[str], optional
            ICAO codes of the airlines to be filtered on e.g ['BAW'], by default None

        Returns
        -------
        List[Tuple[int, int, str, str]]
            flight id, airline ICAO code, departure ICAO code, destination ICAO code, aircraft type ICAO code
        """
        origin = aliased(Airport, name="origin")
        destination = aliased(Airport, name="destination")
        query = (
            self.session.query(
                Leg.flight_id,
                Airline.icao_code,
                origin.icao_code,
                destination.icao_code,
                Type.icao_code,
            )
            .join("flight")
            .join(origin, origin.id == Leg.origin_id)
            .join(destination, destination.id == Leg.destination_id)
            .join(Airline)
            .join(Aircraft)
            .join(Type)
        )

        if departures is not None:
            query = query.filter(origin.icao_code.in_(departures))
        if destinations is not None:
            query = query.filter(destination.icao_code.in_(destinations))
        if airlines is not None:
            query = query.filter(Airline.icao_code.in_(airlines))  # type: ignore

        return query.all()
