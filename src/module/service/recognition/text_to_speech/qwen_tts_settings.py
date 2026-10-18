from typing import Optional
from pydantic import BaseModel, Field, field_validator

class QwenTTSModelSettings(BaseModel):
    model_path: str = Field(
        default="./models/qwen-tts",
        description="Путь к локальной папке модели или ID репозитория HuggingFace"
    )
    device_map: str = Field(
        default="cpu",
        description="Устройство: cpu, cuda:0, auto"
    )
    dtype: str = Field(
        default="bfloat16",
        description="Тип данных: bfloat16, float16, float32"
    )
    attn_implementation: str = Field(
        default="sdpa",
        description="Реализация внимания: sdpa, flash_attention_2"
    )

    @field_validator("device_map")
    @classmethod
    def validate_device(cls, v: str) -> str:
        if v in {"cpu", "auto"} or v.startswith("cuda"):
            return v
        raise ValueError(f"device_map must be 'cpu', 'auto' or 'cuda:N', got '{v}'")

    @field_validator("dtype")
    @classmethod
    def validate_dtype(cls, v: str) -> str:
        allowed = {"bfloat16", "float16", "float32"}
        if v not in allowed:
            raise ValueError(f"dtype must be one of: {allowed}")
        return v

    @field_validator("attn_implementation")
    @classmethod
    def validate_attn(cls, v: str) -> str:
        allowed = {"sdpa", "flash_attention_2"}
        if v not in allowed:
            raise ValueError(f"attn_implementation must be one of: {allowed}")
        return v


# ============================================
# Параметры генерации (передаются в generate_custom_voice)
# Можно переопределять на каждый запрос
# ============================================
class QwenTTSTranscriptionSettings(BaseModel):
    speaker: str = Field(
        default="Vivian",
        description="Голос: Vivian, Serena, Uncle_Fu, Dylan, Eric, Ryan, Aiden, Ono_Anna, Sohee"
    )
    language: str = Field(
        default="Russian",
        description="Язык: Chinese, English, Japanese, Korean, German, French, "
                    "Russian, Portuguese, Spanish, Italian"
    )
    instruct: Optional[str] = Field(
        default=None,
        description="Инструкция стиля речи (только для моделей 1.7B)"
    )
    output_format: str = Field(
        default="wav",
        description="Расширение выходного файла"
    )

    # Параметры сэмплирования
    do_sample: bool = Field(default=True)
    temperature: float = Field(default=0.85, ge=0.0, le=2.0)
    top_k: int = Field(default=50, ge=0)
    top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    repetition_penalty: float = Field(default=1.05, ge=1.0)
    max_new_tokens: int = Field(default=600, gt=0)

    @field_validator("speaker")
    @classmethod
    def validate_speaker(cls, v: str) -> str:
        allowed = {
            "Vivian", "Serena", "Uncle_Fu", "Dylan", "Eric",
            "Ryan", "Aiden", "Ono_Anna", "Sohee",
        }
        if v not in allowed:
            raise ValueError(f"speaker must be one of: {allowed}")
        return v

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        allowed = {
            "Chinese", "English", "Japanese", "Korean", "German",
            "French", "Russian", "Portuguese", "Spanish", "Italian",
        }
        if v not in allowed:
            raise ValueError(f"language must be one of: {allowed}")
        return v

    @field_validator("output_format")
    @classmethod
    def validate_output_format(cls, v: str) -> str:
        allowed = {"wav", "mp3", "flac", "ogg"}
        v = v.lower().lstrip(".")
        if v not in allowed:
            raise ValueError(f"output_format must be one of: {allowed}")
        return v