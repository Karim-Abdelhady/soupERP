from fastapi import FastAPI
from database.database import engine, Base
from app.systemadministration.users.router import router as usersRouter
from app.systemadministration.suppliers.router import router as suppliersRouter
from app.systemadministration.customers.router import router as customersRouter
from app.systemadministration.employees.router import router as EmployeesRouter
from app.systemadministration.auth.router import router as AuthorizationRouter
from app.systemadministration.sessions.router import router as SessionsRouter
from app.systemadministration.system_settings.router import router as SystemSettingsRouter
from app.systemadministration.currencies.router import router as CurrencyRouter
from app.systemadministration.uom.router import router as UomRouter
from app.inventory.items.router import router as ItemRouter

Base.metadata.create_all(bind=engine)
app=FastAPI()

app.include_router(EmployeesRouter)
app.include_router(customersRouter)
app.include_router(suppliersRouter)
app.include_router(usersRouter)
app.include_router(AuthorizationRouter)
app.include_router(SessionsRouter)
app.include_router(SystemSettingsRouter)
app.include_router(CurrencyRouter)
app.include_router(UomRouter)
app.include_router(ItemRouter)
