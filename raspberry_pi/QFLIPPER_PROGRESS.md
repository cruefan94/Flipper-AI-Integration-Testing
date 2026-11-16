# qFlipper progress monitoring on Raspberry Pi 4B

Read-only opt-in prototype. It does not flash devices, control qFlipper, or read GUI progress bars. It only reports percentages explicitly written in a user-selected qFlipper log. Missing evidence means UNKNOWN, not 0%.

Run from the repo root:

    python3 raspberry_pi/qflipper_progress.py --log /path/to/real/qflipper.log --follow
    python3 -m unittest discover -s raspberry_pi -p 'test_qflipper_progress.py'

The log path is an example; discover the actual location on your Pi. If qFlipper doesn't log percentages, use the qFlipper GUI. Output is newline-delimited JSON. A reported_complete log line does not prove a successful flash; manually verify reboot and firmware version. No automatic retry, no USB access, no device writes. Synthetic tests do not prove physical behavior.