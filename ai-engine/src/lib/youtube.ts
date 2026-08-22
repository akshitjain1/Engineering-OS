export function youtubeId(url: string): string | null {
  try {
    const parsed = new URL(url);
    if (parsed.hostname === "youtu.be") {
      return parsed.pathname.replace("/", "") || null;
    }
    if (parsed.hostname.includes("youtube.com")) {
      if (parsed.searchParams.get("v")) return parsed.searchParams.get("v");
      const embed = parsed.pathname.match(/\/embed\/([^/]+)/);
      if (embed) return embed[1];
    }
  } catch {
    return null;
  }
  return null;
}

export function resourceProvider(url: string, resourceType: string): string {
  try {
    const host = new URL(url).hostname.replace(/^www\./, "");
    if (host) return host;
  } catch {
    /* ignore */
  }
  return resourceType.replace(/_/g, " ");
}
