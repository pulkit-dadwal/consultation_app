import app.models.user as user
import app.models.transaction as transaction
import app.models.consultation as consultation
import app.models.review as review
import app.models.chat_message as chat_message
import app.models.consultant as consultant
from app.routers import auth
from app.routers import analytics
from app.routers import consultations
from app.routers import consultants
from app.routers import reviews
from app.routers import transactions
from app.routers import chat
from app.db.session import engine
from fastapi import FastAPI

app = FastAPI()

user.Base.metadata.create_all(bind=engine)
transaction.Base.metadata.create_all(bind=engine)
consultation.Base.metadata.create_all(bind=engine)
review.Base.metadata.create_all(bind=engine)
chat_message.Base.metadata.create_all(bind=engine)
consultant.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(analytics.router)
app.include_router(consultations.router)
app.include_router(consultants.router)
app.include_router(reviews.router)
app.include_router(transactions.router)
app.include_router(chat.router)