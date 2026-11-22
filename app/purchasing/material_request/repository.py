from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from app.purchasing.material_request.models import MaterialRequest, MaterialRequestLine

def get_material_requests(db: Session):
    statement = (
        select(MaterialRequest)
        .options(selectinload(MaterialRequest.lines))
    )
    return db.scalars(statement).all()

def get_material_request_by_id(db: Session, request_id: int):
    statement = (
        select(MaterialRequest)
        .options(selectinload(MaterialRequest.lines))
        .where(MaterialRequest.id == request_id)
    )
    return db.scalar(statement)

def get_material_request_by_document_number(db: Session, document_number: str):
    statement = select(MaterialRequest).where(MaterialRequest.document_number == document_number)
    return db.scalar(statement)

def create_material_request(db: Session, new_request: MaterialRequest, lines_data: list[dict]):
    new_data = MaterialRequest(**new_request)
    for line in lines_data:
        new_data.lines.append(MaterialRequestLine(**line))
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return new_data

def update_material_request(db: Session, update_request: MaterialRequest, lines_data: list[dict] | None = None):
    if lines_data is not None:
        update_request.lines.clear()
        db.flush()
        for line in lines_data:
            update_request.lines.append(MaterialRequestLine(**line))
    db.commit()
    db.refresh(update_request)
    return update_request