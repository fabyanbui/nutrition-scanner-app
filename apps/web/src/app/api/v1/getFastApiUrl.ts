export async function getFastApiUrl(): Promise<string | null> {
  const candidateUrls = [
    process.env.API_URL,
    "http://api:8000",
    process.env.NEXT_PUBLIC_API_URL,
    "http://127.0.0.1:8000",
    "http://localhost:8000",
  ].filter(Boolean) as string[];

  const uniqueUrls = Array.from(new Set(candidateUrls));

  for (const url of uniqueUrls) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 600);
      const res = await fetch(`${url}/health`, { signal: controller.signal });
      clearTimeout(timeoutId);
      if (res.ok) {
        return url;
      }
    } catch {
      // Continue searching
    }
  }

  return null;
}
