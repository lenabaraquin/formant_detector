import matplotlib.pyplot as plt
import numpy as np
import wave
import struct


def get_spectrum(waveform:list, samplerate:int)->list:
    spectrum = np.fft.rfft(waveform, samplerate)
    return spectrum

def get_cepstrum(spectrum:list)->list:
    return np.fft.ifft(np.log10(np.abs(spectrum)))

def get_liftred_cepstrum(cepstrum:list, cutoff_quefrency:int=35)->list:
    for i in range(len(cepstrum)):
        if i>cutoff_quefrency:
            cepstrum[i]=0
    liftred_cepstrum = cepstrum
    return liftred_cepstrum

def get_smoothed_spectrum(liftred_cepstrum:list)->list:
    return np.abs(np.fft.rfft(liftred_cepstrum))

def get_cepstrum_spectral_envelope(waveform:list, samplerate:int, lifter_cutoff_quefrency:int=35):
    spectrum = get_spectrum(waveform, samplerate)
    cepstrum = get_cepstrum(spectrum)
    liftred_cepstrum = get_liftred_cepstrum(cepstrum, lifter_cutoff_quefrency)
    smoothed_spectrum = get_smoothed_spectrum(liftred_cepstrum)
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

def get_waveform(sound, sampwidth)->list:
    nframes = sound.getnframes()
    frames = sound.readframes(nframes)
    #converts binary data to numerical values
    if sampwidth == 1:
        samples = struct.unpack('B'*nframes, frames) # unsigned char pour 8-bit (1 octet)
    elif sampwidth == 2:
        samples = struct.unpack('h'*nframes, frames) # signed short pour 16-bit (2 octets)
    elif sampwidth == 4:
        samples = struct.unpack('i'*nframes, frames) # signed int pour 32-bit (4 octets)
    else:
        raise ValueError(f"Unsupported sample width: {sampwidth} bytes")
    return list(samples)


file_name = 'test_sounds/aaa.wav'
with wave.open(file_name, 'rb') as sound:
    nchannels = sound.getnchannels()
    sampwidth = sound.getsampwidth()
    samplerate = sound.getframerate()
    nsamples = sound.getnframes()

    waveform = get_waveform(sound, sampwidth)
    frames = framing(waveform, samplerate, frame_duration=0.1)
    for i in range(len(frames)):
        spectral_envelope = get_cepstrum_spectral_envelope(frames[i], samplerate, 35)
        formants = get_formants(spectral_envelope)
        print(formants)

    to_plot = spectral_envelope
    fig, ax = plt.subplots()
    ax.plot(to_plot)
    plt.show()
