from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.invoice_route import router as invoice_router
from app.api.routes.clover_route import router as clover_router
from app.api.routes.sales_data_extraction_route import router as sales_data_extraction_router
from app.api.routes.revenue_analyzer_route import router as revenue_analyzer_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(invoice_router, prefix="/api/invoice", tags=["Invoice"])
app.include_router(clover_router, prefix="/api/clover", tags=["Clover API"])
app.include_router(sales_data_extraction_router, prefix="/api/sales", tags=["Sales Data Extraction API"])
app.include_router(revenue_analyzer_router, prefix="/api/revenue", tags=["Revenue Analysis API"])
