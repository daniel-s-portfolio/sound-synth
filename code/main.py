import sys
import numpy as np
import sounddevice as sd
import mido
from scipy.signal import sawtooth

SAMPLE_RATE = 44100
FREQ = 440.0
IDLE = 0
ATTACK = 1
SUSTAIN = 2
RELEASE = 3

class Synth:
    def __init__(self):
        self.sample_rate = SAMPLE_RATE
        self.phase = 0.0
        self.freq = FREQ
        self.active_note = None

        # -3dBFS is about 0.708
        self.max_amp = 0.708 
        
        # 10ms attack and release
        attack_time = 0.01 
        release_time = 0.01
        
        self.attack_rate = self.max_amp / (attack_time * self.sample_rate)
        self.release_rate = self.max_amp / (release_time * self.sample_rate)

        # envelope state tracker
        self.amplitude = 0.0
        self.env_state = IDLE

    def note_on(self, note, velocity):
        # treat 0-velocity KEY ON as KEY OFF
        if velocity == 0:
            self.note_off(note)
            return
            
        self.active_note = note
        
        # MIDI to frequency conversion
        self.freq = FREQ * (2.0 ** ((note - 69) / 12.0))
        
        # trigger attack phase
        self.env_state = ATTACK

    def note_off(self, note):
        # only release if the key lifted is the one currently playing
        if note == self.active_note:
            self.env_state = RELEASE
            self.active_note = None

    def audio_callback(self, outdata, frames, time, status):
        if status:
            print(status, file=sys.stderr)

        phase_increment = self.freq / self.sample_rate
        phases = self.phase + np.arange(frames) * phase_increment
        
        # update the starting phase for the next callback block
        self.phase = (self.phase + frames * phase_increment) % 1.0

        # generate sawtooth wave with scipy
        wave = sawtooth(2 * np.pi * (phases % 1.0))

        # generate AR envelope
        env = np.zeros(frames)
        for i in range(frames):
            if self.env_state == ATTACK:
                self.amplitude += self.attack_rate
                if self.amplitude >= self.max_amp:
                    self.amplitude = self.max_amp
                    self.env_state = SUSTAIN
            
            elif self.env_state == RELEASE:
                self.amplitude -= self.release_rate
                if self.amplitude <= 0.0:
                    self.amplitude = 0.0
                    self.env_state = IDLE

            env[i] = self.amplitude

        # apply envelope to wave, write to output buffer (reshape for sounddevice 1-channel output)
        outdata[:] = (wave * env).reshape(-1, 1)

def main():
    synth = Synth()

    # detect available MIDI ports
    available_ports = mido.get_input_names()
    
    if not available_ports:
        print("no MIDI inputs detected, exiting")
        return

    # list ports, bind to the first available MIDI port
    print("available MIDI ports:")
    for i, port in enumerate(available_ports):
        print(f"[{i}] {port}")
    selected_port = available_ports[0]
    print(f"\nbinding to {selected_port}")
    print("synthesizer running...")

    try:
        with sd.OutputStream(samplerate=SAMPLE_RATE, channels=1, 
                             callback=synth.audio_callback, latency='low'):
            
            # open MIDI port and block the main thread waiting for events
            with mido.open_input(selected_port) as inport:
                for msg in inport:
                    if msg.type == 'note_on':
                        synth.note_on(msg.note, msg.velocity)
                    elif msg.type == 'note_off':
                        synth.note_off(msg.note)
                        
    except KeyboardInterrupt:
        print("\nexiting...")
    except Exception as e:
        print(f"\nerror: {e}")


if __name__ == "__main__":
    main()