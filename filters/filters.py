from scipy import signal
import numpy as np

# Build filters.
def make_filter(rate, freqs, btype):
    freqs = 2.0 * np.array(freqs, dtype=np.float64) / rate

    return signal.firwin(
        255,
        freqs,
        pass_zero=btype,
    )

def write_filter(rate, btype, filt):
    with open(f"filter-{rate}-{btype}.txt", "w") as f:
        for c in filt:
            print(f"{c:.20f}", file=f)

split1 = 300
split2 = 4000

filters = (
    (split1, 'lowpass'),
    ((split1, split2), 'bandpass'),
    (split2, 'highpass'),
)

for rate in [44100, 48000]:
    for freqs, btype in filters:
        f = make_filter(rate, freqs, btype)
        write_filter(rate, btype, f)
