import struct
import wave
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

class Formants:
    def __init__(self, file_path:str, frame_duration:float=0.1, cutoff_quefrency:int=35) -> None:
        self.file_path = file_path
        self.frame_duration = frame_duration
        self.cutoff_quefrency = cutoff_quefrency
        self._extract_waveform()
        self._extract_spectrogram()


    def _extract_waveform(self)-> None:
        """from a file path extract samplerate and list of samples"""
        with wave.open(self.file_path, 'rb') as sound:
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
        self.samplerate = samplerate
        self.sound_waveform = list(samples)
        self.sound_duration = len(samples)/samplerate

    def _extract_spectral_envelope(self, analyzed_waveform):
        """from a waveform give his spectral envelope with the cepstrum method"""
        spectrum = np.fft.rfft(analyzed_waveform, self.samplerate)
        log10_magnitude_spectrum = np.log10(np.abs(spectrum))
        cepstrum = np.fft.irfft(log10_magnitude_spectrum)
        liftred_cepstrum = [0 if i > self.cutoff_quefrency else x for i, x in enumerate(cepstrum)]
        smoothed_spectrum = np.abs(np.fft.rfft(liftred_cepstrum))
        return list(smoothed_spectrum)

    def _framing(self)->list:
        """split the waveform in several frames"""
        frame_size = int(self.samplerate * self.frame_duration)
        self.middle_frame = self.sound_waveform[len(self.sound_waveform)//2:len(self.sound_waveform)//2+frame_size]
        return [self.sound_waveform[i:i + frame_size] for i in range(0, len(self.sound_waveform), frame_size)]

    @staticmethod
    def _hamming_windowing(frame:list)->list:
        """windowing with the hamming function"""
        return list(frame*np.hamming(len(frame)))

    def _extract_spectrogram(self)->None:
        """return a list of (time, frequency, intensity) tuples, the time window length depend on self.frame_duration"""
        spectrogram = []
        matrix_spectrogram = []
        splited_waveform = self._framing()
        ham_splited_waveform = []
        for frame in splited_waveform:
            ham_splited_waveform.append(self._hamming_windowing(frame))
        for i in range(len(ham_splited_waveform)):
            time_slice = [] #list to add to matrix_spectrogram
            frame = ham_splited_waveform[i]
            time = i*self.frame_duration
            spectral_envelope = self._extract_spectral_envelope(frame)
            for j in range(len(spectral_envelope)):
                frequency = j
                intensity = spectral_envelope[j]
                spectrogram.append((time, frequency, intensity))
                time_slice.append(intensity)
            matrix_spectrogram.append(time_slice)
        self.spectrogram = spectrogram
        self.matrix_spectrogram = matrix_spectrogram

    @staticmethod
    def _extract_formants(spectral_envelope:list)->list:
        """compute formants from the spectral envelope of a waveform""" #ameliorer la fonction de recherche de maxima locaux pour qu'elle soit robuste en cas de plateaux
        formants = []
        for i in range(1, len(spectral_envelope) - 1):
            if spectral_envelope[i] > spectral_envelope[i-1] and spectral_envelope[i] > spectral_envelope[i+1]: 
                formants.append(i)
        return formants

    def get_formants_matrix(self)->list:
        formants_matrix = []
        for time_slice in self.matrix_spectrogram:
            formants_matrix.append(self._extract_formants(time_slice))
        return formants_matrix

aaa_file_path = "test_sounds/aaa.wav"
iii_file_path = "test_sounds/iii.wav"
uuu_file_path = "test_sounds/uuu.wav"

#with tuned cutoff_quefrency
aaa = Formants(aaa_file_path, 0.2, 31)
iii = Formants(iii_file_path, 0.2, 38)
uuu = Formants(uuu_file_path, 0.2, 49)

print(aaa.sound_duration)
print(aaa.matrix_spectrogram)



aaa_expected_formants = [900, 1400, 2650]
iii_expected_formants = [255, 2100, 3650]
uuu_expected_formants = [350, 570, 2600]
