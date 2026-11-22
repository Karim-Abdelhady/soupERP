from fastapi import APIRouter, Depends
from app.purchasing.material_request import service
from typing import List
from app.purchasing.material_request.schemas import RequestResponse, RequestCreate, RequestUpdate
from sqlalchemy.orm import Session
from database.database import get_db

router = APIRouter()

@router.get("/materialrequests/", response_model = List[RequestResponse], tags = ["Material Request"])
def get_material_requests(db: Session = Depends(get_db)):
    return service.get_material_requests(db)

@router.get("/materialrequests/{request_id}", response_model= RequestResponse, tags = ["Material Request"])
def get_material_request_by_id(request_id: int, db: Session = Depends(get_db)):
    return service.get_material_request_by_id(db, request_id)

@router.post("/materialrequests/draft", response_model = RequestResponse, tags = ["Material Request"])
def create_material_request(new_request: RequestCreate, db: Session = Depends(get_db)):
    return service.create_material_request(db, new_request)

@router.post("/materialrequests/submit/{request_id}", response_model = RequestResponse, tags = ["Material Request"])
def submit_material_request(request_id: int, db:Session = Depends(get_db)):
    return service.submit_material_request(db, request_id)

@router.post("/materialrequests/cancel/{request_id}", response_model= RequestResponse, tags = ["Material Request"])
def cancel_material_request(request_id: int, db: Session = Depends(get_db)):
    return service.cancel_material_request(db, request_id)

@router.patch("/materialrequests/{request_id}", response_model = RequestResponse, tags = ["Material Request"])
def update_material_request(request_id: int, update_request: RequestUpdate, db: Session = Depends(get_db)):
    return service.update_material_request(db, request_id, update_request)