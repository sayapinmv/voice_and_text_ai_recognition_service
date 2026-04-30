from typing import TextIO
from typing import Any
from pathlib import Path
import torch

from qwen_tts import Qwen3TTSModel

from src.module.entity.transcription_entity import TranscriptionEntity, TranscriptionType
from src.module.service.file_storage.disk_storage.service import DiskFileStorageService, Encoding
from src.module.service.recognition.service import RecognitionService
from src.module.service.file_storage.disk_storage.service import TextFileExtension
from src.module.logger.logger import Logger

ALLOWED_EXTENSIONS = ', '.join(ext.value for ext in TextFileExtension)

class QwenTTSServiceImpl(RecognitionService):

    def __init__(self,
                 default_settings: dict[str, Any],
                 origins_storage: DiskFileStorageService,
                 transcriptions_storage: DiskFileStorageService,
                 logger: Logger):
        super().__init__(default_settings, origins_storage, transcriptions_storage, logger)

        self._default_settings = default_settings

    def create_transcription(self, filename: str, origin_stream: TextIO, model_settings: dict[str, Any] = None) -> TranscriptionEntity:
        file_extension = filename.split('.')[-1]

        if file_extension not in ALLOWED_EXTENSIONS:
            self.logger.error(f"Invalid file extension {file_extension}. Should be one of them: {ALLOWED_EXTENSIONS}")
            raise ValueError(f"Invalid file extension {file_extension}. Should be one of them: {ALLOWED_EXTENSIONS}")

        try:
            model = Qwen3TTSModel.from_pretrained(
                "./models/qwen-tts",
                device_map="cpu",
                dtype=torch.bfloat16,
                attn_implementation="sdpa",
            )

            np_arrays, sample_rate = model.generate_custom_voice(
                text=origin_stream.read(),
                language=["Russian"],
                speaker=["Vivian"]
            )

        except Exception as exc:
            raise ValueError(exc)

        # new_origin_filepath = self.origin_storage.create_text_file(filename, origin_stream, Encoding.UTF_8)
        new_transcription_filename = self.transcriptions_storage.set_new_file_extension(filename, 'wav')
        new_transcription_filepath = self.transcriptions_storage.create_sound_file(new_transcription_filename, np_arrays[0], sample_rate)

        return TranscriptionEntity(
            transcription_type=TranscriptionType.TEXT_TO_SPEECH,
            transcription_name=new_transcription_filename,
            transcription_filepath=new_transcription_filepath,
            origin_name=filename,
            origin_filepath=Path('./')
            # origin_filepath=new_origin_filepath
        )
