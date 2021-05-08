import abc
from typing import List

from carbonserver.database import models, schemas


class Emissions(abc.ABC):
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
    def get_emissions_from_run(self, run_id) -> List[schemas.Emission]:
        raise NotImplementedError
