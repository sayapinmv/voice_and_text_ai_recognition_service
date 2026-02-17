from src.module.logger.logger import Logger
from fastapi.responses import JSONResponse
from fastapi import FastAPI


app = FastAPI()


class TranscriptionsController:

    def __init__(self, logger: Logger):
        pass

    @app.get('/transcriptions/id')
    def get_transcription(self):
        pass