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

def pseudo_distance(x:tuple, y:tuple, r:float)->float:
    x_1 = x[0]
    x_2 = x[1]
    y_1 = y[0]
    y_2 = y[1]
    d = np.sqrt(r*(x_1-y_1)**2 + (1/r)*(x_2-y_2)**2)
    return d

def get_nearest_point(point:tuple, points_to_compare:list)->tuple:
    r = 0.1
    dist_of_nearest_point = (pseudo_distance(point, points_to_compare[0], r),(0, 0))
    for x in points_to_compare:
        d = pseudo_distance(point, x, r)
        if d < dist_of_nearest_point[0]:
            dist_of_nearest_point = (d, x)
    return dist_of_nearest_point[1]

def plot_ball():
    to_plot=([], [])
    for i in np.arange(-2, 2, 0.01):
        for j in np.arange(-2, 2, 0.01):
            if 0.9 < pseudo_distance((0,0), (i,j), 0.1) < 1.1:
                to_plot[0].append(i)
                to_plot[1].append(j)
    return to_plot

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
        formants_in_time.append((i, list_of_formants[i][j], flag:=True))
print(formants_in_time)

#r = 0.1
for (time, formant, flag) formants_in_time:
    if flag:
        formant_set = {(time, formant)}
        #aller voir le point le plus proche parmi les flag true 
        # si inferieur à seuil, alors ajouter dans le set et passer le flag en false, sinon exit, ajouter formant_set à ce qui sera return et i suivant (avec une while ?)

#to_plot=plot_ball()
#plt.plot(to_plot[0], to_plot[1], 'o')
#plt.show()
