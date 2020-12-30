import sqlalchemy as sqa


@sqa.orm.registry.mapped
class Aircraft:
    __tablename__ = "Aircraft"

    aircraft = sqa.Column(sqa.String, primary_key=True)
    fullName = sqa.Column(sqa.String)
    aircraftFamily = sqa.Column(sqa.String)
    aircraftClass = sqa.Column(sqa.Integer)
    propulsion = sqa.Column(sqa.Integer)
