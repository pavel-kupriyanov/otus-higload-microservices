from typing import Dict, Optional, Type, Any

from pydantic import BaseModel

from api_gateway.settings.base import ServiceSettings
from api_gateway.settings import settings


class PathInfo(BaseModel):
    path: str
    service: ServiceSettings = settings.MONOLITH
    service_path: str
    request_model: Optional[Any] = None
    response_model: Optional[Any] = None
    authorized: bool = False
    path_params: Dict[str, Type] = {}
    method: str = 'GET'
    status_code: int = 204
    responses: Dict[int, Dict[str, str]] = {
        200: {'description': 'OK'}
    }
