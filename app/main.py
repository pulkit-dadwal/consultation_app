import app.models.user as user
import app.models.transaction as transaction
import app.models.consultation as consultation
import app.models.review as review
import app.models.chat_message as chat_message
import app.models.consultant as consultant
import app.models.wallet as wallet
import app.models.wallet_transaction as wallet_transaction
from app.routers import auth
from app.routers import analytics
from app.routers import consultations
from app.routers import consultants
from app.routers import reviews
from app.routers import transactions
from app.routers import chat
from app.routers import admin
from app.routers import users
from app.routers import wallet_transactions
from app.db.session import engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user.Base.metadata.create_all(bind=engine)
transaction.Base.metadata.create_all(bind=engine)
consultation.Base.metadata.create_all(bind=engine)
review.Base.metadata.create_all(bind=engine)
chat_message.Base.metadata.create_all(bind=engine)
consultant.Base.metadata.create_all(bind=engine)
wallet.Base.metadata.create_all(bind=engine)
wallet_transaction.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(analytics.router)
app.include_router(consultations.router)
app.include_router(consultants.router)
app.include_router(reviews.router)
app.include_router(transactions.router)
app.include_router(chat.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(wallet_transactions.router)