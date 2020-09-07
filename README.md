# picoquant_tttr_to_ptu
This repository contains a Python script used to convert the time tags file generated via tttr mode from a PicoQuant Time tagging device to .ptu file, with the appropriate header.

Tested using time tags file generated using the PicoHarp300 tttr mode example script (see https://github.com/PicoQuant/PH300-v3.x-Demos/blob/master/demo_python_preliminary/64/TTTRmode/tttrmode.py) from a PicoQuant PicoHarp 300 device.
The converted time tags using the tttr_mode_to_ptu.py are then analyzed using the ReadPTU library provided here : https://github.com/QuantumPhotonicsLab/readPTU
