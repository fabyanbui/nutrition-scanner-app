import numpy as np
from typing import List, Tuple

def calculate_mae(ground_truth: List[float], predictions: List[float]) -> float:
    if not ground_truth or not predictions:
        return 0.0
    return float(np.mean(np.abs(np.array(ground_truth) - np.array(predictions))))

def calculate_mape(ground_truth: List[float], predictions: List[float]) -> float:
    if not ground_truth or not predictions:
        return 0.0
    gt = np.array(ground_truth)
    pred = np.array(predictions)
    # Avoid division by zero
    mask = gt != 0
    if not np.any(mask):
        return 0.0
    return float(np.mean(np.abs((gt[mask] - pred[mask]) / gt[mask])) * 100)

def calculate_rmse(ground_truth: List[float], predictions: List[float]) -> float:
    if not ground_truth or not predictions:
        return 0.0
    return float(np.sqrt(np.mean((np.array(ground_truth) - np.array(predictions)) ** 2)))
