/**
 * Only http(s) links may render as clickable anchors or open windows. URLs
 * coming from MCP tool results or search provider responses are remote
 * content, so a javascript: (or data:/file:) URL must never become a link
 * target of the dashboard origin. A scheme-less string and a scheme-relative
 * //host/path are resolved against the dashboard origin, so only the
 * http(s) protocols among them can pass.
 */
export function isHttpUrl(url: string | undefined | null): url is string {
  if (!url) return false;
  if (!url.startsWith("//") && !/^[a-z][a-z0-9+.-]*:/i.test(url)) return false;
  try {
    const parsed = new URL(url, "https://dashboard.invalid");
    return parsed.protocol === "https:" || parsed.protocol === "http:";
  } catch {
    return false;
  }
}
