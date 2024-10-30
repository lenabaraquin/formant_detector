from scipy import signal
import matplotlib.pyplot as plt
import numpy as np
import wave
import struct


def get_spectrum(waveform:list)->list:
    spectrum = np.fft.rfft(waveform)
    return spectrum

def get_log10_magnitude_spectrum(spectrum:list)->list:
    magnitude_spectrum = []
    for i in spectrum:
        i = abs(i)
        i = np.log10(i)
        magnitude_spectrum.append(i)
    return magnitude_spectrum

def get_power_spectrum(spectrum:list)->list:
    power_spectrum = []
    for i in spectrum:
        i = abs(i)
        i = i*i
        power_spectrum.append(i)
    return power_spectrum

def get_cepstrum(power_spectrum:list)->list:
    cepstrum = []
    for i in power_spectrum:
        i = np.log10(i)
        cepstrum.append(i)
    cepstrum = np.fft.ifft(cepstrum)
    return cepstrum

def lowpass_lifter(cepstrum:list, cutoff_quefrency:int=30)->list:
    for i in range(len(cepstrum)):
        if i>cutoff_quefrency:
            cepstrum[i]=0
    liftred_cepstrum = cepstrum
    return liftred_cepstrum

def get_liftred_spectrum(liftred_cepstrum:list)->list:
    liftred_spectrum = np.abs(np.fft.rfft(liftred_cepstrum))
    return liftred_spectrum

def get_waveform(sound)->list:
    nframes = sound.getnframes()
    frames = sound.readframes(nframes)
    #converts binary data to int values
    samples = struct.unpack('h'*nframes, frames)
    #    # Déterminer le format pour 'struct.unpack'
    #    if sampwidth == 1:
    #        fmt = 'B'  # unsigned char pour 8-bit (1 octet)
    #    elif sampwidth == 2:
    #        fmt = 'h'  # signed short pour 16-bit (2 octets)
    #    elif sampwidth == 4:
    #        fmt = 'i'  # signed int pour 32-bit (4 octets)
    #    else:
    #        raise ValueError(f"Unsupported sample width: {sampwidth} bytes")
    #    fmt = '<' + fmt * nchannels  # Little-endian (<), répété pour chaque canal
    #
    #    # Convertir les frames en valeurs numériques
    #    samples = struct.unpack(fmt * nframes, frames)
    return samples

def get_local_maxima(signal:list)->list:
    local_maxima = []
    for i in range(1, len(signal) - 1):
        if signal[i] > signal[i-1] and signal[i] > signal[i+1]:
            local_maxima.append(i)
    return local_maxima

file_name = 'test_sounds/aaa.wav'
with wave.open(file_name, 'rb') as sound:
    nchannels = sound.getnchannels()
    sampwidth = sound.getsampwidth()
    framerate = sound.getframerate()
    nframes = sound.getnframes()

    filtred_power_spectrum = signal.butter(10, 0.5, fs=framerate)

    fig, ax = plt.subplots()
    waveform = get_waveform(sound)
    spectrum = get_spectrum(waveform)
    log10_magnitude_spectrum = get_log10_magnitude_spectrum(spectrum)
    power_spectrum  = get_power_spectrum(spectrum)
    cepstrum = get_cepstrum(power_spectrum)
    liftred_cepstrum = lowpass_lifter(cepstrum)
    liftred_spectrum = get_liftred_spectrum(liftred_cepstrum)
    to_plot = liftred_spectrum

    ax.plot(to_plot)
    plt.show()
    print(get_local_maxima(liftred_spectrum))
