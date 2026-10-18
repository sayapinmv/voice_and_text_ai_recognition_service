from typing import Any
from pathlib import Path

from qwen_tts import Qwen3TTSModel

from src.module.entities.file import FileEntity, FileType
from src.module.entities.transcription import TranscriptionType
from src.module.service.file_storage.service import FileStorageService, FileDto
from src.module.service.recognition.service import RecognitionService, RecognitionDto, Config
from src.module.logger.logger import Logger
from src.module.service.recognition.text_to_speech.qwen_tts_settings import QwenTTSModelSettings, \
    QwenTTSTranscriptionSettings


class QwenTTSServiceImpl(RecognitionService):

    def __init__(self,
                 qwen_tts_cfg: Config,
                 file_service: FileStorageService,
                 logger: Logger):
        super().__init__(file_service, logger)
        model_settings = QwenTTSModelSettings(**qwen_tts_cfg.model_settings)
        self._model = self.set_up_model(model_settings)
        self._default_settings = QwenTTSTranscriptionSettings(**qwen_tts_cfg.default_transcription_settings)

    def set_up_model(self, model_settings: QwenTTSModelSettings):
        try:
            json_settings = model_settings.model_dump(exclude={'model_path'}, exclude_none=True)
            model = Qwen3TTSModel.from_pretrained(model_settings.model_path, **json_settings)
        except Exception as exc:
            self.logger.error(f"Failed to set up QwenTTS model.\nSettings: {model_settings}\nException: {exc}")
            raise RuntimeError(f"Failed to set up QwenTTS model.\nSettings: {model_settings}\nException: {exc}")
        return model

    def merge_settings(self, transcription_settings: dict[str, Any]) -> dict[str, Any]:
        merged_settings = self._default_settings.model_dump().copy()

        for key, val in transcription_settings.items():
            merged_settings[key] = val

        return merged_settings

    def set_up_transcription_settings(self, transcription_settings: Any):
        union_settings = self.merge_settings(transcription_settings)
        try:
            qwen_tts_settings = QwenTTSTranscriptionSettings.model_validate(union_settings)
        except Exception as e:
            self.logger.error(f"Invalid QwenTTS transcription settings: {e}")
            raise ValueError(f"Invalid QwenTTS transcription settings: {e}")

        return qwen_tts_settings

    def create_transcription(self, recognition_dto: RecognitionDto) -> FileEntity:
        transcription_settings = self._default_settings
        if recognition_dto.model_settings is not None:
            transcription_settings = self.set_up_transcription_settings(recognition_dto.model_settings)

        self.logger.debug(f"QwenTTS transcription settings: {transcription_settings}")

        try:
            np_arrays, sample_rate = self._model.generate_custom_voice(
                text=str(recognition_dto.file.read()),
                **transcription_settings.model_dump(),
            )
        except Exception as exc:
            raise ValueError(exc)

        original_name = Path(recognition_dto.filename).stem
        extension = transcription_settings.output_format
        output_filename = f"{original_name}.{extension}"


        return self.file_service.create_file(FileDto(
            type=FileType.Media,
            filepath=Path("outputs") / Path(TranscriptionType.TEXT_TO_SPEECH.value.lower()) / Path(output_filename),
            file_data=np_arrays[0].tobytes(),
            meta={
                'sample_rate': sample_rate,
            }
        ))
