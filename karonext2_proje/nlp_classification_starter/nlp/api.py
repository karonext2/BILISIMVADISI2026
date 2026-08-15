from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from predict import predict_category

app = FastAPI(title="Kampanya NLP Classification API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CampaignRequest(BaseModel):
    metin: str

@app.get("/")
def root():
    return {"status": "ok", "service": "campaign-classifier"}

@app.post("/classify")
def classify(request: CampaignRequest):
    return predict_category(request.metin)