# Domain Requirements & AI Safety Guidelines

## Core Product Vision

The **Nutrition Scanner** is an AI-powered web application that analyzes user-submitted food photos and estimates nutritional composition using specialized agent workflows.

---

## 1. Multi-Item Food Recognition & User Guidance

### Guidelines & Scope Constraints
1. **Multi-Item Support**: The system recognizes multi-dish plates (e.g., chicken breast, quinoa, avocado, salad in one bowl).
2. **Item Count Limit Recommendation**: The user interface recommends limiting images to **1 to 3 distinct food items per photo** for optimal recognition precision.
3. **Quality & Complexity Warnings**:
   - If an image is overly complex, cluttered, blurry, or low-resolution, the system emits user-visible warnings.
   - Low resolution or poor lighting triggers lower confidence scores.

---

## 2. Confidence Score Propagation Rules

Confidence scores (`0.0` to `1.0`) must propagate logically through every agent stage in the LangGraph workflow:

```
[Upstream Food Recognition Confidence: 0.85]
                    |
                    v
[Ingredient Analysis Confidence capped at max 0.85]
                    |
                    v
[Nutrition Estimation Confidence capped at max 0.85]
```

### Key Principles
- **No Upstream Violation**: A downstream agent (e.g., Nutrition Estimation Agent) **MUST NEVER** produce a confidence score higher than the upstream evidence (Food Recognition / Ingredient Analysis) supports.
- **Confidence Reduction**: If portion estimation is ambiguous, the Ingredient and Nutrition agents adjust confidence downwards accordingly.
- **Quality Control Adjustment**: The Quality Control agent checks for macro consistency and dampens total confidence if discrepancies arise.

---

## 3. Anti-Hallucination & Uncertainty Standards

To maintain user trust and avoid medical/dietary misinformation:

1. **Explicit Uncertainty Communication**:
   - High Confidence (`>= 0.80`): Displayed as green badge (**High**).
   - Medium Confidence (`0.60 - 0.79`): Displayed as yellow/amber badge (**Medium**).
   - Low Confidence (`< 0.60`): Displayed as red badge (**Low**) accompanied by an explicit uncertainty disclaimer.

2. **No Hallucinated Precision**:
   - When ingredients cannot be clearly visually identified (e.g. hidden sauces, deep fried fillings), the system defaults to lower confidence scores and adds clear warning notes in the Quality Control report.

---

## 4. Macronutrient Consistency Rules

The Quality Control agent enforces physical laws of macronutrient energy content:

$$\text{Calculated Energy (kcal)} = (\text{Protein (g)} \times 4) + (\text{Carbohydrates (g)} \times 4) + (\text{Fat (g)} \times 9)$$

- **Tolerance Threshold**: If the model's reported total calories deviate by more than **30%** from the calculated macro sum, Quality Control marks `valid = false`, flags a warning, and scales down confidence.
- **Standard Units**:
  - Calories: `kcal`
  - Protein, Carbohydrates, Fat, Fiber, Sugar: `grams (g)`
  - Sodium: `milligrams (mg)`
