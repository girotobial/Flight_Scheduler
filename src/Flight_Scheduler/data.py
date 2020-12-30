import sqlalchemy as sqa


@sqa.orm.registry.mapped
class Aircraft:
    __tablename__ = "Aircraft"

    aircraft = sqa.Column(sqa.String, primary_key=True)
    fullName = sqa.Column(sqa.String)
    aircraftFamily = sqa.Column(sqa.String)
    aircraftClass = sqa.Column(sqa.Integer)
    propulsion = sqa.Column(sqa.Integer)


@sqa.orm.registry.mapped
class Airline:
    __tablename__ = "Airline"

    airline: str = sqa.Column(sqa.String, primary_key=True)
    airlineFullName: str = sqa.Column(sqa.String)


@sqa.orm.registry.mapped
class Airport:
    __tablename__ = "Airport"

    airportCode: str = sqa.Column(sqa.String, primary_key=True)
    summerTime: str = sqa.Column(sqa.String)
    winterTime: str = sqa.Column(sqa.String)
    city: str = sqa.Column(sqa.String)
    state: str = sqa.Column(sqa.String)
    country: str = sqa.Column(sqa.String)
    fullName: str = sqa.Column(sqa.String)
