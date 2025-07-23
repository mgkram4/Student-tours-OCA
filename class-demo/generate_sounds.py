import os

import numpy as np
import pygame
from scipy.io import wavfile


def generate_sound(frequency, duration, volume=0.3, sample_rate=44100):
    """Generate a simple sine wave sound"""
    samples = int(duration * sample_rate)
    wave = np.sin(2 * np.pi * frequency * np.linspace(0, duration, samples))
    wave = (wave * volume * 32767).astype(np.int16)
    return wave

def save_sound(wave, filename, sample_rate=44100):
    """Save wave data as a WAV file in 16-bit integer format"""
    # Ensure wave is 16-bit integer
    wave = wave.astype(np.int16)
    wavfile.write(filename, sample_rate, wave)

def main():
    pygame.mixer.init(44100, -16, 1, 1024)
    
    # Create sounds directory if it doesn't exist
    if not os.path.exists("sounds"):
        os.makedirs("sounds")
    
    # Generate different sound effects
    print("Generating sound effects...")
    
    # Player shoot sound (high pitch beep)
    shoot_sound = generate_sound(800, 0.1, 0.2)
    save_sound(shoot_sound, "sounds/shoot.wav")
    
    # Enemy shoot sound (lower pitch)
    enemy_shoot = generate_sound(400, 0.15, 0.15)
    save_sound(enemy_shoot, "sounds/invader_shoot.wav")
    
    # Hit sound (medium pitch)
    hit_sound = generate_sound(600, 0.2, 0.25)
    save_sound(hit_sound, "sounds/hit.wav")
    
    # Explosion sound (noise-like)
    explosion_samples = int(0.3 * 44100)
    explosion_wave = np.random.randint(-16384, 16384, explosion_samples, dtype=np.int16)
    explosion_wave = (explosion_wave * 0.3).astype(np.int16)
    save_sound(explosion_wave, "sounds/explosion.wav")
    
    # Game over sound (descending tone)
    game_over_samples = int(0.5 * 44100)
    frequencies = np.linspace(400, 200, game_over_samples)
    game_over_wave = np.zeros(game_over_samples, dtype=np.int16)
    for i in range(game_over_samples):
        freq = frequencies[i]
        game_over_wave[i] = int(16384 * 0.3 * np.sin(2 * np.pi * freq * i / 44100))
    save_sound(game_over_wave, "sounds/game_over.wav")
    
    # Background music (simple loop)
    bg_samples = int(2.0 * 44100)  # 2 second loop
    bg_wave = np.zeros(bg_samples, dtype=np.int16)
    for i in range(bg_samples):
        t = i / 44100
        # Create a simple melody
        note1 = np.sin(2 * np.pi * 220 * t) * 0.1  # A3
        note2 = np.sin(2 * np.pi * 330 * t) * 0.1  # E4
        note3 = np.sin(2 * np.pi * 440 * t) * 0.1  # A4
        bg_wave[i] = int(16384 * (note1 + note2 + note3))
    
    # Save as WAV file
    save_sound(bg_wave, "sounds/background_music.wav")
    
    print("Sound effects generated successfully!")
    print("Files created:")
    print("- sounds/shoot.wav")
    print("- sounds/invader_shoot.wav") 
    print("- sounds/hit.wav")
    print("- sounds/explosion.wav")
    print("- sounds/game_over.wav")
    print("- sounds/background_music.wav")

if __name__ == "__main__":
    main() 