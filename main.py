from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from supabase import create_client
from dotenv import load_dotenv
import os

# .env 読み込み
load_dotenv()

# Supabase 初期化
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "FastAPI is running!"}

@app.post("/save-log")
async def save_log(request: Request):
    try:
        data = await request.json()
        data["user_id"] = "default_user"  # 今は仮で固定（あとでユーザーごとにする）
        res = supabase.table("diet_logs").insert(data).execute()
        print("✅ Saved to Supabase:", res)
        return JSONResponse(content={"status": "saved", "data": data})
    except Exception as e:
        print("❌ Error:", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)

