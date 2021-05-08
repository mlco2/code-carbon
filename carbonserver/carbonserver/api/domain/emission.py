import abc
from typing import List

from carbonserver.database import models
from carbonserver.api import schemas


class Emission(abc.ABC):
    @abc.abstractmethod
    def add_save_emission(self, emission: schemas.EmissionCreate):
        raise NotImplementedError

    @abc.abstractmethod
    def get_db_to_class(self, emission: models.Emission) -> schemas.Emission:
        raise NotImplementedError

    @abc.abstractmethod
    def get_one_emission(self, emission_id) -> schemas.Emission:
        raise NotImplementedError

    @abc.abstractmethod
    def get_emissions_from_experiment(self, experiment_id) -> List[schemas.Emission]:
        raise NotImplementedError
