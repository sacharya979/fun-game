import wave
import struct
import math
import random

def generate_note(frequency, duration, volume=0.3):
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    samples = []
    
    for i in range(num_samples):
        value = int(32767.0 * volume * math.sin(2.0 * math.pi * frequency * i / sample_rate))
        samples.append(value)
    
    return samples

def generate_music():
    # Simple pentatonic scale frequencies
    notes = [523.25, 587.33, 659.25, 783.99, 880.00]  # C5, D5, E5, G5, A5
    sample_rate = 44100
    
    # Create a simple melody
    all_samples = []
    for _ in range(4):  # 4 bars
        for _ in range(4):  # 4 notes per bar
            note = random.choice(notes)
            duration = 0.25  # quarter note
            note_samples = generate_note(note, duration)
            all_samples.extend(note_samples)
    
    # Write to WAV file
    wav_file = wave.open("sounds/background_music.wav", 'w')
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    
    for sample in all_samples:
        data = struct.pack('<h', sample)
        wav_file.writeframes(data)
    
    wav_file.close()

if __name__ == "__main__":
    generate_music()