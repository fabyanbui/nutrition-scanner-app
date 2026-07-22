import { NextRequest, NextResponse } from "next/server";
import { createLocalJob } from "../jobsStore";

const FASTAPI_URL = process.env.API_URL || "http://127.0.0.1:8000";

async function isBackendAvailable(): Promise<boolean> {
  try {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), 800);
    const res = await fetch(`${FASTAPI_URL}/health`, { signal: controller.signal });
    clearTimeout(id);
    return res.ok;
  } catch {
    return false;
  }
}

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const file = formData.get("file") as File | null;

    if (!file) {
      return NextResponse.json({ detail: "No file provided" }, { status: 400 });
    }

    if (!file.type.startsWith("image/")) {
      return NextResponse.json({ detail: "File must be an image" }, { status: 400 });
    }

    const backendUp = await isBackendAvailable();

    if (backendUp) {
      // Forward request to FastAPI backend
      const proxyFormData = new FormData();
      proxyFormData.append("file", file);

      const backendRes = await fetch(`${FASTAPI_URL}/api/v1/analyze`, {
        method: "POST",
        body: proxyFormData,
      });

      const data = await backendRes.json();
      return NextResponse.json(data, { status: backendRes.status });
    }

    // Local fallback when FastAPI backend is not running
    const jobId = typeof crypto !== "undefined" && crypto.randomUUID 
      ? crypto.randomUUID() 
      : `job-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;

    createLocalJob({
      jobId,
      filename: file.name,
      sizeBytes: file.size,
      contentType: file.type,
    });

    return NextResponse.json({ job_id: jobId });
  } catch (err: any) {
    return NextResponse.json(
      { detail: err.message || "Failed to analyze image" },
      { status: 500 }
    );
  }
}
