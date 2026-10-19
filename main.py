from fastapi import FastAPI
from database.database import engine, Base
from app.users.router import router as usersRouter
from app.suppliers.router import router as suppliersRouter
from app.customers.router import router as customersRouter
from app.employees.router import router as EmployeesRouter
from app.auth.router import router as AuthorizationRouter
from app.sessions.router import router as SessionsRouter

Base.metadata.create_all(bind=engine)
app=FastAPI()

app.include_router(EmployeesRouter)
app.include_router(customersRouter)
app.include_router(suppliersRouter)
app.include_router(usersRouter)
app.include_router(AuthorizationRouter)
app.include_router(SessionsRouter)
