export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "";

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(path: string, status: number, detail: unknown) {
    super(`${path} -> ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

export async function api<T = unknown>(path: string, options?: RequestInit): Promise<T> {
  const { headers, ...rest } = options ?? {};
  const method = String(rest.method || "GET").toUpperCase();
  const headerBag = new Headers(headers);
  if (rest.body != null && !headerBag.has("Content-Type")) {
    headerBag.set("Content-Type", "application/json");
  }
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      ...rest,
      method,
      headers: headerBag,
    });
  } catch {
    throw new ApiError(path, 0, "Backend is not reachable. Start FastAPI on port 8000.");
  }
  if (!res.ok) {
    let detail: unknown = res.statusText;
    try {
      detail = await res.json();
    } catch {
      /* ignore */
    }
    throw new ApiError(path, res.status, detail);
  }
  return res.json() as Promise<T>;
}

export function errorMessage(err: unknown): string {
  if (err instanceof ApiError) {
    if (typeof err.detail === "string") return err.detail;
    if (err.detail && typeof err.detail === "object") {
      const detail = err.detail as { detail?: unknown; error?: string; message?: string };
      if (typeof detail.detail === "string") return detail.detail;
      if (detail.detail && typeof detail.detail === "object") {
        const nested = detail.detail as { message?: string; error?: string };
        return nested.message || nested.error || err.message;
      }
      return detail.message || detail.error || err.message;
    }
    if (err.status === 0) return "Backend is not reachable. Start FastAPI on port 8000.";
    return err.message;
  }
  if (err instanceof Error) return err.message;
  return "Something went wrong.";
}
