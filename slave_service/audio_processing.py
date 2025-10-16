"""Audio processing module for analyzing audio files"""
import base64
import json
import wave
import numpy as np

def process_audio(audio_files):
    """
    Process audio files to extract features like duration, frequency analysis, etc.
    Returns audio analysis for each file.
    """
    results = []
    for audio_file in audio_files:
        try:
            # Read audio data (assuming WAV format for simplicity)
            audio_data = audio_file.stream.read()
            
            # Try to parse as WAV
            try:
                # Save to temporary bytes and analyze
                import io
                audio_io = io.BytesIO(audio_data)
                
                with wave.open(audio_io, 'rb') as wav_file:
                    frames = wav_file.readframes(-1)
                    sample_rate = wav_file.getframerate()
                    channels = wav_file.getnchannels()
                    sample_width = wav_file.getsampwidth()
                    duration = len(frames) / (sample_rate * channels * sample_width)
                    
                    # Convert to numpy array for basic analysis
                    if sample_width == 2:
                        audio_array = np.frombuffer(frames, dtype=np.int16)
                    else:
                        audio_array = np.frombuffer(frames, dtype=np.uint8)
                    
                    # Basic audio features
                    rms_energy = np.sqrt(np.mean(audio_array**2))
                    zero_crossings = np.sum(np.diff(np.sign(audio_array)) != 0)
                    
                    audio_analysis = {
                        "duration_seconds": duration,
                        "sample_rate": sample_rate,
                        "channels": channels,
                        "sample_width": sample_width,
                        "rms_energy": float(rms_energy),
                        "zero_crossings": int(zero_crossings),
                        "file_size_bytes": len(audio_data)
                    }
            except:
                # Fallback for non-WAV files
                audio_analysis = {
                    "duration_seconds": "unknown",
                    "sample_rate": "unknown",
                    "channels": "unknown",
                    "file_size_bytes": len(audio_data),
                    "format": "non-wav"
                }
            
            # Encode as base64 JSON
            result_str = base64.b64encode(json.dumps(audio_analysis).encode()).decode('utf-8')
            
            results.append({
                "filename": audio_file.filename,
                "audio_data": result_str
            })
        except Exception as e:
            print(f"Error processing audio file {audio_file.filename}: {e}")
    
    return results