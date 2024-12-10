from fastapi import FastAPI
from app import auth, predict, metrics, retrieve

app = FastAPI()

# Include routers from other modules
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(predict.router, prefix="/predict", tags=["Prediction"])
app.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
app.include_router(retrieve.router, prefix="/data", tags=["Data Retrieval"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the MLOps FastAPI project!"}