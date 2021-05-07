# from uuid import uuid4 as uuid
from typing import List

from carbonserver.api.domain.run import RunInterface
from carbonserver.database import schemas, models
from sqlalchemy.orm import Session

# TODO : read https://fastapi.tiangolo.com/tutorial/sql-databases/

"""
Here there is all the method to manipulate the experiment data
"""


class SqlAlchemyRepository(RunInterface):
    def __init__(self, db: Session):
        self.db = db

    def get_db_to_class(self, run: models.Run) -> schemas.Run:
        """Convert a models.Run to a schemas.Run

        :emission: An Run in SQLAlchemy format.
        :returns: An Run in pyDantic BaseModel format.
        :rtype: schemas.Run
        """
        return schemas.Run(
            id=run.id,
            timestamp=run.timestamp,
            emission_id=run.emission_id,
            experiment_id=run.experiment_id,
        )

    def add_save_run(self, run: schemas.RunCreate):
        """Save an Run to the database.

        :emission: An Run in pyDantic BaseModel format.
        """
        db_run = models.Run(
            timestamp=run.timestamp,
            ##emission_id=run.emission_id,
            experiment_id=run.experiment_id,
        )
        self.db.add(db_run)
        self.db.commit()
