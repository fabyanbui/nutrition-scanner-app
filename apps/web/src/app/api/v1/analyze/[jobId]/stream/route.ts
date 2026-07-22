import { NextRequest, NextResponse } from "next/server";
import { getLocalJob } from "../../../jobsStore";
import { getFastApiUrl } from "../../../getFastApiUrl";

export async function GET(
  req: NextRequest,
  { params }: { params: { jobId: string } }
) {
  const jobId = params.jobId;
  const localJob = getLocalJob(jobId);

  if (!localJob) {
    // Attempt proxying to FastAPI if job wasn't local
    try {
      const apiUrl = await getFastApiUrl();
      if (apiUrl) {
        const proxyRes = await fetch(`${apiUrl}/api/v1/analyze/${jobId}/stream`);
        if (proxyRes.ok && proxyRes.body) {
          return new Response(proxyRes.body, {
            headers: {
              "Content-Type": "text/event-stream",
              "Cache-Control": "no-cache, no-transform",
              Connection: "keep-alive",
            },
          });
        }
      }
    } catch (err) {
      console.warn("Stream proxy to FastAPI failed:", err);
    }
  }

  // Handle local simulated agent pipeline stream
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      const sendEvent = (data: Record<string, any>) => {
        controller.enqueue(
          encoder.encode(`event: message\ndata: ${JSON.stringify(data)}\n\n`)
        );
      };

      const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

      const startTime = Date.now();

      // Stage 1: Quality Check Heuristic
      await sleep(300);
      const warnings: string[] = [];
      const sizeBytes = localJob?.sizeBytes ?? 50000;
      if (sizeBytes < 20000) {
        warnings.push("Image file size is small, resolution might affect accuracy.");
      }
      sendEvent({
        agent: "quality_heuristic",
        status: "completed",
        warning: warnings.length > 0 ? warnings.join(" | ") : undefined,
      });

      // Stage 2: Food Recognition Agent
      await sleep(600);
      sendEvent({ agent: "recognize_food", status: "running" });
      await sleep(700);
      const foods = [
        { name: "Grilled Chicken Bowl & Quinoa", confidence: 0.92 },
        { name: "Avocado Salad", confidence: 0.86 },
      ];
      sendEvent({
        agent: "recognize_food",
        status: "completed",
        latency_ms: 700,
        data: { foods },
      });

      // Stage 3: Ingredient Analysis Agent
      await sleep(400);
      sendEvent({ agent: "analyze_ingredients", status: "running" });
      await sleep(800);
      const ingredients = [
        { name: "Chicken Breast", estimated_amount: "150g", confidence: 0.91 },
        { name: "Cooked Quinoa", estimated_amount: "1 cup (185g)", confidence: 0.88 },
        { name: "Sliced Avocado", estimated_amount: "1/2 medium", confidence: 0.85 },
        { name: "Cherry Tomatoes", estimated_amount: "50g", confidence: 0.82 },
        { name: "Olive Oil Dressing", estimated_amount: "1 tbsp", confidence: 0.76 },
      ];
      sendEvent({
        agent: "analyze_ingredients",
        status: "completed",
        latency_ms: 800,
        data: { ingredients },
      });

      // Stage 4: Nutrition Estimation Agent
      await sleep(400);
      sendEvent({ agent: "estimate_nutrition", status: "running" });
      await sleep(750);
      const nutrition = {
        calories: { value: 540, confidence: 0.88 },
        protein: { value: 42, confidence: 0.90 },
        carbs: { value: 45, confidence: 0.85 },
        fat: { value: 18, confidence: 0.82 },
        fiber: { value: 8, confidence: 0.80 },
        sugar: { value: 4, confidence: 0.84 },
        sodium: { value: 620, confidence: 0.81 },
      };
      sendEvent({
        agent: "estimate_nutrition",
        status: "completed",
        latency_ms: 750,
        data: { nutrition },
      });

      // Stage 5: Quality Control Agent
      await sleep(300);
      sendEvent({ agent: "check_quality", status: "running" });
      await sleep(500);
      const quality = {
        valid: true,
        warnings: [],
        adjusted_confidence: { overall: 0.86 },
      };
      sendEvent({
        agent: "check_quality",
        status: "completed",
        latency_ms: 500,
        data: { quality },
      });

      // Stage 6: Finished
      await sleep(200);
      const totalLatency = Date.now() - startTime;
      const result = {
        foods,
        ingredients,
        nutrition,
        quality,
        processing_time_ms: totalLatency,
      };

      sendEvent({ status: "finished", result });
      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  });
}
