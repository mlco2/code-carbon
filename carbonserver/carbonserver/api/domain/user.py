import abc

from carbonserver.api import schemas


class User(abc.ABC):
    @abc.abstractmethod
    def create_user(self, user: schemas.UserCreate):
        raise NotImplementedError

    @abc.abstractmethod
    def get_user_by_id(self, user_id: int):
        raise NotImplementedError

    @abc.abstractmethod
    def list_users(self):
        raise NotImplementedError
