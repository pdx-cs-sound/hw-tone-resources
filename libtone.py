# Copyright (c) 2018 Bart Massey
# [This program is licensed under the "MIT License"]
# Please see the file LICENSE in the source
# distribution of this software for license terms.

import argparse
from scipy import io
import numpy as np
import sounddevice as sd

# Size of output buffer in frames. Less than 1024 is not
# recommended, as most audio interfaces will choke
# horribly.
BUFFER_SIZE = 2048

# Read from a 16-bit WAV file. Returns the sample rate in
# samples per second, and the samples as a numpy array of
# IEEE 64-bit floats. The array will be 1D for mono data,
# and will be a 2D array of 2-element frames for stereo
# data.
def read_wav(filename):
    rate, data = io.wavfile.read(filename)
    assert data.dtype == np.int16
    data = data.astype(np.float64)
    data /= 32768
    return rate, data

# Write to a 16-bit WAV file. Data is in the same
# format produced by read_wav().
def write_wav(filename, rate, data):
    assert data.dtype == np.float64
    data *= 32767
    data = data.astype(np.int16)
    io.wavfile.write(filename, rate, data)

# Play a tone on the computer. Data is in the same format
# produced by read_wav().
def play(rate, wav):
    # Deal with stereo.
    channels = 1
    if wav.ndim == 2:
        channels = 2

    # Set up and start the stream.
    stream = sd.RawOutputStream(
        samplerate = rate,
        blocksize = BUFFER_SIZE,
        channels = channels,
        dtype = 'float32',
    )

    # Write the samples.
    stream.start()
    # https://stackoverflow.com/a/73368196
    indices = np.arange(BUFFER_SIZE, wav.shape[0], BUFFER_SIZE)
    samples = np.ascontiguousarray(wav, dtype=np.float32)
    for buffer in np.array_split(samples, indices):
        stream.write(buffer)

    # Tear down the stream.
    stream.stop()
    stream.close()

# Parse command-line arguments. Returns a struct whose
# elements are the arguments passed on the command line.
# See the `argparse` documentation for details.
def tone_args():
    argp = argparse.ArgumentParser()
    argp.add_argument(
        "--volume",
        help="volume in 3dB units (default 9 = 0dB, 0 = 0 output)",
        type=np.float64,
        default=9,
    )
    argp.add_argument(
        "--bass",
        help="bass emphasis in 3dB units (default 5 = 0dB, 0 = 0 output)",
        type=np.float64,
        default=5,
    )
    argp.add_argument(
        "--midrange",
        help="midrange emphasis in 3dB units (default 5 = 0dB, 0 = 0 output)",
        type=np.float64,
        default=5,
    )
    argp.add_argument(
        "--treble",
        help="treble emphasis in 3dB units (default 5 = 0dB, 0 = 0 output)",
        type=np.float64,
        default=5,
    )
    argp.add_argument(
        "--out",
        help="write to WAV file instead of playing",
    )
    argp.add_argument("wav", help="input audio file")
    return argp.parse_args()

