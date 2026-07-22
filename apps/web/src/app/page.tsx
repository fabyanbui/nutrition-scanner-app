"use client";

import { useState, useRef, useEffect } from "react";
import { Upload, ImageIcon, Loader2, CheckCircle2, Clock, AlertTriangle } from "lucide-react";

type AgentStatus = "pending" | "running" | "completed" | "error";

interface AgentStage {
  id: string;
  name: string;
  status: AgentStatus;
  latencyMs?: number;
}

export default function Home() {
  const [image, setImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  
  const [stages, setStages] = useState<AgentStage[]>([
    { id: "quality_heuristic", name: "Quality Check", status: "pending" },
    { id: "recognize_food", name: "Food Recognition", status: "pending" },
    { id: "analyze_ingredients", name: "Ingredient Analysis", status: "pending" },
    { id: "estimate_nutrition", name: "Nutrition Estimation", status: "pending" },
    { id: "check_quality", name: "Quality Control", status: "pending" },
  ]);
  
  const [pipelineFinished, setPipelineFinished] = useState(false);
  const [result, setResult] = useState<any | null>(null);
  const [partialData, setPartialData] = useState<any>({});
  const [error, setError] = useState<string | null>(null);
  const [qualityWarning, setQualityWarning] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImage(file);
      setPreview(URL.createObjectURL(file));
      resetState();
    }
  };

  const resetState = () => {
    setResult(null);
    setError(null);
    setQualityWarning(null);
    setJobId(null);
    setPipelineFinished(false);
    setPartialData({});
    setStages(prev => prev.map(s => ({ ...s, status: "pending", latencyMs: undefined })));
  };

  const analyzeImage = async () => {
    if (!image) return;
    resetState();
    try {
      const formData = new FormData();
      formData.append("file", image);

      // Create Job
      const res = await fetch("/api/v1/analyze", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error("Failed to create analysis job");
      }

      const data = await res.json();
      setJobId(data.job_id);
    } catch (err: any) {
      setError(err.message || "An error occurred");
    }
  };

  useEffect(() => {
    if (!jobId) return;

    const eventSource = new EventSource(`/api/v1/analyze/${jobId}/stream`);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.status === "finished") {
        setPipelineFinished(true);
        setResult(data.result);
        eventSource.close();
      } else if (data.status === "error") {
        setError(data.message);
        eventSource.close();
      } else if (data.agent) {
        setStages(prev => prev.map(stage => {
          if (stage.id === data.agent) {
            return {
              ...stage,
              status: data.status || stage.status,
              latencyMs: data.latency_ms ?? stage.latencyMs
            };
          }
          return stage;
        }));

        if (data.agent === "quality_heuristic" && data.warning) {
          setQualityWarning(data.warning);
        }

        if (data.data) {
          setPartialData((prev: any) => ({ ...prev, ...data.data }));
        }
      }
    };

    eventSource.onerror = (err) => {
      console.error("EventSource failed:", err);
      setError("Stream connection lost");
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [jobId]);

  const renderConfidenceBadge = (confidence: number) => {
    const pct = Math.round(confidence * 100);
    let colorClass = "bg-green-50 text-green-700 border-green-200";
    if (pct < 60) colorClass = "bg-red-50 text-red-700 border-red-200";
    else if (pct < 80) colorClass = "bg-yellow-50 text-yellow-700 border-yellow-200";
    
    return (
      <span className={`text-xs font-medium px-2 py-1 rounded-full border ${colorClass}`}>
        {pct}% Conf
      </span>
    );
  };

  return (
    <div className="max-w-5xl mx-auto p-6 py-12">
      <header className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Nutrition Scanner</h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Upload an image of your food to estimate nutrition and ingredients via an AI Agent Pipeline.
        </p>
      </header>

      <div className="grid md:grid-cols-[1fr_1.5fr] gap-8">
        <div className="space-y-6">
          <div
            className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:bg-gray-50 transition-colors"
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleImageChange}
              accept="image/*"
              className="hidden"
            />
            {preview ? (
              <img
                src={preview}
                alt="Preview"
                className="max-h-64 mx-auto rounded-lg object-contain shadow-sm"
              />
            ) : (
              <div className="flex flex-col items-center py-12 text-gray-500">
                <Upload className="w-12 h-12 mb-4 text-gray-400" />
                <p className="font-medium text-gray-700">Click to upload an image</p>
                <p className="text-sm mt-1">JPEG, PNG, WebP</p>
              </div>
            )}
          </div>

          <button
            onClick={analyzeImage}
            disabled={!image || (!!jobId && !pipelineFinished && !error)}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-colors shadow-sm"
          >
            {!!jobId && !pipelineFinished && !error ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Processing Pipeline...
              </>
            ) : (
              "Analyze Food"
            )}
          </button>

          {error && (
            <div className="p-4 bg-red-50 text-red-700 rounded-xl text-sm border border-red-200">
              {error}
            </div>
          )}

          {qualityWarning && (
            <div className="p-4 bg-yellow-50 text-yellow-800 rounded-xl text-sm border border-yellow-200 flex items-start">
              <AlertTriangle className="w-5 h-5 mr-2 flex-shrink-0" />
              <div>
                <p className="font-medium">Image Quality Notice</p>
                <p className="mt-1">{qualityWarning}</p>
                <p className="mt-2 text-xs text-yellow-700 opacity-80">Suggest: Use brighter lighting, move camera closer, or reduce number of food items.</p>
              </div>
            </div>
          )}
          
          {(jobId || pipelineFinished) && (
             <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 space-y-4">
               <h3 className="font-semibold text-gray-800">Agent Pipeline</h3>
               <div className="space-y-4">
                 {stages.map((stage, idx) => (
                   <div key={stage.id} className="flex items-center">
                     <div className="flex-shrink-0 mr-4">
                       {stage.status === "completed" ? (
                         <CheckCircle2 className="w-6 h-6 text-green-500" />
                       ) : stage.status === "running" ? (
                         <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />
                       ) : (
                         <div className="w-6 h-6 rounded-full border-2 border-gray-200" />
                       )}
                     </div>
                     <div className="flex-1">
                       <p className={`font-medium ${stage.status !== "pending" ? "text-gray-900" : "text-gray-400"}`}>
                         {stage.name}
                       </p>
                       {stage.latencyMs && (
                         <p className="text-xs text-gray-500 flex items-center mt-0.5">
                           <Clock className="w-3 h-3 mr-1" />
                           {(stage.latencyMs / 1000).toFixed(2)}s
                         </p>
                       )}
                     </div>
                   </div>
                 ))}
               </div>
               
               {result?.processing_time_ms && (
                  <div className="pt-4 mt-4 border-t border-gray-100 flex justify-between text-sm text-gray-500">
                     <span>Total Pipeline Time</span>
                     <span className="font-medium text-gray-700">{(result.processing_time_ms / 1000).toFixed(2)}s</span>
                  </div>
               )}
             </div>
          )}
        </div>

        <div>
          {Object.keys(partialData).length > 0 || result ? (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="p-6 border-b border-gray-100 bg-gray-50/50">
                <h2 className="text-2xl font-semibold text-gray-900">Analysis Results</h2>
              </div>
              
              <div className="p-6 space-y-8">
                {/* Detected Foods */}
                {(partialData.foods?.length > 0 || result?.foods?.length > 0) && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4 flex items-center">
                      <span className="bg-blue-100 text-blue-800 w-6 h-6 rounded-full inline-flex items-center justify-center mr-2 text-xs">1</span>
                      Detected Foods
                    </h3>
                    <div className="space-y-3">
                      {(result?.foods || partialData.foods).map((f: any, i: number) => (
                        <div key={i} className="flex justify-between items-center bg-gray-50 border border-gray-100 p-4 rounded-xl">
                          <span className="font-medium text-gray-900">{f.name}</span>
                          {renderConfidenceBadge(f.confidence)}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Ingredients */}
                {(partialData.ingredients?.length > 0 || result?.ingredients?.length > 0) && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4 flex items-center">
                      <span className="bg-indigo-100 text-indigo-800 w-6 h-6 rounded-full inline-flex items-center justify-center mr-2 text-xs">2</span>
                      Key Ingredients
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {(result?.ingredients || partialData.ingredients).map((ing: any, i: number) => (
                        <div key={i} className="inline-flex items-center bg-white border border-gray-200 px-3 py-1.5 rounded-lg shadow-sm">
                          <span className="text-sm font-medium text-gray-800 mr-2">{ing.name}</span>
                          <span className="text-xs text-gray-500 mr-2">{ing.estimated_amount}</span>
                          {renderConfidenceBadge(ing.confidence)}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Nutrition */}
                {(partialData.nutrition || result?.nutrition) && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4 flex items-center">
                       <span className="bg-orange-100 text-orange-800 w-6 h-6 rounded-full inline-flex items-center justify-center mr-2 text-xs">3</span>
                       Nutrition Estimates
                    </h3>
                    
                    {/* Quality Assurance note if applicable */}
                    {(partialData.quality?.warnings?.length > 0 || result?.quality?.warnings?.length > 0) && (
                        <div className="mb-4 p-3 bg-amber-50 text-amber-800 text-sm rounded-lg border border-amber-200 flex items-start">
                           <AlertTriangle className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                           <div>
                              <span className="font-medium">QC Adjustments: </span>
                              {(result?.quality?.warnings || partialData.quality.warnings).join(" | ")}
                           </div>
                        </div>
                    )}
                    
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                      {Object.entries(result?.nutrition || partialData.nutrition || {}).map(([key, data]: [string, any]) => {
                         if (!data || typeof data.value === 'undefined') return null;
                         const isCalories = key === 'calories';
                         return (
                          <div key={key} className={`p-4 rounded-xl border ${isCalories ? 'bg-orange-50 border-orange-100 col-span-2 sm:col-span-1' : 'bg-white border-gray-200'}`}>
                            <div className="text-sm text-gray-500 capitalize">{key}</div>
                            <div className={`font-bold mt-1 mb-2 ${isCalories ? 'text-3xl text-orange-700' : 'text-xl text-gray-900'}`}>
                              {data.value} {isCalories ? 'kcal' : 'g'}
                            </div>
                            {renderConfidenceBadge(data.confidence)}
                          </div>
                        )
                      })}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-gray-400 bg-gray-50/50 rounded-xl border-2 border-dashed border-gray-200 p-8 text-center min-h-[400px]">
              <ImageIcon className="w-16 h-16 mb-4 text-gray-300" />
              <p className="max-w-sm">Results will stream here as the pipeline processes your image.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
