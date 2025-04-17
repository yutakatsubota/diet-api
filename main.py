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

from fastapi import Query
from io import BytesIO
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

# generate graph
@app.get("/generate-graph")
def generate_graph(days: int = Query(default=7, description="何日分のデータをグラフにするか")):
    try:
        since = (datetime.now() - timedelta(days=days)).date().isoformat()
        res = supabase.table("diet_logs").select("*").gte("date", since).order("date").execute()
        logs = res.data

        if not logs or len(logs) < 2:
            return {"status": "error", "message": "グラフを作るにはデータが少なすぎます"}

        df = pd.DataFrame(logs)
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)

        plt.figure(figsize=(8, 4))
        plt.plot(df.index, df["weight"], marker="o", label="体重(kg)")
        if "body_fat" in df.columns and df["body_fat"].notnull().any():
            plt.plot(df.index, df["body_fat"], marker="s", label="体脂肪(%)")
        plt.xlabel("日付")
        plt.ylabel("数値")
        plt.title("体重と体脂肪の推移")
        plt.legend()
        plt.grid(True)

        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format="png")
        buf.seek(0)

        today = datetime.now().strftime("%Y-%m-%d-%H%M")
        file_name = f"chart-{today}.png"
        supabase.storage.from_("charts").upload(file_name, buf.read(), {"content-type": "image/png"})

        url = f"{SUPABASE_URL}/storage/v1/object/public/charts/{file_name}"
        return {"status": "ok", "url": url}

    except Exception as e:
        print("❌ Error in /generate-graph:", str(e))
        return {"status": "error", "message": str(e)}

