from typing import Annotated
from fastapi import APIRouter
from app.schemas.url import URLCreate
from app.db.dependencies import get_url_service
from app.services.url_service import URLService

router = APIRouter()

