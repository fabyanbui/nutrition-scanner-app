let cachedFastApiUrl: string | null = null;

export async function getFastApiUrl(): Promise<string | null> {
  // Check cached URL first with a generous timeout
  if (cachedFastApiUrl) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);
      const res = await fetch(`${cachedFastApiUrl}/health`, { signal: controller.signal });
      clearTimeout(timeoutId);
      if (res.ok) {
        return cachedFastApiUrl;
      }
    } catch {
      cachedFastApiUrl = null;
    }
  }

  const envApiUrl = process.env.API_URL;
  const envNextPublicApiUrl = process.env.NEXT_PUBLIC_API_URL;

  // Prioritize remote/docker URLs before 127.0.0.1 or localhost fallbacks
  const candidateUrls = [
    envApiUrl && !envApiUrl.includes("127.0.0.1") && !envApiUrl.includes("localhost") ? envApiUrl : null,
    "http://api:8000",
    envApiUrl,
    envNextPublicApiUrl && !envNextPublicApiUrl.includes("127.0.0.1") && !envNextPublicApiUrl.includes("localhost") ? envNextPublicApiUrl : null,
    envNextPublicApiUrl,
    "http://127.0.0.1:8000",
    "http://localhost:8000",
  ].filter(Boolean) as string[];

  const uniqueUrls = Array.from(new Set(candidateUrls));

  for (const url of uniqueUrls) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2500);
      const res = await fetch(`${url}/health`, { signal: controller.signal });
      clearTimeout(timeoutId);
      if (res.ok) {
        cachedFastApiUrl = url;
        return url;
      }
    } catch {
      // Continue searching
    }
  }

  return null;
}
