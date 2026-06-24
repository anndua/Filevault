from fastapi import FastAPI,HTTPException

from routers.auth import router as auth_router


app=FastAPI()

@app.get("/")
def home():
    return {"message":"hi"}

app.include_router(auth_router)

