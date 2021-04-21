# from uuid import uuid4 as uuid
from . import models, schemas
from sqlalchemy.orm import Session

# TODO : read https://fastapi.tiangolo.com/tutorial/sql-databases/

"""
Here there is all the method to manipulate the experiment data

"""


def save_experiment(db: Session, experiment: schemas.ExperimentCreate):
    # TODO : save experiment in database and get her ID
    db_experiment = models.Experiment(
        timestamp=experiment.timestamp,
        name=experiment.name,
        description=experiment.description,
        is_active=experiment.is_active,
        project_id=experiment.project_id,
    )
    db.add(db_experiment)
    db.commit()
    db.refresh(db_experiment)
    return db_experiment


def get_one_experiment(experiment_id):
    # TODO : find the experiment in database and return it

    return


def get_experiments_from_experiment(experiment_id):
    # TODO : get experiments from experiment id in database
    return
