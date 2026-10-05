// Browser requests use the Next.js rewrite by default. That keeps the browser
// same-origin and avoids coupling a deployed frontend to a localhost API URL.
const base = (process.env.NEXT_PUBLIC_API_URL || '/api/v1').replace(/\/$/, '');

// `any` is retained as the default during the gradual migration of existing
// pages; callers can opt into a response shape with api<MyResponse>(...).
export async function api<T = any>(path: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  const response = await fetch(`${base}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = typeof body?.detail === 'string' ? body.detail : `Request failed (${response.status})`;
    throw new Error(detail);
  }

  return (response.status === 204 ? null : response.json()) as Promise<T>;
}
