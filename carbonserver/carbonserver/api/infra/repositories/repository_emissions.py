# from uuid import uuid4 as uuid
from typing import List

from carbonserver.api.domain.emission import Emission
from carbonserver.database import models
from carbonserver.api import schemas

from sqlalchemy.orm import Session

"""
The emissions are stored in the database by this repository class.
The emission repository is implemented to facilitate tests & the switch of database backend.
It relies on an abstract repository which exposes an interface of signatures shared by all repository implementations.

"""


class SqlAlchemyRepository(Emission):
    def __init__(self, db: Session):
        self.db = db

    def get_db_to_class(self, emission: models.Emission) -> schemas.Emission:
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

    def add_save_emission(self, emission: schemas.EmissionCreate):
        """Save an emission to the database.

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
        self.db.add(db_emission)
        self.db.commit()

    def get_one_emission(self, emission_id) -> schemas.Emission:
        """Find the emission in database and return it

        :emission_id: The id of the emission to retreive.
        :returns: An Emission in pyDantic BaseModel format.
        :rtype: schemas.Emission
        """
        e = (
            self.db.query(models.Emission)
            .filter(models.Emission.id == emission_id)
            .first()
        )
        if e is None:
            return None
        else:
            return self.get_db_to_class(e)

    def get_emissions_from_experiment(self, experiment_id) -> List[schemas.Emission]:
        """Find the emissions from an experiment in database and return it

        :experiment_id: The id of the experiment to retreive emissions from.
        :returns: An Emission in pyDantic BaseModel format.
        :rtype: List[schemas.Emission]
        """
        res = self.db.query(models.Emission).filter(
            models.Emission.experiment_id == experiment_id
        )
        if res.first() is None:
            return []
        else:
            # Convert the table of models.Emission to a table of schemas.Emission
            emissions = []
            for e in res:
                emission = self.get_db_to_class(e)
                emissions.append(emission)
            return emissions


class InMemoryRepository(Emission):
    def __init__(self):
        self.emissions: List = []
        self.id: int = 0

    def add_save_emission(self, emission: schemas.EmissionCreate):
        self.emissions.append(
            models.Emission(
                id=self.id + 1,
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
        )

    def get_db_to_class(self, emission: models.Emission) -> schemas.Emission:
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

    def get_one_emission(self, emission_id) -> schemas.Emission:
        first_emission = self.emissions[0]
        return schemas.Emission(
            id=first_emission.id,
            timestamp=first_emission.timestamp,
            duration=first_emission.duration,
            emissions=first_emission.emissions,
            energy_consumed=first_emission.energy_consumed,
            country_name=first_emission.country_name,
            country_iso_code=first_emission.country_iso_code,
            region=first_emission.region,
            on_cloud=first_emission.on_cloud,
            cloud_provider=first_emission.cloud_provider,
            cloud_region=first_emission.cloud_region,
            experiment_id=first_emission.experiment_id,
        )

    def get_emissions_from_experiment(self, experiment_id) -> List[schemas.Emission]:
        print(len(self.emissions))
        stored_emissions = [
            stored_emission
            for stored_emission in self.emissions
            if stored_emission.experiment_id == experiment_id
        ]
        emissions: List[schemas.Emission] = []
        for emission in stored_emissions:
            emissions.append(self.get_db_to_class(emission))
        return emissions
