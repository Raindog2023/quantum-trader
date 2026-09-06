"""Dashboard app stub"""
from fastapi import FastAPI

app = FastAPI(title="R20 Dashboard")

@app.get("/")
def read_root():
    return {"message": "R20 Quantum Trader Dashboard"}

@app.get("/health")
def health():
    return {"status": "healthy"}
