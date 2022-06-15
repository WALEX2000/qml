from fastapi import FastAPI, Body
import pickle
from mlblocks import MLPipeline
import pathlib
import pandas as pd

pipelinePath = str(pathlib.Path(__file__).parent.resolve()) + '/model.pipeline'
with open(pipelinePath, 'rb') as pipelineFile:
    mlPipeline : MLPipeline = pickle.load(pipelineFile)

app = FastAPI()

@app.get("/")
def home_get():
    return {"The ML Model is": "LIVE!"}

@app.post("/")
async def predictML(payload: dict = Body(...)):
    X = pd.DataFrame([list(payload.values())], columns=list(payload.keys()))

    try:
        output = mlPipeline.predict(X)
    except:
        return {'ERROR': 'Invalid input structure'}

    return {'Result': str(output)}