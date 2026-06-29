from fastapi import FastAPI,HTTPException

from routers.auth import router as auth_router
from routers.files import router as file_router




app=FastAPI()

@app.get("/")
def home():
    return {"message":"hi"}

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Auth"],
)
app.include_router(file_router)



