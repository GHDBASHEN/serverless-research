from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from cloudpredict.predict import predict_latency

app = FastAPI(title='CloudPredict API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MigrationRequest(BaseModel):
    source: str
    target: str
    exec_mean: float
    mem_mean: float
    runtime: str = 'python'

@app.post('/predict')
def predict(req: MigrationRequest):
    return predict_latency(
        req.source, req.target,
        req.exec_mean, req.mem_mean, req.runtime
    )
