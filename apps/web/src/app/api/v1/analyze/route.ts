import { NextRequest, NextResponse } from "next/server";
import { createLocalJob } from "../jobsStore";
import { getFastApiUrl } from "../getFastApiUrl";

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

    const apiUrl = await getFastApiUrl();

    if (apiUrl) {
      try {
        // Forward request to FastAPI backend
        const proxyFormData = new FormData();
        proxyFormData.append("file", file);

        const backendRes = await fetch(`${apiUrl}/api/v1/analyze`, {
          method: "POST",
          body: proxyFormData,
        });

        if (backendRes.ok) {
          const data = await backendRes.json();
          return NextResponse.json(data, { status: backendRes.status });
        }
      } catch (err) {
        console.warn(`Backend proxy to ${apiUrl} failed, using local simulation:`, err);
      }
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
