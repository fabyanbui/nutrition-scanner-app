let cachedFastApiUrl: string | null = null;

export async function getFastApiUrl(): Promise<string | null> {
  // Check cached URL first with a fast timeout
  if (cachedFastApiUrl) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1000);
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

  const candidateUrls = [
    envApiUrl,
    envNextPublicApiUrl,
    "http://api:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
  ].filter(Boolean) as string[];

  const uniqueUrls = Array.from(new Set(candidateUrls));

  const checkUrl = async (url: string): Promise<string> => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 1200);
    try {
      const res = await fetch(`${url}/health`, { signal: controller.signal });
      clearTimeout(timeoutId);
      if (res.ok) return url;
      throw new Error("Not ok");
    } catch (e) {
      clearTimeout(timeoutId);
      throw e;
    }
  };

  try {
    const winner = await Promise.any(uniqueUrls.map((url) => checkUrl(url)));
    cachedFastApiUrl = winner;
    return winner;
  } catch {
    return null;
  }
}
