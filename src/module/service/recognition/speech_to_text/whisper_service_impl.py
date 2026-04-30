from dataclasses import dataclass
from typing import Any
import numpy as np
import librosa
import io

import whisper

from src.module.service.recognition.speech_to_text.models.whisper_settings import WhisperSettings
from src.module.entity.transcription_entity import TranscriptionEntity, TranscriptionType
from src.module.service.file_storage.disk_storage.service import DiskFileStorageService, Encoding
from src.module.service.file_storage.disk_storage.service import AudioFileExtension
from src.module.service.recognition.service import RecognitionService
from src.module.logger.logger import Logger


@dataclass
class Transcription:
    transcription_filename: str
    transcription_filepath: str
    origin_filename: str
    origin_filepath: str


ALLOWED_EXTENSIONS = ', '.join(ext.value for ext in AudioFileExtension)
DEFAULT_SAMPLE_RATE = 16000

class WhisperServiceImpl(RecognitionService):
    def __init__(self,
                 default_settings: dict[str, Any],
                 origin_storage: DiskFileStorageService,
                 transcriptions_storage: DiskFileStorageService,
                 logger: Logger):
        super().__init__(default_settings, origin_storage, transcriptions_storage, logger)

        self._default_settings = self.set_up_settings(default_settings)

    def create_transcription(self, filename: str, origin_stream: io.BytesIO, model_settings: dict[str, Any] = None) -> TranscriptionEntity:
        file_extension = filename.split('.')[-1]

        if file_extension.lower() not in ALLOWED_EXTENSIONS:
            self.logger.error(f"Invalid file extension {file_extension}. Should be one of them: {ALLOWED_EXTENSIONS}")
            raise ValueError(f"Invalid file extension {file_extension}. Should be one of them: {ALLOWED_EXTENSIONS}")

        try:
            np_array = self._audio_bytes_to_array(origin_stream)
        except Exception as exc:
            raise Exception(f"Failed converting to narray file tread for file by name '{filename}'. error: {exc}")

        if model_settings is None or not model_settings:
            whisper_settings = self._default_settings
        else:
            whisper_settings = self.set_up_settings(model_settings)

        try:
            model = self.set_up_model(whisper_settings)
            transcription_result = self.transcript(np_array, model, whisper_settings)

            if transcription_result["text"] is None:
                self.logger.error("Failed to transcript speech to text.")
                raise RuntimeError("Failed to transcript speech to text.")

            transcription_stream = io.StringIO()
            transcription_stream.write(transcription_result["text"])

        except Exception as exc:
            raise ValueError(exc)

        new_origin_filepath = self.origin_storage.create_sound_file(filename, np_array, DEFAULT_SAMPLE_RATE)
        new_transcription_filename = self.transcriptions_storage.set_new_file_extension(filename, 'txt')
        new_transcription_filepath = self.transcriptions_storage.create_text_file(new_transcription_filename, transcription_stream, Encoding.UTF_8)

        return TranscriptionEntity(
            transcription_type=TranscriptionType.SPEECH_TO_TEXT,
            transcription_name=new_transcription_filename,
            transcription_filepath=new_transcription_filepath,
            origin_name=filename,
            origin_filepath=new_origin_filepath
        )

    @staticmethod
    def _audio_bytes_to_array(audio_stream: io.BytesIO) -> np.ndarray:
        try:
            audio_array, samplerate = librosa.load(audio_stream, sr=None)
        except Exception as exc:
            raise exc

        if samplerate != DEFAULT_SAMPLE_RATE:
            audio_array = librosa.resample(audio_array, orig_sr=samplerate, target_sr=16000)

        return audio_array.astype(np.float32)

    def set_up_settings(self, whisper_settings: dict[str, Any]) -> WhisperSettings:
        try:
            whisper_model_settings = WhisperSettings.model_validate(whisper_settings)
        except Exception as e:
            self.logger.error(f"Invalid model settings: {e}")
            raise ValueError(f"Invalid model settings: {e}")

        return whisper_model_settings

    def set_up_model(self, whisper_settings: WhisperSettings):
        try:
            model = whisper.load_model(whisper_settings.name, whisper_settings.device, in_memory=whisper_settings.in_memory)
        except Exception as exc:
            self.logger.error(f"Failed to set up model.\nSettings: {whisper_settings}\nException: {exc}")
            raise RuntimeError(f"Failed to set up model.\nSettings: {whisper_settings}\nException: {exc}")
        return model

    def transcript(self, audio_np_array, model, whisper_settings: WhisperSettings) -> dict[str, Any]:
        if model is None:
            self.set_up_model(whisper_settings)

        # decode_options = {
        #     'beam_size': whisper_settings.beam_size,
        #     'best_of': whisper_settings.best_of,
        #     'patience': whisper_settings.patience,
        #     'length_penalty': whisper_settings.length_penalty,
        #     'suppress_tokens': whisper_settings.suppress_tokens,
        #     'suppress_blank': whisper_settings.suppress_blank,
        #     'without_timestamps': whisper_settings.without_timestamps,
        #     'max_initial_timestamp': whisper_settings.max_initial_timestamp,
        # }
        #
        # if whisper_settings.word_timestamps:
        #     decode_options['word_timestamps'] = True
        #
        # if whisper_settings.fp16 and model.device.type == 'cuda':
        #     decode_options['fp16'] = True
        #
        # decode_options = {k: v for k, v in decode_options.items() if v is not None}

        self.logger.info(
            f"Whisper model settings: {' '.join(f'{key}={val}' for key, val in whisper_settings.model_dump().items())}"
        )
        try:
            transcription_result = model.transcribe(
                audio_np_array,
                task=whisper_settings.task,
                language=whisper_settings.language,
                temperature=whisper_settings.temperature,
                compression_ratio_threshold=whisper_settings.compression_ratio_threshold,
                logprob_threshold=whisper_settings.logprob_threshold,
                no_speech_threshold=whisper_settings.no_speech_threshold,
                condition_on_previous_text=whisper_settings.condition_on_previous_text,
                initial_prompt=whisper_settings.initial_prompt,
                verbose=whisper_settings.verbose,
                # decode_options=decode_options if decode_options else None
            )
        except Exception as exc:
            self.logger.error(f"Failed to transcript .\nSettings: {whisper_settings}\nException: {exc}")
            raise RuntimeError(f"Failed to set up model.\nSettings: {whisper_settings}\nException: {exc}")

        return transcription_result
