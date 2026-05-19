from typing import Optional, Union, List

from pydantic import BaseModel, Field, field_validator


class WhisperSettings(BaseModel):
    model_name: Optional[str] = Field(
        default='base',
        description="Версия нейросетевой модели whisper (tiny, small, base, medium, large-v2, large-v3)"
    )
    device: Optional[str] = Field(
        default='cpu',
        description="Чип, на котором будут производится вычисления (cpu, gpu)"
    )
    in_memory: Optional[bool] = Field(
        default='false',
        description="..."
    )
    language: Optional[str] = Field(
        default='ru',
        description="Язык аудио (ru, en, fr и т.д. или null для автоопределения)"
    )
    task: str = Field(
        default='transcribe',
        description="Тип задачи: transcribe или translate"
    )

    temperature: Union[float, List[float]] = Field(
        default=0.0,
        description="Температура семплинга (float или список значений)"
    )
    compression_ratio_threshold: Optional[float] = Field(
        default=2.4,
        description="Порог отбраковки по коэффициенту сжатия"
    )
    logprob_threshold: Optional[float] = Field(
        default=-1.0,
        description="Порог отбраковки по логарифмической вероятности"
    )
    no_speech_threshold: Optional[float] = Field(
        default=0.6,
        description="Порог определения тишины"
    )

    condition_on_previous_text: bool = Field(
        default=True,
        description="Учитывать предыдущий текст при декодировании"
    )
    initial_prompt: Optional[str] = Field(
        default=None,
        description="Начальный промпт для контекста"
    )
    word_timestamps: bool = Field(
        default=False,
        description="Добавлять таймстампы для каждого слова"
    )
    verbose: bool = Field(
        default=False,
        description="Подробный вывод в консоль"
    )
    fp16: bool = Field(
        default=True,
        description="Использовать FP16 (только для GPU)"
    )

    @field_validator('model_name')
    def validate_name(cls, v):
        allowed = ['tiny', 'small', 'base', 'medium', 'large-v2', 'large-v3']
        if v not in allowed:
            raise ValueError(f'Model name must be one of: {allowed}')
        return v

    @field_validator('device')
    def validate_device(cls, v):
        allowed = ['cpu', 'gpu']
        if v not in allowed:
            raise ValueError(f'Model device must be one of: {allowed}')
        return v

    @field_validator('task')
    def validate_task(cls, v):
        allowed = ['transcribe', 'translate']
        if v not in allowed:
            raise ValueError(f'task must be one of: {allowed}')
        return v

    @field_validator('temperature')
    def validate_temperature(cls, v):
        if isinstance(v, float):
            if v < 0 or v > 2:
                raise ValueError('temperature float must be between 0 and 2')
        elif isinstance(v, list):
            for t in v:
                if t < 0 or t > 2:
                    raise ValueError('all temperature values must be between 0 and 2')
        return v

    @field_validator('compression_ratio_threshold')
    def validate_compression_ratio(cls, v):
        if v is not None and v < 0:
            raise ValueError('compression_ratio_threshold must be positive')
        return v

    @field_validator('logprob_threshold')
    def validate_logprob(cls, v):
        if v is not None and v > 0:
            raise ValueError('logprob_threshold should typically be negative')
        return v

    @field_validator('no_speech_threshold')
    def validate_no_speech(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError('no_speech_threshold must be between 0 and 1')
        return v
