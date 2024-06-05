from fastapi import FastAPI
from uvicorn import run
from routs.user import users
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"]
) 

app.include_router(users)
#run(app, host="192.168.1.11", port=8000) #ejecuta en en ip y puerto especifico
#uvicorn app:app --reload abre el server y recarga cada vez que guardamos los cambios