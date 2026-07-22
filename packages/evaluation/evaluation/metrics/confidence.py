import numpy as np
from typing import List, Tuple

def calculate_ece(accuracies: List[float], confidences: List[float], num_bins: int = 10) -> float:
    """
    Expected Calibration Error (ECE)
    """
    if not accuracies or not confidences:
        return 0.0
        
    bins = np.linspace(0.0, 1.0, num_bins + 1)
    bin_indices = np.digitize(confidences, bins, right=True) - 1
    
    ece = 0.0
    total_samples = len(accuracies)
    
    for i in range(num_bins):
        bin_mask = bin_indices == i
        if np.any(bin_mask):
            bin_acc = np.mean(np.array(accuracies)[bin_mask])
            bin_conf = np.mean(np.array(confidences)[bin_mask])
            bin_weight = np.sum(bin_mask) / total_samples
            ece += bin_weight * np.abs(bin_acc - bin_conf)
            
    return float(ece)
