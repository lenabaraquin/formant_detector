import struct
import wave
import numpy as np
import matplotlib.pyplot as plt

class Formants:
    def __init__(self, file_path:str, frame_duration:float=0.1, cutoff_quefrency:int=35) -> None:
        self.file_path = file_path
        self.frame_duration = frame_duration
        self.cutoff_quefrency = cutoff_quefrency
        self._extract_waveform()

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

    def _extract_spectral_envelope(self, frame_waveform, lifter_cutoff_quefrency:int):
        """from a waveform give his spectral envelope with the cepstrum method"""
        spectrum = np.fft.rfft(frame_waveform, self.samplerate)
        log10_magnitude_spectrum = np.log10(np.abs(spectrum))
        cepstrum = np.fft.irfft(log10_magnitude_spectrum)
        liftred_cepstrum = [0 if i > lifter_cutoff_quefrency else x for i, x in enumerate(cepstrum)]
        smoothed_spectrum = np.abs(np.fft.rfft(liftred_cepstrum))
        return list(smoothed_spectrum)

    def _framing(self, frame_duration:float)->list:
        """split the waveform in several frames"""
        frame_size = int(self.samplerate * frame_duration)
        return [self.sound_waveform[i:i + frame_size] for i in range(0, len(self.sound_waveform), frame_size)]

    @staticmethod
    def _extract_formants(spectral_envelope:list)->list:
        """compute formants from the spectral envelope of a waveform""" #ameliorer la fonction de recherche de maxima locaux pour qu'elle soit robuste en cas de plateaux
        formants = []
        for i in range(1, len(spectral_envelope) - 1):
            if spectral_envelope[i] > spectral_envelope[i-1] and spectral_envelope[i] > spectral_envelope[i+1]: 
                formants.append(i)
        return formants

    @staticmethod
    def _hamming_windowing(frame:list)->list:
        """windowing with the hamming function"""
        return list(frame*np.hamming(len(frame)))

    def get_formants_class(self)->list:
        """return a list of same class formant lists"""
        frames = self._framing(self.frame_duration)
        formants_class = []
        for i in range(len(frames)):
            frame = self._hamming_windowing(frames[i])
            spectral_envelope = self._extract_spectral_envelope(frame, self.cutoff_quefrency)
            formants = self._extract_formants(list(spectral_envelope))
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

    def get_time_formant_vectors(self) -> list:
        frames = self._framing(self.frame_duration)
        formant_vectors = []
        for i in range(len(frames)):
            t = i*self.frame_duration
            frame = self._hamming_windowing(frames[i])
            spectral_envelope = self._extract_spectral_envelope(frame, self.cutoff_quefrency)
            formants = self._extract_formants(list(spectral_envelope))
            for formant in formants:
                formant_vectors.append((t, formant))
        return formant_vectors

    def get_mean_formants(self)->list:
        formants_class = self.get_formants_class()
        mean_formants = []
        for formant_class in formants_class:
            mean_formants.append(np.mean(formant_class))
        return mean_formants

def ajust_cutoff_quefrency(file_path:str, frame_duration:float=0.1, expected_first_formants:list, min_quefrency:int=10, max_quefrency:int=50):
    (dist, optimum_quefrency) = float('inf'), 0
    for quefrency in range(min_quefrency, max_quefrency):
        formants_for_quefrency = Formants(file_path, frame_duration, quefrency)
        mean_formants_for_quefrency = formants_for_quefrency.get_mean_formants()
        diff = 0
        for i in range(len(expected_first_formants)):
            diff += np.abs(expected_first_formants[i] - mean_formants_for_quefrency[i])
        if diff < dist:
            (dist, optimum_quefrency) = diff, quefrency 
    return optimum_quefrency

def plot_2D_vectors_from_list(vector_list:list, graph_title:str)->None:
    x_coords = [point[0] for point in vector_list]
    y_coords = [point[1] for point in vector_list]

    plt.plot(x_coords, y_coords, "o")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title(graph_title)
    plt.show()


aaa = Formants("test_sounds/aaa.wav", 0.01, 35)
iii = Formants("test_sounds/iii.wav", 0.01, 35)
uuu = Formants("test_sounds/uuu.wav", 0.01, 35)

aaa_formants = aaa.get_time_formant_vectors()
iii_formants = iii.get_time_formant_vectors()
uuu_formants = uuu.get_time_formant_vectors()





