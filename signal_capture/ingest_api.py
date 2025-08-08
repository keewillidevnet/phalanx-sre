from fastapi import FastAPI, UploadFile, File, Form
from pathlib import Path
from datetime import datetime
import shutil

app = FastAPI(title="Phalanx Ingest API")

ART_DIR = Path("artifacts")
ART_DIR.mkdir(exist_ok=True)

@app.post("/upload")
async def upload_pcap(node: str = Form(...), hop: int = Form(...), pcap: UploadFile = File(...)):
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    dest = ART_DIR / f"{ts}_hop{hop}_{node}.pcapng"
    with dest.open("wb") as f:
        shutil.copyfileobj(pcap.file, f)
    return {"status":"ok","saved":str(dest)}
