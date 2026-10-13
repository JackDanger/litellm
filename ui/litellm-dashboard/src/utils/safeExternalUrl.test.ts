import { isHttpUrl } from "./safeExternalUrl";

describe("isHttpUrl", () => {
  it("allows http and https URLs", () => {
    expect(isHttpUrl("https://example.com/page")).toBe(true);
    expect(isHttpUrl("http://example.com/file")).toBe(true);
  });

  it("rejects javascript, data and file URLs", () => {
    expect(isHttpUrl("javascript:fetch('/key/generate')")).toBe(false);
    expect(isHttpUrl("data:text/html,<script>alert(1)</script>")).toBe(false);
    expect(isHttpUrl("file:///etc/passwd")).toBe(false);
  });

  it("rejects empty and malformed values", () => {
    expect(isHttpUrl(undefined)).toBe(false);
    expect(isHttpUrl(null)).toBe(false);
    expect(isHttpUrl("")).toBe(false);
    expect(isHttpUrl("not a url")).toBe(false);
  });

  it("accepts scheme-relative URLs resolved as http(s)", () => {
    expect(isHttpUrl("//example.com/page")).toBe(true);
  });
});
