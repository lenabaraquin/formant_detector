import matplotlib.pyplot as plt
import struct
import wave
import numpy as np


def get_waveform(file_path:str)->tuple:
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
    frame_size = int(samplerate * frame_duration)
    return [waveform[i:i + frame_size] for i in range(0, len(waveform), frame_size//2)]

def hamming_windowing(frame:list)->list:
    return list(frame*np.hamming(len(frame)))

def plot_ball():
    to_plot=([], [])
    for i in np.arange(-2, 2, 0.01):
        for j in np.arange(-2, 2, 0.01):
            if 0.9 < weighted_distance((0,0), (i,j)) < 1.1:
                to_plot[0].append(i)
                to_plot[1].append(j)
    return to_plot

def weighted_distance(X1, X2, x_weight=0.5, y_weight=1.0):
    dx = np.abs(X1[0] - X2[0]) * x_weight
    dy = np.abs(X1[1] - X2[1]) * y_weight
    return np.amax([dx, dy])

def find_sequences(points, x_weight=0.5, y_weight=1.0, max_distance=300):
    sequences = []
    unvisited_points = set(points)
    
    while unvisited_points:
        current_sequence = []
        point = unvisited_points.pop()
        current_sequence.append(point)
        
        while True:
            nearest_point = None
            min_dist = float('inf')
            
            for other in unvisited_points:
                dist = weighted_distance(point, other, x_weight, y_weight)
                if dist < min_dist and dist <= max_distance:
                    nearest_point = other
                    min_dist = dist
            
            if nearest_point:
                current_sequence.append(nearest_point)
                unvisited_points.remove(nearest_point)
                point = nearest_point
            else:
                break
        
        sequences.append(current_sequence)
    
    return sequences

file_path = 'test_sounds/aaa.wav'
(waveform, samplerate) = get_waveform(file_path)
frames = framing(waveform, samplerate, frame_duration=0.1)
list_of_formants = []
for i in range(len(frames)):
    frame = hamming_windowing(frames[i])
    spectral_envelope = get_cepstrum_spectral_envelope(frame, samplerate, 30)
    formants = get_formants(list(spectral_envelope))
    list_of_formants.append(formants)

formants_in_time = [] #vectors in the time-frequency space
for i in range(len(list_of_formants)):
    for j in range(len(list_of_formants[i])):
        formants_in_time.append((i, list_of_formants[i][j]))

seq = find_sequences(formants_in_time)
for i in seq:
    print(i)

