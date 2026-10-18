from typing import Literal

from pydantic import BaseModel, Field, field_validator, ConfigDict


class ModelSettings(BaseModel):
    name: Literal[
        "tiny",
        "tiny.en",
        "base",
        "base.en",
        "small",
        "small.en",
        "medium",
        "medium.en",
        "large",
        "large-v1",
        "large-v2",
        "large-v3",
        "large-v3-turbo",
        "turbo",
    ] = "base"

    device: Literal["cpu", "cuda"] = "cpu"
    in_memory: bool = False

class TranscriptionSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    language: str | None = "ru"
    task: Literal["transcribe", "translate"] = "transcribe"

    temperature: float | list[float] = 0.0
    compression_ratio_threshold: float | None = Field(default=2.4, gt=0)
    logprob_threshold: float | None = -1.0
    no_speech_threshold: float | None = Field(default=0.6, ge=0, le=1)

    condition_on_previous_text: bool = True
    initial_prompt: str | None = None
    word_timestamps: bool = False
    without_timestamps: bool = False
    hallucination_silence_threshold: float | None = Field(
        default=None, ge=0
    )

    verbose: bool = False
    fp16: bool = True

    beam_size: int | None = Field(default=5, ge=1)
    best_of: int | None = Field(default=5, ge=1)
    patience: float | None = Field(default=None, gt=0)
    length_penalty: float | None = Field(default=None, gt=0)

    output_format: Literal["txt", "srt", "vtt", "json"] = "txt"

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, value):
        values = value if isinstance(value, list) else [value]
        if not values or any(not 0 <= t <= 1 for t in values):
            raise ValueError("temperature must be between 0 and 1")
        return value