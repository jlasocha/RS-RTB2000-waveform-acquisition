###

# Basic usage example for RTB2000lib.
# Connects to the first detected VISA instrument, grabs the maximum-length
# waveform record on CHAN3, saves it to CSV, and disconnects.

###

import sys
from pathlib import Path

# Allow running this script directly from the examples/ folder without
# installing the library as a package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import RTB2000lib as rtb


def main():
    rtb.list_instruments()
    rtb.connect()

    try:
        result = rtb.max_acq("CHAN3")
        print(f"Acquired {result['points']} points on {result['channel']}")

        rtb.save(result, filename="example_acquisition", filetype="csv", output_dir="data/")
        print("Saved to data/example_acquisition.csv")
    finally:
        rtb.disconnect()


if __name__ == "__main__":
    main()
