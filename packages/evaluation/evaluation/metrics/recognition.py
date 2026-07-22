from typing import List, Tuple
from collections import Counter

def calculate_precision_recall_f1(ground_truth: List[str], predictions: List[str]) -> Tuple[float, float, float]:
    """
    Calculate basic precision, recall, and F1 for a list of strings (foods or ingredients).
    A highly simplified exact-match evaluation for demonstration.
    """
    if not predictions and not ground_truth:
        return 1.0, 1.0, 1.0
    if not predictions or not ground_truth:
        return 0.0, 0.0, 0.0
        
    gt_lower = [g.lower() for g in ground_truth]
    pred_lower = [p.lower() for p in predictions]
    
    true_positives = sum(1 for p in pred_lower if p in gt_lower)
    
    precision = true_positives / len(pred_lower) if pred_lower else 0.0
    recall = true_positives / len(gt_lower) if gt_lower else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return precision, recall, f1

def calculate_top_k_accuracy(ground_truth: List[str], predictions_with_scores: List[Tuple[str, float]], k: int = 1) -> float:
    """
    Calculates if any of the ground truth items exist in the top-k predictions.
    """
    if not ground_truth or not predictions_with_scores:
        return 0.0
        
    top_k_preds = sorted(predictions_with_scores, key=lambda x: x[1], reverse=True)[:k]
    top_k_names = [p[0].lower() for p in top_k_preds]
    gt_lower = [g.lower() for g in ground_truth]
    
    for gt in gt_lower:
        if gt in top_k_names:
            return 1.0
    return 0.0
