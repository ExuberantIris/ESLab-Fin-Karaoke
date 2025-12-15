from typing import TypedDict
import json

class Rythmn(TypedDict):
    time: int
    duration: int
    pitch: str

rythmn: list[Rythmn] = []
last_node = None
base = "3"
bpm = 121
START_TIME = 16830

bar_start_time = START_TIME
def beat_to_bpm(beat):
    return int(60 * 1000 * 4 / 121 * beat)

with open("SomeThing.txt", "r") as f:
    skip = f.readline()
    skip = f.readline()

    while True:
        line = f.readline()
        if line == "":
            break
        elif line[0] == "#":
            continue

        bar_end_time = int(line.split()[-1])
        print(bar_end_time)
        beat_length = (bar_end_time - bar_start_time)
        cur_beat = 0
        for word in line.split():
            if word[0].isnumeric():
                break
            pitch, maybe_pitch, beat = "", "", ""
            if "_" not in word:
                beat = 0.25
                maybe_pitch = word
            else:
                maybe_pitch, beat_inv = tuple(word.split("_"))
                beat = 1.0 / float(beat_inv)

            if maybe_pitch[0] == "F" or maybe_pitch[0] == "C":
                if len(maybe_pitch) != 1 and maybe_pitch[1] == "s":
                    pass
                else:
                    maybe_pitch = maybe_pitch[0] + "s" + maybe_pitch[1:] 

            if not maybe_pitch[-1].isnumeric():
                pitch = maybe_pitch + base
            else:
                pitch = maybe_pitch

            if pitch[0] != "Z" and pitch[0] != "z": 
                if len(rythmn) and rythmn[-1]["pitch"] == pitch:
                    rythmn[-1]["duration"] += beat * beat_length

                rythmn.append({
                    "time": bar_start_time + cur_beat * beat_length,
                    "duration": beat * beat_length,
                    "pitch": pitch
                })
            
            cur_beat += beat
        
        bar_start_time = bar_end_time

#print(rythmn)
print("OK")
with open("AWholeNewWorld.json", "w") as f:
    json.dump(rythmn, f, indent=4)
