import time
from .datasets.loader import DatasetLoader
from .metrics.recognition import calculate_precision_recall_f1
from .metrics.nutrition import calculate_mae, calculate_mape
from .metrics.confidence import calculate_ece
from .reports.generator import ReportGenerator

class EvaluationPipeline:
    def __init__(self, dataset_dir: str, model_wrapper):
        self.loader = DatasetLoader(dataset_dir)
        self.model = model_wrapper
        
    def run(self, annotation_file: str):
        dataset = self.loader.load_dataset(annotation_file)
        
        ground_truth_foods = []
        pred_foods = []
        gt_calories = []
        pred_calories = []
        latencies = []
        
        for sample in dataset.samples:
            start_t = time.time()
            # In a real scenario, we load image and pass to model:
            # prediction = self.model.predict(sample.image_path)
            # We mock predictions for structural demonstration
            prediction = {
                "foods": [f.name for f in sample.foods],
                "calories": sum(f.nutrition.calories for f in sample.foods) * 0.95, # Mock 5% error
                "confidence": 0.85
            }
            latencies.append((time.time() - start_t) * 1000)
            
            ground_truth_foods.extend([f.name for f in sample.foods])
            pred_foods.extend(prediction["foods"])
            
            gt_calories.append(sum(f.nutrition.calories for f in sample.foods))
            pred_calories.append(prediction["calories"])
            
        p, r, f1 = calculate_precision_recall_f1(ground_truth_foods, pred_foods)
        mae = calculate_mae(gt_calories, pred_calories)
        
        metrics = {
            "food_precision": p,
            "food_recall": r,
            "food_f1": f1,
            "calories_mae": mae,
            "latency_ms": sum(latencies)/len(latencies) if latencies else 0,
            "worst_categories": ["Blurry images"] # Mock failure analysis
        }
        
        return metrics

    def generate_report(self, metrics, report_dir: str):
        gen = ReportGenerator(metrics, "NutritionScanner-v1")
        gen.to_json(f"{report_dir}/report.json")
        gen.to_markdown(f"{report_dir}/report.md")
