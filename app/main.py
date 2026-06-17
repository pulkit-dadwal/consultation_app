from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.base import Base
from app.db.session import engine

# Import all models so Base.metadata is fully populated before create_all.
# Every model must be imported here even if not used directly — otherwise
# its table won't be created.
import app.models.user
import app.models.consultant
import app.models.consultant_request
import app.models.consultation
import app.models.consultation_message
import app.models.transaction
import app.models.wallet_transaction
import app.models.review
import app.models.chat_message

from app.routers import (
    auth,
    admin,
    users,
    consultants,
    consultations,
    reviews,
    transactions,
    wallet_transactions,
)
from app.routers.websocket import router as websocket_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Single create_all is enough — all models share the same Base so one call
# creates every table. Calling it once per model was redundant.
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(consultants.router)
app.include_router(consultations.router)
app.include_router(reviews.router)
app.include_router(transactions.router)
app.include_router(wallet_transactions.router)
app.include_router(websocket_router)