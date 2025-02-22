import sounddevice as sd
import numpy as np

# Using a reasonable sample rate and factory settings
SAMPLE_RATE = 16000     # Sample rate
CHANNELS = 1            # Mono audio
AMPLIFY_AMOUNT = 1.2      # Lower amplification factor for cleaner sound
NOISE_THRESHOLD = 0.007  # Much lower threshold to preserve almost all detail

# Less severe quantization (increasing bit depth preserves more quality)
QUANTIZE_BITS = 8      # Increased bit depth; higher = cleaner signal

def filter_noise(audio_data, threshold=NOISE_THRESHOLD):
    """
    Filter out background noise by zeroing samples with extremely low amplitudes.
    """
    return np.where(np.abs(audio_data) < threshold, 0, audio_data)

def bad_quality(audio_data):
    """
    Apply mild quantization to degrade quality slightly.
    """
    # Normalize audio data to the range [-1, 1]
    norm = np.max(np.abs(audio_data))
    if norm == 0:
        return audio_data
    audio_data = audio_data / norm
    # Quantize the audio data using higher bit depth for less degradation
    levels = 2**(QUANTIZE_BITS) - 1
    quantized = np.round(audio_data * levels) / levels
    return quantized

def callback(indata, outdata, frames, time, status):
    if status:
        print(status)
    # Apply a minimal noise filter to preserve nearly all the signal detail
    filtered = filter_noise(indata)
    # Process the audio with mild quantization
    processed = bad_quality(filtered)
    # Amplify the processed audio moderately
    amplified = np.clip(processed * AMPLIFY_AMOUNT, -1, 1)
    outdata[:] = amplified

# Configure output device to target VB-Audio Virtual Cable.
with sd.Stream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        device=(None, 'CABLE Input (VB-Audio Virtual C, MME'),
        callback=callback
    ):
    print("Streaming processed audio from microphone to VB-Audio Cable...\nPress Ctrl+C to exit.")
    try:
        while True:
            sd.sleep(1000)
    except KeyboardInterrupt:
        print("Streaming stopped.")