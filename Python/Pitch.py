from enum import IntEnum
from math import log2, floor

pitch_enum = ['C', 'Cs', 'D', 'Ds', 'E', 'F', 'Fs', 'G', 'Gs', 'A', 'As', 'B']
pitch_symb = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
Pitch = IntEnum('Pitch', pitch_enum) #C=1, A=10

type Octave = int
class PitchWithOctave(tuple):
    def __new__(cls, pitch: Pitch, octave: Octave):
        return super().__new__(cls, (pitch, octave))
    
    @classmethod
    def from_int(cls, i):
        base_pitch = Pitch(i % 12 + 1)
        octave = floor(i / 12) - 1
        return PitchWithOctave(base_pitch, octave)

    def __int__(self):
        # A = 10, C-1 = 0
        base_pitch, octave = self
        return octave * 12 + base_pitch + 11

    def next(self):
        self_int = int(self)
        return PitchWithOctave.from_int(self_int + 1)
    
    @classmethod
    def inclusive_range(cls, start, stop):
        start_int = int(start)
        stop_int = int(stop)
        for i in range(start_int, stop_int + 1):
            yield cls.from_int(i)
    
    @classmethod
    def reversed_inclusive_range(cls, start, stop):
        start_int = int(start)
        stop_int = int(stop)
        for i in range(stop_int, start_int - 1, -1):
            yield cls.from_int(i)

    def is_natural(self):
        base_pitch = self[0]
        return len(base_pitch.name) == 1
    
    def is_accidental(self):
        base_pitch = self[0]
        return len(base_pitch.name) != 1
    
    def __repr__(self):
        basic_pitch, octave = self
        return f"{pitch_symb[basic_pitch - 1]}{octave}"
#type PitchWithOctave = tuple[Pitch, Octave]

def freq_to_pitch(freq: float) -> PitchWithOctave: 
    #BASE_PITCH: pitchWithOctave = (Pitch.A, -2)
    BASE_FREQ = 6.875

    cur_freq = BASE_FREQ
    cur_octave = -1
    while cur_freq * 2 < freq:
        cur_freq *= 2
        cur_octave += 1
    
    log_cur_freq = log2(cur_freq)
    log_freq = log2(freq)
    difference = log_freq - log_cur_freq
    
    difference *= 12
    difference += 0.5 
    difference_int = floor(difference)

    if difference_int <= 2: 
        cur_freq = Pitch(difference_int + Pitch.A)
        cur_octave -= 1
    else:
        cur_freq = Pitch(difference_int - 2)
    
    return PitchWithOctave(cur_freq, cur_octave)

if __name__ == "__main__":
    C4 = PitchWithOctave(Pitch.C, 4)
    Ds6 = PitchWithOctave(Pitch.Ds, 6)
    for i in PitchWithOctave.inclusive_range(C4, Ds6):
        print(f"{i} ", end="")
    print()

    for i in range(100, 200):
        pitch_str = freq_to_pitch(i)
        print(f"({i}, {pitch_str})", end=" ")
        if (i % 20) == 19:
            print()