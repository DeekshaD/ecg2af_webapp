import numpy as np
import h5py
from tensorflow.keras.models import load_model
from ml4h.models.model_factory import get_custom_objects
from ml4h.tensormap.ukb.survival import mgb_afib_wrt_instance2
from ml4h.tensormap.ukb.demographics import age_2_wide, af_dummy, sex_dummy3

# Constants
ECG_REST_LEADS = {
    'strip_I': 0, 'strip_II': 1, 'strip_III': 2, 'strip_V1': 3, 'strip_V2': 4, 'strip_V3': 5,
    'strip_V4': 6, 'strip_V5': 7, 'strip_V6': 8, 'strip_aVF': 9, 'strip_aVL': 10, 'strip_aVR': 11,
}
ECG_SHAPE = (5000, 12)
ECG_HD5_PATH = 'ukb_ecg_rest'

def load_ecg2af_model(model_path: str):
    """Load the ECG2AF model with custom objects."""
    output_tensormaps = {
        tm.output_name(): tm for tm in [
            mgb_afib_wrt_instance2,
            age_2_wide,
            af_dummy,
            sex_dummy3
        ]
    }
    custom_dict = get_custom_objects(list(output_tensormaps.values()))
    return load_model(model_path, custom_objects=custom_dict), output_tensormaps

def ecg_as_tensor(ecg_file: str) -> np.ndarray:
    """Convert an ECG file to a tensor."""
    with h5py.File(ecg_file, 'r') as hd5:
        tensor = np.zeros(ECG_SHAPE, dtype=np.float32)
        for lead in ECG_REST_LEADS:
            data = np.array(hd5[f'{ECG_HD5_PATH}/{lead}/instance_0'])
            tensor[:, ECG_REST_LEADS[lead]] = data
        tensor -= np.mean(tensor)
        tensor /= np.std(tensor) + 1e-6
    return tensor

def process_predictions(model, output_tensormaps: dict, predictions: list) -> dict:
    """Process the model predictions and format them for display."""
    results = {}

    for name, pred in zip(model.output_names, predictions):
        otm = output_tensormaps[name]
        if otm.is_survival_curve():
            intervals = otm.shape[-1] // 2
            days_per_bin = 1 + otm.days_window // intervals
            predicted_survivals = np.cumprod(pred[:, :intervals], axis=1)

            results['survival_curve'] = {
                'values': predicted_survivals[0],
                'days': [i * days_per_bin for i in range(intervals)],
                'af_risk': 1 - predicted_survivals[0, -1]
            }
        else:
            results[str(otm)] = pred[0]

    return results
