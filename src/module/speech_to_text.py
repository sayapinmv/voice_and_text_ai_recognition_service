import whisper
import time

print("🎵 Whisper транскрибация")
print("="*50)

# 1. Загрузи модель
print("1. Загрузка модели tiny...")
start = time.time()
model = whisper.load_model("tiny")
print(f"✅ Загружено за {time.time()-start:.1f} сек")

# 2. Распознай
print("\n2. Распознавание аудио...")
start = time.time()
result = model.transcribe(
    "audio_2026-01-08_19-13-59.ogg",
    verbose=True,
    fp16=False
)

print(f"\n✅ Готово за {time.time()-start:.1f} сек")

# 3. Результат
print("\n" + "="*50)
print("📝 ТРАНСКРИПЦИЯ:")
print("="*50)
print(result["text"])

# 4. Сохрани
with open("transcript.txt", "w", encoding="utf-8") as f:
    f.write(result["text"])
print(f"\n💾 Сохранено в transcript.txt")
