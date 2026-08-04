import numpy as np
import pyvisa as pv
import csv  
import datetime
from pathlib import Path
import time

## VISA CONNECTION
scope = None
dev_name = None

def list_instruments():
    rm = pv.ResourceManager()
    devices = rm.list_resources()
    print("Available instruments:")
    for i, d in enumerate(devices):
        print(f"  [{i}] {d}")

def connect(addr=0, timeout=10000, chunksize=8*1024*1024):
    global scope, dev_name
    rm = pv.ResourceManager()
    devices = rm.list_resources()
    dev_addr = devices[addr]  # example: 'USB0::0x1AB1::0x0641::DG1ZA...::INSTR' most of the time VISA instruments is the first one, that's why addr default value is 0.
    scope = rm.open_resource(dev_addr)
    scope.timeout = timeout  # Setting the time-out, I choose 10 s.
    scope.chunk_size = chunksize
    dev_name = scope.query('*IDN?')
    print('Connected to:', dev_name)

def disconnect():
    global scope, dev_name
    if scope is not None:
        scope.close()
        scope = None
        dev_name = None
        print("Disconnected.")
    else:
        print("You're already disconnected connected.")

## SUPPLEMENTARY FUNCTIONS
# Channel validation
def _validate_channel(chan):
    valid_channels = ("CHAN1", "CHAN2", "CHAN3", "CHAN4")
    if chan not in valid_channels:
        raise ValueError(f"Unknown channel: {chan}")
    if scope.query(f"{chan}:STAT?").strip() != "1":
        raise RuntimeError(f"{chan} is disabled.")

# Configuration of acquisition settings
def _configure_acq():
    scope.write("*CLS")             # Clears queue
    scope.write("FORM REAL")        # REAL data format
    scope.write("FORM:BORD LSBF")   # Little endian byte order

# Reading the measured data from the oscilloscope
def _read_waveform(chan):
    header = scope.query(f"{chan}:DATA:HEAD?").strip()
    _, _, n_points, _ = header.split(",")
    n_points = int(n_points)

    y = scope.query_binary_values(
        f"{chan}:DATA?",
        datatype="f",
        is_big_endian=False,
        container=np.array,
        expect_termination=False,
    )

    if len(y) != n_points:
        raise RuntimeError(f"Expected {n_points} samples, received {len(y)}.")

    t0 = float(scope.query(f"{chan}:DATA:XOR?"))
    dt = float(scope.query(f"{chan}:DATA:XINC?"))
    return y, n_points, t0, dt

# Writing the output of measurement.
def _write_output(chan, y, n_points, t0, dt, acq_type):
    t = t0 + np.arange(len(y)) * dt
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "t": t,
        "y": y,
        "channel": chan,
        "instrument": dev_name,
        "timestamp": timestamp,
        "points": n_points,
        "dt": dt,
        "t0": t0,
        "acq_type": acq_type,
    }

## MAIN ACQUISTION FUNCTIONS
def _acq(chan, points_mode, single_shot, acq_type):
    if scope is None:
        raise RuntimeError("Not connected. Call connect() first.")

    _validate_channel(chan)
    _configure_acq()
    scope.write(f"{chan}:DATA:POIN {points_mode}")
    scope.query(f"{chan}:DATA:POIN?")

    previous_state = None
    if single_shot:
        previous_state = scope.query("ACQ:STATE?").strip()
        scope.query("SING;*OPC?")  # blocks until acquisition completes

    try:
        y, n_points, t0, dt = _read_waveform(chan)
    except Exception as e:
        print(f"{acq_type} acquisition failed.")
        print(e)
        print("SCPI errors:")
        print(scope.query("SYST:ERR:ALL?"))
        raise
    finally:
        if single_shot:
            scope.write("RUN" if previous_state == "RUN" else "STOP")

    return _write_output(chan, y, n_points, t0, dt, acq_type)

def fast_acq(chan="CHAN1"):
    return _acq(chan, points_mode="DEF", single_shot=False, acq_type="FAST")

def max_acq(chan="CHAN1"):
    return _acq(chan, points_mode="MAX", single_shot=True, acq_type="MAX")

def dyn_acq(chan="CHAN1"):
    return _acq(chan, points_mode="DMAX", single_shot=True, acq_type="DYN")

## SAVING THE DATA FUNCTIONS
# Saving data to .csv file
def save_csv(output, filepath): 
    t = output["t"]
    y = output["y"]
    meta = (f"""ACQUISITION: {output['acq_type']}, INSTRUMENT: {output['instrument']}, CHANNEL: {output['channel']}, DATE: {output['timestamp']}, LENGTH: {output['points']}\nTime(s),Voltage(V)""")

    np.savetxt(
    filepath,
    np.column_stack((t, y)),
    delimiter=",",
    header=meta,
    comments=""
    )

# Saving data to .npy file
def save_npy(output, filepath):
    t = output["t"]
    y = output["y"]
    np.save(
        filepath,
        np.column_stack((t, y)),
        )

# Dictionary for different formats
SAVE_FORMATS = {
    "csv": save_csv,
    "npy": save_npy,
}

def save(output, filename="scope_data", filetype="csv", output_dir=None):
    # File-type validation
    valid_filetypes = ("csv", "npy")
    if filetype not in valid_filetypes:
        raise ValueError(f"Unknown filetype: {filetype}")

    # Target directory
    if output_dir is None:
        filepath = Path(f"{filename}.{filetype}")
    else:
        filepath = Path(output_dir) / f"{filename}.{filetype}"
        
    SAVE_FORMATS[filetype](output, filepath)
    