import matplotlib.pyplot as plt
import numpy as np
import wave
import struct

def get_waveform(file_path:str)->list:
    with wave.open(file_name, 'rb') as sound:
        nchannels = sound.getnchannels()
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
    return frame*np.hamming(len(frame))

file_name = 'test_sounds/aaa.wav'
(waveform, samplerate) = get_waveform(file_name)
frames = framing(waveform, samplerate, frame_duration=0.1)
list_of_formants = []
for i in range(len(frames)):
    frame = hamming_windowing(frames[i])
    spectral_envelope = get_cepstrum_spectral_envelope(frame, samplerate, 30)
    formants = get_formants(spectral_envelope)
    list_of_formants.append(formants)

for i in range(len(list_of_formants)-1):
    print(list_of_formants[i])
#    k = 0
#    for j in range(len(list_of_formants[i])):
#        if i==0 or i==1:
#            print(f"ligne {i}, colonne {j}")
#            print(list_of_formants[i])
#            print(list_of_formants[i+1])
#            print(list_of_formants[i+1][j])
#        r = 0.1
#        interval = range(int(list_of_formants[i][j]-list_of_formants[i][j]*r), int(list_of_formants[i][j]-list_of_formants[i][j]*r))
#        if list_of_formants[i+1][j-k] not in interval:
#            list_of_formants[i+1].insert(j, 0)
#            k+=1 #it seems to read unmodified row i+1, so the column counter has to be increase

#    to_plot = spectral_envelope
#    fig, ax = plt.subplots()
#    ax.plot(to_plot)
#    plt.show()
