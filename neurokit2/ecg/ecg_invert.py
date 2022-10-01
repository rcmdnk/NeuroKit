import numpy as np

from numba import njit
from .ecg_clean import ecg_clean


def ecg_invert(ecg_signal, sampling_rate=1000, check_inverted=True):
    """**ECG signal inversion**

    Checks whether an ECG signal is inverted, and if so, corrects for this inversion.

    Parameters
    ----------
    ecg_signal : Union[list, np.array, pd.Series]
        The raw ECG channel.
    sampling_rate : int
        The sampling frequency of ``ecg_signal`` (in Hz, i.e., samples/second). Defaults to 1000.
    check_inverted : bool, optional
        Whether to check whether the signal is inverted before inverting it. The default is True.
        If False, always returns the inverted input signal regardless of whether the input was inverted.
    Returns
    -------
    array
        Vector containing the corrected ECG signal.
    Examples
    --------
    **Example 1**: With an inverted ECG signal
    .. ipython:: python
      import neurokit2 as nk
      import matplotlib.pyplot as plt
      plt.rc('font', size=8)
      # Download data
      data = nk.data("bio_resting_5min_100hz")
      # Invert ECG signal
      ecg_inverted = data["ECG"] * -1 + 2 * np.nanmean(data["ECG"])
      # Fix inversion
      ecg_fixed = nk.ecg_invert(ecg_inverted, sampling_rate=100)

      # Plot inverted ECG and fixed ECG
      @savefig p_ecg_inverted1.png scale=100%
      fig, ax = plt.subplots(2, 1, sharex=True, sharey=True)
      ax[0].plot(ecg_inverted[:sampling_rate*5])
      ax[0].set_title("Inverted ECG")
      ax[1].plot(ecg_fixed[:sampling_rate*5])
      ax[1].set_title("Fixed ECG")
      fig.show()
    """
    inverted_ecg_signal = np.array(ecg_signal) * -1 + 2 * np.nanmean(ecg_signal)
    if check_inverted:
        if _ecg_inverted(ecg_signal, sampling_rate=sampling_rate):
            return inverted_ecg_signal
        else:
            return ecg_signal
    else:
        return inverted_ecg_signal


def _ecg_inverted(ecg_signal, sampling_rate=1000, window_time=2.0):
    """Checks whether an ECG signal is inverted."""
    ecg_cleaned = ecg_clean(ecg_signal, sampling_rate=sampling_rate)
    # take the median of the original value of the maximum of the squared signal
    # over a window where we would expect at least one heartbeat
    med_max = np.nanmedian(_roll_orig_max_squared(ecg_cleaned, 
                                                  window=int(window_time * sampling_rate)))
    return med_max < np.nanmean(ecg_cleaned)


@njit
def _roll_orig_max_squared(x, window=2000):
    """With a rolling window, takes the original value corresponding to the maximum of the squared signal."""
    roll_x = []
    for i in range(len(x) - window):
        roll_x.append(x[i : i + window][np.argmax(np.square(x[i : i + window]))])
    return roll_x
