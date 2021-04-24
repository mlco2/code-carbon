"""

Based on https://kernelpanic.io/the-modern-way-to-call-apis-in-python


"""
from schema import EmissionCreate, ExperimentCreate
from httpx import AsyncClient
import logging
from datetime import datetime

IFCONFIG_URL = "https://localhost:8000/"
LOGGER = logging.getLogger(__name__)


class ApiClient(AsyncClient):
    """
    This class call the Code Carbon API
    Note : The project, team and organization must have been created in the interface.
    """

    def __init__(self, project_id, api_key):
        """
        :project_id: ID of the existing project
        :api_ley: Code Carbon API_KEY
        """
        super().__init__(base_url=IFCONFIG_URL)
        self.project_id = project_id
        self.api_key = api_key
        self.create_experiment()

    async def save_emission(self, emission: EmissionCreate):
        try:
            payload = EmissionCreate.get_dict()
            r = self.put(data=payload)
            assert r.status_code == 201
        except Exception as e:
            LOGGER.error(e, exc_info=True)
            return False
        return True

    async def _create_experiment(self):
        """
        Create the experiment for project_id
        # TODO : Allow to give an existing experiment_id
        """
        try:
            experiment = ExperimentCreate(
                timestamp=datetime.now(),
                name="Random Name Run",
                description="Rando description",
                is_active=True,
                project_id=self.project_id,
            )
            payload = experiment.to_dict()
            r = self.put(data=payload)
            assert r.status_code == 200
            experiment_id = r["experiment_id"]
        except Exception as e:
            LOGGER.error(e, exc_info=True)
            return None
        return experiment_id

    async def close_experiment(self):
        """
        Tell the API that the experiment has ended.
        """
        pass
