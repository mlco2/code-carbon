from fastapi import APIRouter, Path, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import get_token_header, get_db
from database import crud_projects
from database.schemas import ProjectCreate


router = APIRouter(
    dependencies=[Depends(get_token_header)],
)


projects_temp_db = []


@router.put("/project", tags=["projects"])
def add_project(project: ProjectCreate, db: Session = Depends(get_db)):
    # Remove next line when DB work
    projects_temp_db.append(project.dict())
    crud_projects.save_project(db, project)


@router.get("/project/{project_id}", tags=["projects"])
async def read_project(
    project_id: str = Path(..., title="The ID of the project to get")
):
    project = crud_projects.get_one_project(project_id)
    if project_id is False:
        raise HTTPException(status_code=404, detail="Item not found")
    return project


@router.get("/projects/{project_id}", tags=["projects"])
async def read_experiment_projects(
    experiment_id: str = Path(..., title="The ID of the experiment to get")
):
    experiment_projects = crud_projects.get_projects_from_experiment(experiment_id)
    # Remove next line when DB work
    experiment_projects = projects_temp_db
    return experiment_projects
