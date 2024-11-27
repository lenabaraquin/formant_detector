import struct
import wave
import numpy as np

class Formants:
    def __init__(self, file_path:str, frame_duration:float, cutoff_quefrency:int=35) -> None:
        self.file_path = file_path
        self.frame_duration = frame_duration
        self.cutoff_quefrency = cutoff_quefrency
        self.extract_waveform()

    def extract_waveform(self)-> None:
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
        self.waveform = list(samples)
        
    def get_cepstrum_spectral_envelope(self, waveform, lifter_cutoff_quefrency:int):
        """from a waveform give his spectral envelope with the cepstrum method"""
        spectrum = np.fft.rfft(waveform, self.samplerate)
        log10_magnitude_spectrum = np.log10(np.abs(spectrum))
        cepstrum = np.fft.irfft(log10_magnitude_spectrum)
        liftred_cepstrum = [0 if i > lifter_cutoff_quefrency else x for i, x in enumerate(cepstrum)]
        smoothed_spectrum = np.abs(np.fft.rfft(liftred_cepstrum))
        return list(smoothed_spectrum)

    def framing(self, frame_duration:float)->list:
        """split the waveform in several frames"""
        frame_size = int(self.samplerate * frame_duration)
        return [self.waveform[i:i + frame_size] for i in range(0, len(self.waveform), frame_size//2)]

    @staticmethod
    def get_formants(spectral_envelope:list)->list:
        formants = []
        for i in range(1, len(spectral_envelope) - 1):
            if spectral_envelope[i] > spectral_envelope[i-1] and spectral_envelope[i] > spectral_envelope[i+1]:
                formants.append(i)
        return formants
    
    @staticmethod
    def hamming_windowing(frame:list)->list:
        """windowing with the hamming function"""
        return list(frame*np.hamming(len(frame)))

    def get_formants_class(self, frame_duration:float=0.1, cepstrum_cutoff_quefrency=35)->list:
        """return a list of same class formant lists"""
        frames = self.framing(frame_duration)
        formants_class = []
        for i in range(len(frames)):
            frame = self.hamming_windowing(frames[i])
            spectral_envelope = self.get_cepstrum_spectral_envelope(frame, cepstrum_cutoff_quefrency)
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

blop = Formants(file_path, window_duration, cepstrum_cutoff_quefrency)
print(blop.get_formants_class())
