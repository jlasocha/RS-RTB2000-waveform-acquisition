# RS-RTB2000-waveform-acquisition

Minimal Python library for waveform and measurement acquisition from
Rohde & Schwarz RTB2000-series oscilloscopes over USB, via PyVISA.

## Requirements

- NI-VISA (or another VISA backend) installed and available on your system.
  PyVISA talks to the instrument through this backend — without it, PyVISA
  has nothing to connect to.
- Python 3.9+
- Python packages listed in `requirements.txt`

## Installation

```bash
git clone https://github.com/jlasocha/RS-RTB2000-waveform-acquisition.git
cd RS-RTB2000-waveform-acquisition
pip install -r requirements.txt
```

## Usage

```python
import RTB2000lib as rtb

rtb.list_instruments()      # optional: see what VISA can find
rtb.connect()                # connects to the first detected instrument

result = rtb.fast_acq("CHAN3")
rtb.save(result, filename="myfile", filetype="csv", output_dir="data/")

rtb.disconnect()
```

See `examples/basic_acquisition.py` for a complete runnable example.

## Acquisition modes

| Function     | Record length              | Triggers single-shot acquisition |
|--------------|-----------------------------|-----------------------------------|
| `fast_acq()` | Default (scope's current setting) | No — reads whatever is currently on screen |
| `max_acq()`  | Maximum available record length   | Yes |
| `dyn_acq()`  | Dynamic maximum (`DMAX`)          | Yes |

All three return a dictionary:

```python
{
    "t": ...,            # time axis, numpy array (s)
    "y": ...,             # voltage samples, numpy array (V)
    "channel": "CHAN3",
    "instrument": "Rohde&Schwarz,RTB2004,...",
    "timestamp": "2026-08-04 15:50:47",
    "points": 10000000,
    "dt": 8e-10,
    "t0": -0.0039992064,
    "acq_type": "MAX",
}
```

## Saving data

```python
rtb.save(result, filename="myfile", filetype="csv", output_dir="data/")
```

Supported `filetype` values: `"csv"`, `"npy"`.

## Known limitations

- Tested against a single RTB2004 unit over USB; other RTB2000-series
  models and interfaces (LAN/GPIB) are untested.
- `read_termination` is intentionally left unset on the VISA session.
  Binary waveform blocks can contain byte values identical to a line
  terminator; enabling termination-character detection truncates these
  transfers unpredictably. Message framing instead relies on the VISA
  END indicator (EOI), which PyVISA handles automatically. Do not
  re-enable `read_termination` for this reason.

## License

MIT — see `LICENSE`.
