from fastapi import APIRouter
from app.api_v1.router_records import router as records_router
from app.api_v1.router_projects import router as projects_router
from app.api_v1.router_update_partial_record import router as update_record
from app.api_v1.router_predict import router as predict_router

router = APIRouter()
router.include_router(router=projects_router, prefix="/projects")
router.include_router(router=records_router, prefix="/records")
router.include_router(router=update_record, prefix="/update_record")
router.include_router(router=predict_router, prefix="/predict")
