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

def from_file_get_formant_matrix(file_path:str, window_duration:float, cepstrum_cutoff_quefrency:int)->list:
    (waveform, samplerate) = get_waveform(file_path)
    frames = framing(waveform, samplerate, frame_duration=window_duration)
    formant_matrix = []
    for i in range(len(frames)):
        frame = hamming_windowing(frames[i])
        spectral_envelope = get_cepstrum_spectral_envelope(frame, samplerate, cepstrum_cutoff_quefrency)
        formants = get_formants(list(spectral_envelope))
        formant_matrix.append(formants)
    return formant_matrix

def take_formants_in_time_frequency_space(formant_matrix:list)->list:
    formants_in_time = [] #vectors in the time-frequency space
    for i in range(len(formant_matrix)):
        for j in range(len(formant_matrix[i])):
            formants_in_time.append((i, formant_matrix[i][j]))
    return formants_in_time

def weighted_distance(X1, X2, weight=0.5):
    dx = np.abs(X1[0] - X2[0]) * weight
    dy = np.abs(X1[1] - X2[1]) * (1/weight)
    return np.amax([dx, dy])

def find_sequences(points, weight=0.5, max_distance=300):
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
                dist = weighted_distance(point, other, weight)
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

def get_mean_formants_list(formants_sequences:list)->list:
    mean_formants_list = []
    for i in formants_sequences:
        mean_formants_list.append(np.mean(i))
    mean_formants_list.sort()
    return mean_formants_list

def from_formant_matrix_get_mean_formants(formant_matrix:list, squeezing_coefficient:float, max_dist_to_regroup:int)->list:
    formants_in_time = take_formants_in_time_frequency_space(formant_matrix)
    formants_sequences = find_sequences(formants_in_time, squeezing_coefficient, max_dist_to_regroup)
    mean_formants_list = get_mean_formants_list(formants_sequences)
    return mean_formants_list

def list_distance(list_1:list, list_2:list)->float:
    dist = 0
    for i in range(len(list_1)):
        dist += np.abs(list_1[i] - list_2[i])
    return dist

def ajust_cutoff_quefrency(expected_first_formants:list, file_path:str)->tuple:
    to_compare = (float('inf'), 0)
    for i in range(20, 50):
        print("plop")
        formant_matrix = from_file_get_formant_matrix(file_path, window_duration=0.1, cepstrum_cutoff_quefrency=i)
        mean_formants_list = from_formant_matrix_get_mean_formants(formant_matrix, squeezing_coefficient=0.5, max_dist_to_regroup=300)
        dist = list_distance(expected_first_formants, mean_formants_list)
        print(dist)
        if dist < to_compare[0]:
            to_compare = (dist, i)
            print(to_compare)
    return to_compare


file_path = 'test_sounds/aaa.wav'
formant_matrix = from_file_get_formant_matrix(file_path, window_duration=0.1, cepstrum_cutoff_quefrency=30)
mean_formants_list = from_formant_matrix_get_mean_formants(formant_matrix, squeezing_coefficient=0.5, max_dist_to_regroup=300)
print(mean_formants_list)

expected_first_formants = [930, 1400, 2700]
print(ajust_cutoff_quefrency(expected_first_formants, file_path))


















