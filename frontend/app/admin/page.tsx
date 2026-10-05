'use client';

import { useEffect, useState } from 'react';
import { api } from '../../lib/api';

type Feedback = { id: string; name: string; email: string; category: string; rating: number; message: string; suggestions: string; created_at: string };

export default function Admin() {
  const [data, setData] = useState<any>();
  const [error, setError] = useState('');
  const [feedback, setFeedback] = useState<Feedback[]>([]);
  useEffect(() => {
    api('/admin/reports/summary').then(setData).catch((reason) => setError(reason.message));
    api<{ items: Feedback[] }>('/admin/feedback').then((result) => setFeedback(result.items)).catch(() => undefined);
  }, []);
  return <main className="wrap"><h1>Admin dashboard</h1>{error ? <p>{error} Sign in with admin@hotel.test to access reports.</p> : !data ? <p>Loading dashboard…</p> : <><div className="card"><p>Hotels: {data.hotels}</p><p>Bookings: {data.bookings}</p><p>Paid revenue: ₹{data.revenue}</p><small>Inventory, rates, users, payment and audit management APIs are available under the secured API.</small></div><section className="card"><h2 className="text-xl font-bold">Submitted feedback</h2>{feedback.length === 0 ? <p className="mt-3 text-slate-600">No feedback submissions yet.</p> : <div className="mt-4 grid gap-4">{feedback.map((item) => <article key={item.id} className="rounded-xl border border-slate-200 p-4"><div className="flex flex-wrap justify-between gap-2"><div><h3 className="font-bold">{item.category.replaceAll('_', ' ')}</h3><p className="text-sm text-slate-600">{item.name} · {item.email}</p></div><span className="text-sm font-semibold text-amber-600">{'★'.repeat(item.rating)}{'☆'.repeat(5 - item.rating)} · {new Date(item.created_at).toLocaleDateString()}</span></div><p className="mt-3 whitespace-pre-wrap">{item.message}</p>{item.suggestions && <p className="mt-2 text-sm text-slate-600">Suggestions: {item.suggestions}</p>}</article>)}</div>}</section></>}</main>;
}
