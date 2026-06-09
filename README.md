### Daniel Schuster, CS-516 Computers Sound and Music
- Program to create a MIDI synthesizer using Python
- It is set up to detect active MIDI ports and connect to the first available port.  If you have multiple MIDI inputs, you may have to edit line 103 of main.py to select a different port besides the first one from the listing of ports.
- I have tested the program using loopMIDI and VMPK.  loopMIDI was necessary for me when running the program on Windows 11, if you are on a different OS you may need a different program.  If you use the setup with loopMIDI and VMPK, you will need to do the following:
    - Start loopMIDI, add a port (default name is loopMIDI Port)
    - Leave loopMIDI running
    - Start VMPK
    - In VMPK, go to Edit -> MIDI Connections and select the chosen loopMIDI Port for the Output MIDI Connection option
    - Perform the setup steps below as needed, then run the main.py script
    - Stop main.py when desired using ctrl-C
    - loopMIDI can now be closed when desired

### Usage
```
# optional: setup virtual environment
python -m venv .venv
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt

# ensure a MIDI input is setup before running the program,
# otherwise it will simply display an error message and exit. 
# see above for details on setting up a virtual keyboard

# run program (detects available MIDI ports, uses first available)
python code/main.py
```
