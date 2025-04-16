from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
def root():
    return {"message": "FastAPI is running!"}

@app.post("/save-log")
async def save_log(request: Request):
    try:
        data = await request.json()
        print("📥 Received:", data)
        return JSONResponse(content={"status": "ok", "received": data})
    except Exception as e:
        print("❌ Error in /save-log:", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)

