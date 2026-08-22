from fastapi import FastAPI

app = FastAPI()

@app.get("/resident/{resident_id}")
def get_resident(resident_id: str):
    return {"resident_id": resident_id, "status": "stub - not yet implemented"}