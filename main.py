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

formants_in_time = [] #vectors in the time-frequency space
for i in range(len(list_of_formants)):
    for j in range(len(list_of_formants[i])):
        formants_in_time.append((i,list_of_formants[i][j]))
print(formants_in_time)

for i in range(len(formants_in_time)):
    (time, formant)=formants_in_time[i]
    #formant_set = {(time, formant)}
    #def set de tous les formants des couples de forme (time+1, formant)
    #def set formant-r, formant+r
    #set1.intersection(set2)
    #new_formant = si taille 1, continuer, si taille plus de 1 prendre le plus proche de formant, si inter vide, stop et passe à formants_in_time[i+1]
    #formant_set.append(new_formant)
    #recommancer avec (time+1, formant) jusqu'a ce que l'intersection soit vide
    #envoyer formant_set dans une liste à return 

#    to_plot = spectral_envelope
#    fig, ax = plt.subplots()
#    ax.plot(to_plot)
#    plt.show()
