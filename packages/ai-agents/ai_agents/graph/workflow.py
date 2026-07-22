from langgraph.graph import StateGraph, END
from .state import GraphState
from ..models.llm_provider import BaseVisionModel
from ..agents.food_recognition import FoodRecognitionAgent
from ..agents.ingredient_analysis import IngredientAnalysisAgent
from ..agents.nutrition_estimation import NutritionEstimationAgent
from ..agents.quality_control import QualityControlAgent
from ..agents.response_formatter import ResponseFormattingAgent

class NutritionScannerWorkflow:
    def __init__(self, model: BaseVisionModel):
        self.model = model
        self.food_agent = FoodRecognitionAgent(model)
        self.ingredient_agent = IngredientAnalysisAgent(model)
        self.nutrition_agent = NutritionEstimationAgent(model)
        self.quality_agent = QualityControlAgent(model)
        self.formatter_agent = ResponseFormattingAgent()

        self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(GraphState)

        # Add nodes
        workflow.add_node("recognize_food", self.food_agent.run)
        workflow.add_node("analyze_ingredients", self.ingredient_agent.run)
        workflow.add_node("estimate_nutrition", self.nutrition_agent.run)
        workflow.add_node("check_quality", self.quality_agent.run)
        workflow.add_node("format_response", self.formatter_agent.run)

        # Edges
        workflow.set_entry_point("recognize_food")
        workflow.add_edge("recognize_food", "analyze_ingredients")
        workflow.add_edge("analyze_ingredients", "estimate_nutrition")
        workflow.add_edge("estimate_nutrition", "check_quality")
        workflow.add_edge("check_quality", "format_response")
        workflow.add_edge("format_response", END)

        self.app = workflow.compile()

    async def run(self, image_bytes: bytes) -> GraphState:
        initial_state = {
            "image_bytes": image_bytes,
            "foods": [],
            "ingredients": [],
            "nutrition": None,
            "quality": None,
            "metadata": {"model_name": getattr(self.model, "model_name", "unknown")}
        }
        
        # Stream or invoke
        result = await self.app.ainvoke(initial_state)
        return result
