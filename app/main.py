import app.models.user as user
import app.models.transaction as transaction
import app.models.consultation as consultation
import app.models.review as review
import app.models.chat_message as chat_message
from db.session import engine
from fastapi import FastAPI

app=FastAPI()

user.Base.metadata.create_all(bind=engine)
transaction.Base.metadata.create_all(bind=engine)
consultation.Base.metadata.create_all(bind=engine)
review.Base.metadata.create_all(bind=engine)
chat_message.Base.metadata.create_all(bind=engine)