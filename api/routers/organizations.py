from fastapi import APIRouter, Path, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import get_token_header, get_db
from database import crud_organizations
from database.schemas import OrganizationCreate


router = APIRouter(
    dependencies=[Depends(get_token_header)],
)


organizations_temp_db = []


@router.put("/organization", tags=["organizations"])
def add_organization(organization: OrganizationCreate, db: Session = Depends(get_db)):
    # Remove next line when DB work
    organizations_temp_db.append(organization.dict())
    crud_organizations.save_organization(db, organization)


@router.get("/organization/{organization_id}", tags=["organizations"])
async def read_organization(
    organization_id: str = Path(..., title="The ID of the organization to get")
):
    organization = crud_organizations.get_one_organization(organization_id)
    if organization_id is False:
        raise HTTPException(status_code=404, detail="Item not found")
    return organization


@router.get("/organizations/{organization_id}", tags=["organizations"])
async def read_teams_organizations(
    team_id: str = Path(..., title="The ID of the team to get")
):
    team_organizations = crud_organizations.get_Team_from_Organizations(team_id)
    # Remove next line when DB work
    team_organizations = organizations_temp_db
    return team_organizations
