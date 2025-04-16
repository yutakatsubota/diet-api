from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
def root():
    return {"message": "FastAPI is running!"}

@app.post("/save-log")
async def save_log(request: Request):
    data = await request.json()
    print("📥 Received:", data)
    return JSONResponse(content={"status": "ok", "received": data})
