from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import model
from config.index import Config
from helpers.model import warmup_models

app = FastAPI()

origins = [Config.FRONTEND_URL, Config.FRONTEND_BUILD]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
)


@app.on_event("startup")
def startup_event():
    warmup_models()


@app.get("/ping")
def read_root():
    return {"message": "pong"}


app.include_router(model.router, prefix="/api")
