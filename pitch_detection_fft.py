import pyaudio
import numpy as np

# Audio settings
FORMAT = pyaudio.paInt16  # 16-bit audio
CHANNELS = 1  # Mono audio
RATE = 44100  # Sampling rate (CD quality)
BUFFER_SIZE = 1024  # Frames per buffer (audio chunk size)

running = True

p = pyaudio.PyAudio()

def detect_pitch(audio_data, rate):
    """ Apply FFT to find the dominant frequency """
    fft_spectrum = np.fft.fft(audio_data)  
    freqs = np.fft.fftfreq(len(fft_spectrum), d=1/rate)  

    magnitude = np.abs(fft_spectrum)  
    
    peak_index = np.argmax(magnitude[:len(magnitude)//2])  
    peak_freq = abs(freqs[peak_index])

    return peak_freq

def audio_callback(in_data, frame_count, time_info, status):
    global running
    audio_data = np.frombuffer(in_data, dtype=np.int16)  
    
    pitch = detect_pitch(audio_data, RATE)

    if pitch > 50:
        print(f"Detected Pitch: {pitch:.2f} Hz")

    return (in_data, pyaudio.paContinue if running else pyaudio.paComplete)

stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                input=True, frames_per_buffer=BUFFER_SIZE,
                stream_callback=audio_callback)

print("Running... Press Ctrl+C to stop.")

stream.start_stream()
try:
    while stream.is_active():
        pass  

except KeyboardInterrupt:
    running = False  
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("Exiting...")
