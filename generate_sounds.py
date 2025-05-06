import wave
import struct
import math

def generate_tone(filename, frequency, duration, volume=0.5):
    # Audio parameters
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    
    wav_file = wave.open(f"sounds/{filename}", 'w')
    wav_file.setnchannels(1)  # Mono
    wav_file.setsampwidth(2)  # 2 bytes per sample
    wav_file.setframerate(sample_rate)
    
    for i in range(num_samples):
        value = int(32767.0 * volume * math.sin(2.0 * math.pi * frequency * i / sample_rate))
        data = struct.pack('<h', value)
        wav_file.writeframes(data)
    
    wav_file.close()

# Generate sound effects
generate_tone("correct.wav", 800, 0.1)  # High pitch success sound
generate_tone("wrong.wav", 300, 0.2)    # Low pitch error sound
generate_tone("win.wav", 600, 0.5)      # Victory fanfare
generate_tone("click.wav", 1000, 0.05)  # Quick click sound