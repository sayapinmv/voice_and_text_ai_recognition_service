import json
from typing import Optional

from fastapi.responses import FileResponse, Response, JSONResponse
from fastapi import APIRouter, UploadFile, Form, File, status

from src.module.logger.logger import Logger
from src.module.service.transcription.service import TranscriptionService
from src.module.entity.transcription_entity import TranscriptionType
from src.module.controller.models import GetTranscriptionResponse
from src.module.service.transcription.model import TranscriptionDto


class TranscriptionsController:
    def __init__(self,
                 logger: Logger,
                 transcription_service: TranscriptionService):

        self._logger = logger
        self._transcription_service = transcription_service

        self._router = APIRouter(prefix="/transcriptions", tags=["Transcriptions"])
        self._add_routes()

    def _add_routes(self):
        self._router.add_api_route(path="/{id}", methods=["GET"], endpoint=self._get)
        self._router.add_api_route(path="/", methods=["POST"], endpoint=self._create)
        self._router.add_api_route(path="/{id}", methods=["DELETE"], endpoint=self._remove)
        self._router.add_api_route(path='/{id}/file', methods=["GET"], endpoint=self._get_transcription_file)
        self._router.add_api_route(path='/{id}/file/origin', methods=["GET"], endpoint=self._get_origin_file)


    @property
    def router(self):
        return self._router

    async def _get(self, id: int):
        self._logger.info(f"Getting transcription {id}")
        entity = self._transcription_service.get(id)
        response = GetTranscriptionResponse(
            id=entity.id,
            transcription_type=entity.transcription_type,
            transcription_name=entity.transcription_name,
            origin_name=entity.origin_name
        )

        return JSONResponse(response.model_dump_json())

    async def _get_transcription_file(self, id: int):
        entity = self._transcription_service.get(id)
        print(entity.transcription_filepath)
        return FileResponse(entity.transcription_filepath, status_code=status.HTTP_200_OK)

    async def _get_origin_file(self, id: int):
        entity = self._transcription_service.get(id)
        print(entity.origin_filepath)
        return FileResponse(entity.origin_filepath, status_code=status.HTTP_200_OK)

    async def _create(self,
                      transcription_type: str = Form(str),
                      model_settings: Optional[str] = Form('{}'),
                      file: UploadFile = File(None)):

        try:
            trans_type = TranscriptionType(transcription_type)
        except ValueError:
            raise ValueError(f"Invalid transcription type '{transcription_type}'")

        json_model_settings = {}

        if model_settings is not None:
            try:
                json_model_settings = json.loads(model_settings)
            except Exception as exc:
                raise ValueError(
                    f"Invalid model settings json format: model_settings: {model_settings}, exception: {exc}")

        transcription_dto = TranscriptionDto(
            model_settings=json_model_settings,
            filename=str(file.filename),
            transcription_type=trans_type,
            file_stream=file.file
        )

        try:
            entity = self._transcription_service.create(transcription_dto)
        except Exception as exc:
            raise exc

        return FileResponse(entity.transcription_filepath)

    async def _remove(self, id):
        self._transcription_service.remove(id)
        return Response(status_code=status.HTTP_202_ACCEPTED)
