# RS-RTB2000-waveform-acquisition

Minimal Python library for waveform and measurement acquisition from
Rohde&Schwarz RTB2000-series oscilloscopes over USB, via PyVISA. <br>
I used RTB2004 with USB-B connection but it should work fine in other cases too.

## Requirements

- NI-VISA (or another VISA backend) installed and available on your system.
- Python 3.9+
- Packages: NumPy, PyVisa

## Installation

```bash
git clone https://github.com/jlasocha/RS-RTB2000-waveform-acquisition.git
cd RS-RTB2000-waveform-acquisition
pip install -r requirements.txt
```

## How to use

```python
import RTB2000lib as rtb

rtb.list_instruments()       # optional: see what VISA can find
rtb.connect()                # connects to the first detected instrument

result = rtb.fast_acq("CHAN3") # fast acquisition from channel 3
rtb.save(result, filename="myfile", filetype="csv", output_dir="data/") # saving the data to myfile.csv

rtb.disconnect()
```

See `example.py` for a complete runnable example.

## Acquisition modes

| Function     | Record length              | Triggers single-shot acquisition |
|--------------|-----------------------------|-----------------------------------|
| `fast_acq()` | Default (scope's current setting) | No - reads whatever is currently on screen |
| `max_acq()`  | Maximum available record length   | Yes, then goes back to previous state |
| `dyn_acq()`  | Dynamic maximum (`DMAX`)          | Yes, then goes back to previous state |

For additional information about DEF, MAX and DMAX read the RTB2000 manual. <br>

All three return a dictionary:

```python
{
    "t": ...,            # time axis, numpy array (s)
    "y": ...,             # voltage samples, numpy array (V)
    "channel": "CHAN3",
    "instrument": "Rohde&Schwarz,RTB2004,...",
    "timestamp": "2026-08-04 15:50:47",
    "points": 10000000,    # Record length, depends on the acquisition mode and your settings on the oscilloscope.
    "dt": 8e-10,
    "t0": -0.0039992064,
    "acq_type": "MAX",
}
```

## Saving data

```python
rtb.save(result, filename="myfile", filetype="csv", output_dir="data/")
```

Currently supported `filetype` values: `"csv"`, `"npy"`.

## Known limitations
- `read_termination` is intentionally left unset on the VISA session.
  Binary waveform blocks can contain byte values identical to a line
  terminator; enabling termination-character detection truncates these
  transfers unpredictably. Message framing instead relies on the VISA
  END indicator (EOI), which PyVISA handles automatically. Do NOT
  include `read_termination` for this reason.

## License

MIT 
