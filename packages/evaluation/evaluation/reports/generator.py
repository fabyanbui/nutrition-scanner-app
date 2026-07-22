import json
import csv
from typing import Dict, Any

class ReportGenerator:
    def __init__(self, metrics: Dict[str, Any], model_name: str):
        self.metrics = metrics
        self.model_name = model_name
        
    def to_json(self, filepath: str):
        data = {
            "model": self.model_name,
            "metrics": self.metrics
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
            
    def to_markdown(self, filepath: str):
        md = f"# Evaluation Report: {self.model_name}\n\n"
        md += "## Overview\n"
        md += f"- **Food Recognition F1**: {self.metrics.get('food_f1', 0):.2f}\n"
        md += f"- **Nutrition MAE (Calories)**: {self.metrics.get('calories_mae', 0):.2f} kcal\n"
        md += f"- **Average Latency**: {self.metrics.get('latency_ms', 0)} ms\n\n"
        
        md += "## Failure Analysis\n"
        worst = self.metrics.get('worst_categories', [])
        md += f"Worst performing categories: {', '.join(worst) if worst else 'N/A'}\n"
        
        with open(filepath, 'w') as f:
            f.write(md)
