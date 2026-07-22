"use client";

import { useState, useRef } from "react";
import { Upload, ImageIcon, Loader2 } from "lucide-react";

export default function Home() {
  const [image, setImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImage(file);
      setPreview(URL.createObjectURL(file));
      setResult(null);
      setError(null);
    }
  };

  const analyzeImage = async () => {
    if (!image) return;
    setAnalyzing(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", image);

      const res = await fetch("/api/v1/analyze", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error("Failed to analyze image");
      }

      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 py-12">
      <header className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Nutrition Scanner</h1>
        <p className="text-lg text-gray-600">
          Upload an image of your food to estimate nutrition and ingredients.
        </p>
      </header>

      <div className="grid md:grid-cols-2 gap-8">
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
                className="max-h-64 mx-auto rounded-lg object-contain"
              />
            ) : (
              <div className="flex flex-col items-center py-12 text-gray-500">
                <Upload className="w-12 h-12 mb-4 text-gray-400" />
                <p className="font-medium">Click to upload an image</p>
                <p className="text-sm mt-1">JPEG, PNG, WebP</p>
              </div>
            )}
          </div>

          <button
            onClick={analyzeImage}
            disabled={!image || analyzing}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-colors"
          >
            {analyzing ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Analyzing...
              </>
            ) : (
              "Analyze Food"
            )}
          </button>

          {error && (
            <div className="p-4 bg-red-50 text-red-700 rounded-xl text-sm">
              {error}
            </div>
          )}
        </div>

        <div>
          {result ? (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-6">
              <h2 className="text-2xl font-semibold border-b pb-4">Analysis Result</h2>
              
              <div>
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">Detected Food</h3>
                <div className="space-y-2">
                  {result.foods?.map((f: any, i: number) => (
                    <div key={i} className="flex justify-between items-center bg-gray-50 p-3 rounded-lg">
                      <span className="font-medium">{f.name}</span>
                      <span className="text-sm text-green-600 font-medium bg-green-50 px-2 py-1 rounded-full">
                        {Math.round(f.confidence * 100)}% Match
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">Estimated Nutrition</h3>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(result.nutrition || {}).map(([key, data]: [string, any]) => (
                    <div key={key} className="bg-gray-50 p-4 rounded-lg">
                      <div className="text-sm text-gray-500 capitalize">{key}</div>
                      <div className="text-xl font-bold mt-1">
                        {data.value} {key === 'calories' ? 'kcal' : 'g'}
                      </div>
                      <div className="text-xs text-gray-400 mt-1">
                        Confidence: {Math.round(data.confidence * 100)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {result.quality_warning && (
                <div className="p-4 bg-yellow-50 text-yellow-800 rounded-xl text-sm border border-yellow-200">
                  <p className="font-medium">Quality Notice</p>
                  <p className="mt-1">{result.quality_warning}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-gray-400 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200 p-8 text-center min-h-[400px]">
              <ImageIcon className="w-16 h-16 mb-4 text-gray-300" />
              <p>Upload an image and analyze it to see the results here.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
