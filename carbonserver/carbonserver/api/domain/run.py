import abc
from carbonserver.database import schemas


class RunInterface(abc.ABC):
    @abc.abstractmethod
    def add_save_run(self, run: schemas.RunCreate):
        raise NotImplementedError
