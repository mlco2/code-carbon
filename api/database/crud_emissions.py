# from uuid import uuid4 as uuid
from . import models, schemas
from sqlalchemy.orm import Session
from typing import List


"""
Here there is all the method to manipulate the emissions data
Inspired by https://fastapi.tiangolo.com/tutorial/sql-databases/
# TODO:
 - Récupérationd d'une / des émission(s)
 - Pouvoir créer plusieurs émissions d'un coup
 - Créer crud_experiment, project, team, organizations
"""


def db_to_class(emission: models.Emission) -> schemas.Emission:
    """Convert a models.Emission to a schemas.Emission

    :emission: An Emission in SQLAlchemy format.
    :returns: An Emission in pyDantic BaseModel format.
    :rtype: schemas.Emission
    """
    return schemas.Emission(
        id=emission.id,
        timestamp=emission.timestamp,
        duration=emission.duration,
        emissions=emission.emissions,
        energy_consumed=emission.energy_consumed,
        country_name=emission.country_name,
        country_iso_code=emission.country_iso_code,
        region=emission.region,
        on_cloud=emission.on_cloud,
        cloud_provider=emission.cloud_provider,
        cloud_region=emission.cloud_region,
        experiment_id=emission.experiment_id,
    )


def save_emission(db: Session, emission: schemas.EmissionCreate):
    """Save an emission to the database.

    :db: : A SQLAlchemy session.
    :emission: An Emission in pyDantic BaseModel format.
    """
    db_emission = models.Emission(
        timestamp=emission.timestamp,
        duration=emission.duration,
        emissions=emission.emissions,
        energy_consumed=emission.energy_consumed,
        country_name=emission.country_name,
        country_iso_code=emission.country_iso_code,
        region=emission.region,
        on_cloud=emission.on_cloud,
        cloud_provider=emission.cloud_provider,
        cloud_region=emission.cloud_region,
        experiment_id=emission.experiment_id,
    )
    db.add(db_emission)
    db.commit()


def get_one_emission(db: Session, emission_id) -> schemas.Emission:
    """Find the emission in database and return it

    :db: : A SQLAlchemy session.
    :emission_id: The id of the emission to retreive.
    :returns: An Emission in pyDantic BaseModel format.
    :rtype: schemas.Emission
    """
    e = db.query(models.Emission).filter(models.Emission.id == emission_id).first()
    if e is None:
        return None
    else:
        return db_to_class(e)


def get_emissions_from_experiment(db: Session, experiment_id) -> List[schemas.Emission]:
    """Find the emissions from an experiment in database and return it

    :db: : A SQLAlchemy session.
    :experiment_id: The id of the experiment to retreive emissions from.
    :returns: An Emission in pyDantic BaseModel format.
    :rtype: List[schemas.Emission]
    """
    res = db.query(models.Emission).filter(
        models.Emission.experiment_id == experiment_id
    )
    if res.first() is None:
        return None
    else:
        # Convert the table of models.Emission to a table of schemas.Emission
        emissions = []
        for e in res:
            emission = db_to_class(e)
            emissions.append(emission)
        return emissions
