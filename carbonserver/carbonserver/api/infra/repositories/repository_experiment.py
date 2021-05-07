# from uuid import uuid4 as uuid
from typing import List

from carbonserver.api.domain.experiment import ExperimentInterface
from carbonserver.database import schemas, models
from sqlalchemy.orm import Session

# TODO : read https://fastapi.tiangolo.com/tutorial/sql-databases/

"""
Here there is all the method to manipulate the experiment data
"""


class SqlAlchemyRepository(Experiment):
    def __init__(self, db: Session):
        self.db = db

    def get_db_to_class(self, experiment: models.Experiment) -> schemas.Experiment:
        """Convert a models.Experiment to a schemas.Experiment

        :experiment: An Experiment in SQLAlchemy format.
        :returns: An Experiment in pyDantic BaseModel format.
        :rtype: schemas.Experiment
        """
        return schemas.Experiment(
            id=experiment.id,
            timestamp=experiment.timestamp,
            name=experiment.name,
            description=experiment.description,
            isactive=experiment.energy_consumed,
            country_name=experiment.country_name,
            country_iso_code=experiment.country_iso_code,
            region=experiment.region,
            on_cloud=experiment.on_cloud,
            cloud_provider=experiment.cloud_provider,
            cloud_region=experiment.cloud_region,
            # emission_id=experiment.emission_id,
            project_id=experiment.project_id,
        )

    def save_experiment(self, experiment: schemas.ExperimentCreate):
        # TODO : save experiment in database and get her ID
        db_experiment = models.Experiment(
            timestamp=experiment.timestamp,
            name=experiment.name,
            description=experiment.description,
            country_name=experiment.country_name,
            country_iso_code=experiment.country_iso_code,
            region=experiment.region,
            on_cloud=experiment.on_cloud,
            cloud_provider=experiment.cloud_provider,
            cloud_region=experiment.cloud_region,
            is_active=experiment.is_active,
            # emission_id=experiment.emission_id,
            project_id=experiment.project_id,
        )
        self.db.add(db_experiment)
        self.db.commit()
        self.db.refresh(db_experiment)
        return db_experiment

    def get_one_experiment(self, experiment_id):
        """Find the experiment in database and return it

        :experiment_id: The id of the experiment to retreive.
        :returns: An Experiment in pyDantic BaseModel format.
        :rtype: schemas.Experiment
        """
        e = (
            self.db.query(models.Experiment)
            .filter(models.Experiment.id == experiment_id)
            .first()
        )
        if e is None:
            return None
        else:
            return self.get_db_to_class(e)

    # def get_experiments_from_experiment(self, experiment_id):
    # TODO : get experiments from experiment id in database
    #    return True

    def get_experiment_from_emission(self, emission_id) -> List[schemas.Experiment]:
        """Find the experiment from an emission in database and return it

        :emission_id: The id of the emission to retreive experiment from.
        :returns: An Experiment in pyDantic BaseModel format.
        :rtype: List[schemas.Experiment]
        """
        res = self.db.query(models.Experiment).filter(
            models.Experiment.emission_id == emission_id
        )
        if res.first() is None:
            return []
        else:
            # Convert the table of models.Emission to a table of schemas.Emission
            experiments = []
            for e in res:
                experiment = self.get_db_to_class(e)
                experiments.append(experiment)
            return experiments


class InMemoryRepository(Experiment):
    def __init__(self):
        self.experiments: List = []
        self.id: int = 0

    def save_experiment(self, experiment: schemas.ExperimentCreate):
        self.experiments.append(
            models.Experiment(
                id=self.id + 1,
                timestamp=experiment.timestamp,
                name=experiment.name,
                description=experiment.description,
                country_name=experiment.country_name,
                country_iso_code=experiment.country_iso_code,
                region=experiment.region,
                on_cloud=experiment.on_cloud,
                cloud_provider=experiment.cloud_provider,
                cloud_region=experiment.cloud_region,
                is_active=experiment.is_active,
                # emission_id=experiment.emission_id,
                project_id=experiment.project_id,
            )
        )

    def get_one_experiment(self, experiment_id: int) -> schemas.Experiment:
        experiment = self.experiments[0]
        return schemas.Experiment(
            id=experiment.id,
            timestamp=experiment.timestamp,
            name=experiment.name,
            description=experiment.description,
            country_name=experiment.country_name,
            country_iso_code=experiment.country_iso_code,
            region=experiment.region,
            on_cloud=experiment.on_cloud,
            cloud_provider=experiment.cloud_provider,
            cloud_region=experiment.cloud_region,
            is_active=experiment.is_active,
            # emission_id=experiment.emission_id,
            project_id=experiment.project_id,
        )

    def get_experiment_from_emission(self, emission_id) -> List[schemas.Experiment]:
        experiments = []
        for experiment in self.experiments:
            experiments.append(
                schemas.Experiment(
                    id=experiment.id,
                    timestamp=experiment.timestamp,
                    name=experiment.name,
                    description=experiment.description,
                    country_name=experiment.country_name,
                    country_iso_code=experiment.country_iso_code,
                    region=experiment.region,
                    on_cloud=experiment.on_cloud,
                    cloud_provider=experiment.cloud_provider,
                    cloud_region=experiment.cloud_region,
                    is_active=experiment.is_active,
                    # emission_id=experiment.emission_id,
                    project_id=experiment.project_id,
                )
            )
        return experiments
