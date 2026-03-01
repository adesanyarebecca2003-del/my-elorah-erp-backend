from fastapi import FastAPI, Request, HTTPException
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.accounts import router as accounts_router
from app.api.journal import router as journal_router
from app.api.inventory_purchase import router as inventory_purchase_router
from app.api.inventory_sale import router as inventory_sale_router
from app.api.inventory_bulk_upload import router as inventory_bulk_upload_router
from app.api.inventory_sale_return import router as inventory_sale_return_router
from app.api.inventory_adjustment import router as inventory_adjustment_router
from app.api.inventory_category import router as inventory_category_router
from app.api.inventory_product import router as inventory_product_router
from app.api.inventory_valuation import router as inventory_valuation_router
from app.api.ledger import router as ledger_router
from app.api.trial_balance import router as trial_balance_router
from app.api.income_statement import router as income_statement_router
from app.api.accounting_periods import router as accounting_periods_router
from app.api.balance_sheet import router as balance_sheet_router
from app.api.reports import router as reports_router
from app.api.auth import router as auth_router
from app.api.admin_seed import router as admin_seed_router

app = FastAPI(
    title="Elorah ERP",
    swagger_ui_parameters={
        "persistAuthorization": True
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://elorahresources-frontend.vercel.app",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

bearer_scheme = HTTPBearer()

app.include_router(accounts_router)
app.include_router(journal_router)
app.include_router(inventory_purchase_router)
app.include_router(inventory_sale_router)
app.include_router(inventory_bulk_upload_router)
app.include_router(inventory_sale_return_router)
app.include_router(inventory_adjustment_router)
app.include_router(inventory_category_router)
app.include_router(inventory_product_router)
app.include_router(inventory_valuation_router)
app.include_router(ledger_router)
app.include_router(trial_balance_router)
app.include_router(income_statement_router)
app.include_router(accounting_periods_router)
app.include_router(balance_sheet_router)
app.include_router(reports_router)
app.include_router(auth_router)
app.include_router(admin_seed_router)

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.get("/health")
def health_check():
    return {"status": "El'Orah Resources Enterprise is Active"}