/**
 * Only http(s) links may render as clickable anchors or open windows. URLs
 * coming from MCP tool results or search provider responses are remote
 * content, so a javascript: (or data:/file:) URL must never become a link
 * target inside the dashboard origin (LD fork R2-24, R2-33).
 */
export function isHttpUrl(url: string | undefined | null): url is string {
  if (!url) return false;
  try {
    const parsed = new URL(url, "https://dashboard.invalid");
    return parsed.protocol === "https:" || parsed.protocol === "http:";
  } catch {
    return false;
  }
}
