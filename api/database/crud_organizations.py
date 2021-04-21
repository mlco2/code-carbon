# from uuid import uuid4 as uuid
from . import models, schemas
from sqlalchemy.orm import Session

# TODO : read https://fastapi.tiangolo.com/tutorial/sql-databases/

"""
Here there is all the method to manipulate the project data

"""


def save_organization(db: Session, organization: schemas.OrganizationCreate):
    # TODO : save Organization in database and get her ID
    db_organization = models.Organization(
       name=organization.name,
        description=organization.description,
        team_id=organization.organization_id,
    )
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    return db_organization


def get_one_organization(organization_id):
    # TODO : find the Organization in database and return it

    return


def get_Team_from_Organizations(organization_id):
    # TODO : get Organization from team id in database
    return
