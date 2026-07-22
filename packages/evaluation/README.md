# AI Evaluation Framework (Phase 3.5)

This package contains the evaluation framework to measure and continuously improve the quality of the Nutrition Scanner's AI models. It is built for developers and researchers to systematically benchmark models using Golden Datasets.

## Evaluation Architecture

The framework consists of:
1. **Dataset Loader**: Parses the Golden Dataset (`Dataset`, `Annotation`, `FoodItem` schema).
2. **Inference Runner**: (Orchestrated by `EvaluationPipeline`) Iterates over the dataset and executes the AI logic.
3. **Comparison Engine & Metrics Calculator**: Computes accuracy, F1, MAE, MAPE, RMSE, and Expected Calibration Error (ECE) for confidence tracking.
4. **Report Generator**: Outputs aggregated metrics into Markdown and JSON reports for easy tracking.
5. **API Layer**: Exposes evaluation summaries via the main FastAPI backend for the Developer Dashboard (`GET /api/v1/evaluations`).

## Folder Structure

- `datasets/`: Dataset schema definitions and JSON loaders. Contains an `annotation_example.json` reference.
- `metrics/`: Core calculation logic for Recognition (Precision/Recall/F1), Nutrition (MAE/MAPE/RMSE), and Confidence Calibration (ECE).
- `reports/`: Generates `.md` and `.json` reports to summarize results.
- `pipeline.py`: Orchestrates the loading, inference, metrics calculation, and report generation.

## Dataset Schema

The Golden Dataset uses a standardized JSON schema. See `datasets/annotation_example.json` for a detailed look.

```json
{
  "name": "golden_benchmark_v1",
  "version": "1.0",
  "samples": [
    {
      "image_id": "food_001",
      "image_path": "images/food_001.jpg",
      "foods": [
        {
          "name": "Pho",
          "ingredients": ["Beef", "Rice noodle", "Green onion"],
          "nutrition": {
            "calories": 450,
            "protein": 32,
            "fat": 9,
            "carbohydrates": 54
          }
        }
      ]
    }
  ]
}
```

## Metrics

### Food & Ingredient Detection
- **Precision, Recall, F1**: Basic match measurements between predictions and ground truth.
- **Top-K Accuracy**: Is the actual food present in the top-K returned options?

### Nutrition
- **MAE (Mean Absolute Error)**: Average absolute deviation.
- **MAPE (Mean Absolute Percentage Error)**: Percentage deviation, providing context to the error scale.
- **RMSE (Root Mean Square Error)**: Penalizes large outliers.

### Confidence Calibration
- **Expected Calibration Error (ECE)**: Groups predictions by confidence bins and compares average accuracy vs average confidence per bin to detect if the model is systematically overconfident or underconfident.

## Usage

You can use the `EvaluationPipeline` to benchmark your models against the golden dataset and run `generate_report()` to persist the metrics.
