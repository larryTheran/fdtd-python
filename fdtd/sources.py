"""Sources evaluated on the actual simulation time grid, without fixed buffers."""
import numpy as np


def waveform(t, frequency, kind="gaussian", tau_periods=0.5):
    tau = tau_periods / frequency
    t0 = 5 * tau
    if kind == "sine":
        # Smooth startup prevents a spurious broadband wavefront.
        ramp = np.sin(0.5 * np.pi * np.clip(np.asarray(t) / (4 / frequency), 0, 1)) ** 2
        return ramp * np.sin(2 * np.pi * frequency * np.asarray(t))
    pulse = np.exp(-((np.asarray(t) - t0) / tau) ** 2)
    if kind == "gaussian":
        return pulse
    if kind == "modulated":
        return pulse * np.sin(2 * np.pi * frequency * (np.asarray(t) - t0))
    raise ValueError(f"Unknown source: {kind}")
