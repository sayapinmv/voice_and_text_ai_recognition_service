import json
from pathlib import Path
from typing import Any, BinaryIO
import numpy as np
import io
import av

import whisper

from src.module.entities.file import FileType, FileEntity
from src.module.entities.transcription import TranscriptionType
from src.module.service.recognition.speech_to_text.whisper_settings import ModelSettings, TranscriptionSettings
from src.module.service.file_storage.service import FileStorageService, FileDto
from src.module.service.recognition.service import RecognitionService, RecognitionDto, Config
from src.module.logger.logger import Logger

DEFAULT_SAMPLE_RATE = 16000

def _format_timestamp(seconds: float, srt: bool = True) -> str:
    milliseconds = round(seconds * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, milliseconds = divmod(remainder, 1000)

    separator = "," if srt else "."
    return (
        f"{hours:02}:{minutes:02}:{secs:02}"
        f"{separator}{milliseconds:03}"
    )

def _to_srt(segments: list[dict]) -> str:
    blocks = []

    for index, segment in enumerate(segments, start=1):
        start = _format_timestamp(segment["start"])
        end = _format_timestamp(segment["end"])
        text = segment["text"].strip()

        blocks.append(f"{index}\n{start} --> {end}\n{text}")

    return "\n\n".join(blocks) + ("\n" if blocks else "")

def _to_vtt(segments: list[dict]) -> str:
    blocks = ["WEBVTT"]

    for segment in segments:
        start = _format_timestamp(segment["start"], srt=False)
        end = _format_timestamp(segment["end"], srt=False)
        text = segment["text"].strip()

        blocks.append(f"{start} --> {end}\n{text}")

    return "\n\n".join(blocks) + "\n"

class WhisperServiceImpl(RecognitionService):
    def __init__(self,
                 cfg: Config,
                 file_service: FileStorageService,
                 logger: Logger):
        super().__init__(file_service, logger)

        model_settings = ModelSettings(**cfg.model_settings)
        self._model = self.set_up_model(model_settings)
        self._default_settings = TranscriptionSettings(**cfg.default_transcription_settings)

    def set_up_model(self, model_settings: ModelSettings):
        try:
            model = whisper.load_model(model_settings.name, model_settings.device, in_memory=model_settings.in_memory)
        except Exception as exc:
            self.logger.error(f"Failed to set up Whisper model.\nSettings: {model_settings}\nException: {exc}")
            raise RuntimeError(f"Failed to set up Whisper model.\nSettings: {model_settings}\nException: {exc}")
        return model

    def merge_settings(self, transcription_settings: dict[str, Any]) -> dict[str, Any]:
        merged_settings = self._default_settings.model_dump().copy()

        for key, val in transcription_settings.items():
            merged_settings[key] = val

        return merged_settings

    def set_up_transcription_settings(self, transcription_settings: dict[str, Any]) -> TranscriptionSettings:
        union_settings = self.merge_settings(transcription_settings)
        try:
            whisper_settings = TranscriptionSettings.model_validate(union_settings)
        except Exception as e:
            self.logger.error(f"Invalid Whisper transcription settings: {e}")
            raise ValueError(f"Invalid Whisper transcription settings: {e}")

        return whisper_settings

    def create_transcription(self, recognition_dto: RecognitionDto) -> FileEntity:
        transcription_settings = self._default_settings
        if recognition_dto.model_settings is not None:
            transcription_settings = self.set_up_transcription_settings(recognition_dto.model_settings)

        self.logger.debug(f"Whisper transcription settings: {transcription_settings}")

        try:
            recognition = self.transcript(recognition_dto.filename, recognition_dto.file, transcription_settings)
        except Exception as exc:
            raise ValueError(exc)

        original_name = Path(recognition_dto.filename).stem
        extension = transcription_settings.output_format
        output_filename = f"{original_name}.{extension}"

        return self.file_service.create_file(FileDto(
            type=FileType.Text,
            filepath=Path("outputs") / Path(TranscriptionType.SPEECH_TO_TEXT.value.lower()) / Path(output_filename),
            file_data=recognition,
        ))

    def audio_bytes_to_array(self, file: BinaryIO, file_extension: str) -> np.ndarray:
        file.seek(0)
        data = file.read()

        if not data:
            raise ValueError("Uploaded file is empty")

        try:
            with av.open(io.BytesIO(data), mode="r") as container:
                audio_streams = [
                    stream
                    for stream in container.streams
                    if stream.type == "audio"
                ]

                if not audio_streams:
                    raise ValueError("Video contains no audio stream")

                resampler = av.AudioResampler(
                    format="fltp",
                    layout="mono",
                    rate=DEFAULT_SAMPLE_RATE,
                )

                audio_chunks = []

                for frame in container.decode(audio_streams[0]):
                    resampled_frames = resampler.resample(frame)

                    if not isinstance(resampled_frames, list):
                        resampled_frames = [resampled_frames]

                    for resampled_frame in resampled_frames:
                        if resampled_frame is not None:
                            audio_chunks.append(
                                resampled_frame.to_ndarray().reshape(-1)
                            )

                # Забираем оставшиеся семплы из ресемплера.
                remaining = resampler.resample(None)

                if not isinstance(remaining, list):
                    remaining = [remaining]

                for resampled_frame in remaining:
                    if resampled_frame is not None:
                        audio_chunks.append(
                            resampled_frame.to_ndarray().reshape(-1)
                        )

                if not audio_chunks:
                    raise ValueError("Decoded audio is empty")

                audio_array = np.concatenate(audio_chunks).astype(np.float32)

                self.logger.debug(
                    f"Audio duration: {len(audio_array) / DEFAULT_SAMPLE_RATE:.2f}s"
                )

                return audio_array

        except (ValueError, RuntimeError):
            raise
        except Exception as exc:
            raise RuntimeError(
                f"Failed to decode audio from '{file_extension}' file: {exc}"
            ) from exc
        finally:
            file.seek(0)
        if result.returncode != 0:
            error_message = result.stderr.decode("utf-8", errors="replace")
            raise RuntimeError(f"FFmpeg failed: {error_message}")

        if not result.stdout:
            error_message = result.stderr.decode("utf-8", errors="replace")
            raise RuntimeError(
                f"FFmpeg returned empty output. Details: {error_message}"
            )

        audio_file = io.BytesIO(result.stdout)
        audio_file.seek(0)

        return audio_file

    def transcript(self, filename: str, file: BinaryIO, transcription_settings: TranscriptionSettings) -> bytes:
        ext = Path(filename).suffix.lower().lstrip(".")
        try:
            audio_array = self.audio_bytes_to_array(file, ext)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load audio file '{filename}'"
            ) from exc

        settings = transcription_settings.model_dump(
            exclude={"output_format"},
            exclude_none=True,
        )

        # На CPU отключаем FP16
        if getattr(self._model, "device", None) is not None:
            if str(self._model.device) == "cpu":
                settings["fp16"] = False

        try:
            result = self._model.transcribe(audio_array, **settings)
        except Exception as exc:
            self.logger.error(
                f"Transcription failed for '{filename}': {exc}"
            )
            raise RuntimeError(
                f"Failed to transcribe '{filename}'"
            ) from exc

        if result is None or result["text"] == "" or result["text"] is None:
            raise RuntimeError('Transcription text is empty')

        output_format = transcription_settings.output_format

        if output_format == "txt":
            output = result["text"].strip()

        elif output_format == "srt":
            output = _to_srt(result["segments"])

        elif output_format == "vtt":
            output = _to_vtt(result["segments"])

        elif output_format == "json":
            output = json.dumps(result, ensure_ascii=False, indent=2)

        else:
            raise ValueError(f"Unsupported format: {output_format}")

        return output.encode("utf-8")