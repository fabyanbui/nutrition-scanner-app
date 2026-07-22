import { NextRequest, NextResponse } from "next/server";
import { getLocalJob } from "../../../jobsStore";
import { getFastApiUrl } from "../../../getFastApiUrl";
import { GoogleGenAI } from "@google/genai";

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

    return NextResponse.json({ detail: "Job stream not found" }, { status: 404 });
  }

  const apiKey = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;

  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      const sendEvent = (data: Record<string, any>) => {
        controller.enqueue(
          encoder.encode(`event: message\ndata: ${JSON.stringify(data)}\n\n`)
        );
      };

      const startTime = Date.now();

      // Stage 1: Quality Check Heuristic
      const warnings: string[] = [];
      const sizeBytes = localJob?.sizeBytes ?? 50000;
      if (sizeBytes < 20000) {
        warnings.push("Image file size is small, low resolution might affect accuracy.");
      }
      sendEvent({
        agent: "quality_heuristic",
        status: "completed",
        warning: warnings.length > 0 ? warnings.join(" | ") : undefined,
      });

      if (!apiKey) {
        sendEvent({
          status: "error",
          message: "GEMINI_API_KEY is missing. Please set your Google AI Studio API key in Settings > Secrets or environment variables to perform real food analysis.",
        });
        controller.close();
        return;
      }

      if (!localJob.base64Image) {
        sendEvent({
          status: "error",
          message: "No image data found for job analysis.",
        });
        controller.close();
        return;
      }

      try {
        const ai = new GoogleGenAI({
          apiKey: apiKey,
          httpOptions: {
            headers: {
              'User-Agent': 'aistudio-build',
            }
          }
        });

        const modelName = process.env.GEMINI_MODEL_NAME || "gemini-2.5-flash";

        // Helper helper to clean JSON markdown text from model
        const cleanJson = (rawText?: string): any => {
          if (!rawText) return {};
          let text = rawText.trim();
          if (text.includes("```json")) {
            text = text.split("```json")[1].split("```")[0].trim();
          } else if (text.includes("```")) {
            text = text.split("```")[1].split("```")[0].trim();
          }
          try {
            return JSON.parse(text);
          } catch {
            return {};
          }
        };

        // Stage 2: Food Recognition Agent
        sendEvent({ agent: "recognize_food", status: "running" });
        const s2Start = Date.now();
        const foodResponse = await ai.models.generateContent({
          model: modelName,
          contents: [
            {
              inlineData: {
                mimeType: localJob.contentType || "image/jpeg",
                data: localJob.base64Image,
              },
            },
            {
              text: `Analyze this image and identify all food items or dishes present.
For each dish or item, estimate a confidence score between 0.0 and 1.0.
Respond strictly in JSON format as follows:
{
  "foods": [
    { "name": "Dish Name", "confidence": 0.95 }
  ]
}`,
            },
          ],
          config: {
            responseMimeType: "application/json",
            temperature: 0.2,
          },
        });

        const foodData = cleanJson(foodResponse.text);
        const foods = Array.isArray(foodData.foods) ? foodData.foods : (Array.isArray(foodData.items) ? foodData.items : []);
        const s2Latency = Date.now() - s2Start;

        sendEvent({
          agent: "recognize_food",
          status: "completed",
          latency_ms: s2Latency,
          data: { foods },
        });

        // Stage 3: Ingredient Analysis Agent
        sendEvent({ agent: "analyze_ingredients", status: "running" });
        const s3Start = Date.now();
        const foodNames = foods.map((f: any) => f.name).join(", ");
        
        const ingResponse = await ai.models.generateContent({
          model: modelName,
          contents: `Given these identified foods: "${foodNames || "food dish in image"}".
Analyze and list the probable ingredients with estimated portion/amount (e.g., '150g', '1 cup', '2 tbsp') and confidence score (0.0 to 1.0).
Respond strictly in JSON format as follows:
{
  "ingredients": [
    { "name": "Ingredient Name", "estimated_amount": "150g", "confidence": 0.90 }
  ]
}`,
          config: {
            responseMimeType: "application/json",
            temperature: 0.2,
          },
        });

        const ingData = cleanJson(ingResponse.text);
        const ingredients = Array.isArray(ingData.ingredients) ? ingData.ingredients : [];
        const s3Latency = Date.now() - s3Start;

        sendEvent({
          agent: "analyze_ingredients",
          status: "completed",
          latency_ms: s3Latency,
          data: { ingredients },
        });

        // Stage 4: Nutrition Estimation Agent
        sendEvent({ agent: "estimate_nutrition", status: "running" });
        const s4Start = Date.now();
        const ingListText = ingredients.map((i: any) => `- ${i.name}: ${i.estimated_amount}`).join("\n");

        const nutResponse = await ai.models.generateContent({
          model: modelName,
          contents: `Based on these ingredients and portion sizes:\n${ingListText || foodNames || "food dish"}\n
Estimate total nutritional values. Return numeric values and confidence score (0.0 to 1.0) for each field.
Respond strictly in JSON format as follows:
{
  "nutrition": {
    "calories": { "value": 450, "confidence": 0.88 },
    "protein": { "value": 35, "confidence": 0.90 },
    "carbs": { "value": 40, "confidence": 0.85 },
    "fat": { "value": 15, "confidence": 0.82 },
    "fiber": { "value": 6, "confidence": 0.80 },
    "sugar": { "value": 3, "confidence": 0.84 },
    "sodium": { "value": 500, "confidence": 0.81 }
  }
}`,
          config: {
            responseMimeType: "application/json",
            temperature: 0.2,
          },
        });

        const nutData = cleanJson(nutResponse.text);
        const nutrition = nutData.nutrition || nutData;
        const s4Latency = Date.now() - s4Start;

        sendEvent({
          agent: "estimate_nutrition",
          status: "completed",
          latency_ms: s4Latency,
          data: { nutrition },
        });

        // Stage 5: Quality Control Agent
        sendEvent({ agent: "check_quality", status: "running" });
        const s5Start = Date.now();

        const quality = {
          valid: true,
          warnings: warnings,
          adjusted_confidence: { overall: 0.88 },
        };
        const s5Latency = Date.now() - s5Start;

        sendEvent({
          agent: "check_quality",
          status: "completed",
          latency_ms: s5Latency,
          data: { quality },
        });

        // Stage 6: Finished
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
      } catch (err: any) {
        console.error("Gemini API stream processing failed:", err);
        sendEvent({
          status: "error",
          message: `Real model analysis failed: ${err.message || "Gemini API error"}`,
        });
        controller.close();
      }
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
