import struct
import wave
import numpy as np

def get_waveform(file_path:str)->tuple:
    """from a file path give the (list(samples), samplerate) tuple"""
    with wave.open(file_path, 'rb') as sound:
        #nchannels = sound.getnchannels() if is stereo sound
        sampwidth = sound.getsampwidth()
        samplerate = sound.getframerate()
        nframes = sound.getnframes()
        frames = sound.readframes(nframes)
    #converts binary data to numerical values
    if sampwidth == 1:
        samples = struct.unpack('B'*nframes, frames) # unsigned char for 8-bit
    elif sampwidth == 2:
        samples = struct.unpack('h'*nframes, frames) # signed short for 16-bit
    elif sampwidth == 4:
        samples = struct.unpack('i'*nframes, frames) # signed int for 32-bit
    else:
        raise ValueError(f"Unsupported sample width: {sampwidth} bytes")
    return (list(samples), samplerate)

def get_cepstrum_spectral_envelope(waveform:list, samplerate:int, lifter_cutoff_quefrency:int=35):
    """from a waveform give his spectral envelope with the cepstrum method"""
    spectrum = np.fft.rfft(waveform, samplerate)
    log10_magnitude_spectrum = np.log10(np.abs(spectrum))
    cepstrum = np.fft.irfft(log10_magnitude_spectrum)
    liftred_cepstrum = [0 if i > lifter_cutoff_quefrency else x for i, x in enumerate(cepstrum)]
    smoothed_spectrum = np.abs(np.fft.rfft(liftred_cepstrum))
    return smoothed_spectrum

def get_formants(spectral_envelope:list)->list:
    formants = []
    for i in range(1, len(spectral_envelope) - 1):
        if spectral_envelope[i] > spectral_envelope[i-1] and spectral_envelope[i] > spectral_envelope[i+1]:
            formants.append(i)
    return formants

def framing(waveform:list, samplerate:int, frame_duration:float=0.1)->list:
    """split the waveform in several frames"""
    frame_size = int(samplerate * frame_duration)
    return [waveform[i:i + frame_size] for i in range(0, len(waveform), frame_size//2)]

def hamming_windowing(frame:list)->list:
    """windowing with the hamming function"""
    return list(frame*np.hamming(len(frame)))

def ajust_cutoff_quefrency(expected_first_formants:list, file_path:str)->tuple:
    to_compare = (float('inf'), 0)
    for i in range(20, 50):
        print("plop")
        formants_class = get_formants_class(frames, samplerate, i)
        mean_formants_list = from_formants_class_get_mean_formants(formants_class)
        dist = list_distance(expected_first_formants, mean_formants_list)
        print(dist)
        if dist < to_compare[0]:
            to_compare = (dist, i)
            print(to_compare)
    return to_compare

def get_formants_class(frames:list, samplerate:int, cepstrum_cutoff_quefrency=35)->list:
    """return a list of same class formant lists"""
    formants_class = []
    for i in range(len(frames)):
        frame = hamming_windowing(frames[i])
        spectral_envelope = get_cepstrum_spectral_envelope(frame, samplerate, cepstrum_cutoff_quefrency)
        formants = get_formants(list(spectral_envelope))
        if i == 0:
            for current_formant in formants:
                formants_class.append([current_formant])
        if i != 0:
            for current_formant in formants:
                min_distance = float('inf')
                nearest_formant_class = [] #init
                for formant_class in formants_class:
                    if np.abs(formant_class[-1] - current_formant) < min_distance:
                        min_distance, nearest_formant_class = np.abs(formant_class[-1] - current_formant), formant_class
                nearest_formant_class.append(current_formant)
    return formants_class


file_path = 'test_sounds/aaa.wav'
window_duration = 0.1
cepstrum_cutoff_quefrency = 30

(waveform, samplerate) = get_waveform(file_path)
frames = framing(waveform, samplerate, frame_duration=window_duration)
print(get_formants_class(frames, samplerate))
print(get_mean_formants_list(get_formants_class(frames, samplerate)))
















