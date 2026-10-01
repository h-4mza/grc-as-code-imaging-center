from fastapi import FastAPI

app = FastAPI(
    title="GRC API",
    description="API de pilotage GRC as-code (EBIOS, ISO 27001, NIS2)",
    version="1.0.0",
)

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API GRC-as-code"}

@app.get("/risks")
def get_risks():
    return []

@app.get("/controls")
def get_controls():
    return []
