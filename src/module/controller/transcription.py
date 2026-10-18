import json
from typing import Optional

from fastapi.responses import FileResponse, Response, JSONResponse
from fastapi import APIRouter, UploadFile, Form, File, status, HTTPException

from src.module.logger.logger import Logger
from src.module.service.transcription.service import TranscriptionService, TranscriptionDto
from src.module.entities.transcription import TranscriptionType

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
        return JSONResponse(entity.model_dump_json())

    async def _get_origin_file(self, id: int):
        origin_file = self._transcription_service.get_origin_filepath(id)
        self._logger.info(f"Transcription origin filepath: {origin_file.filepath}")
        return FileResponse(origin_file.filepath, filename=origin_file.filename, status_code=status.HTTP_200_OK)

    async def _get_transcription_file(self, id: int):
        transcription_file = self._transcription_service.get_transcription_filepath(id)
        self._logger.info(f"Transcription filepath: {transcription_file.filepath}")
        return FileResponse(transcription_file.filepath, filename=transcription_file.filename, status_code=status.HTTP_200_OK)

    async def _create(self,
                      type: str = Form(str),
                      transcription_settings: Optional[str] = Form('{}'),
                      origin_file: UploadFile = File(None)):

        try:
            trans_type = TranscriptionType(type)
        except ValueError:
            raise HTTPException(detail=json.dumps({"err_msg":f"Invalid transcription type '{type}'"}, status_code=status.HTTP_400_BAD_REQUEST))

        json_model_settings = {}

        if transcription_settings is not None:
            try:
                json_model_settings = json.loads(transcription_settings)
            except Exception as exc:
                raise HTTPException(detail=json.dumps({f"Invalid model settings json format: model_settings: {transcription_settings}, exception: {exc}"},
                                                      status_code=status.HTTP_400_BAD_REQUEST))

        transcription_dto = TranscriptionDto(
            model_settings=json_model_settings,
            filename=str(origin_file.filename),
            type=trans_type,
            file=origin_file.file
        )

        try:
            entity = self._transcription_service.create(transcription_dto)
        except Exception as exc:
            raise exc

        return JSONResponse(entity.model_dump_json())

    async def _remove(self, id):
        self._transcription_service.remove(id)
        return Response(status_code=status.HTTP_202_ACCEPTED)
