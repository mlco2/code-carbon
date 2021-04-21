# from uuid import uuid4 as uuid
from . import models, schemas
from sqlalchemy.orm import Session

# TODO : read https://fastapi.tiangolo.com/tutorial/sql-databases/

"""
Here there is all the method to manipulate the project data

"""


def save_project(db: Session, project: schemas.ProjectCreate):
    # TODO : save Project in database and get her ID
    db_project = models.Project(
        name=project.name,
        description=project.description,
        team_id=project.team_id,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_one_Project(project_id):
    # TODO : find the Project in database and return it

    return


def get_Projects_from_Project(project_id):
    # TODO : get Projects from Project id in database
    return
