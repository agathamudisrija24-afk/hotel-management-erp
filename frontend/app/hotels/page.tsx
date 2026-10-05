'use client';

import { FormEvent, Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import HotelCard, { Hotel } from '../../components/HotelCard';
import { api } from '../../lib/api';

function HotelsPageContent() {
  const searchParams = useSearchParams();
  const [hotels, setHotels] = useState<Hotel[]>([]); const [error, setError] = useState(''); const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState(searchParams.get('q') ?? ''); const [sort, setSort] = useState('rating_desc'); const [rating, setRating] = useState(''); const [service, setService] = useState('');
  function load() { const params = new URLSearchParams({ sort }); if (query) params.set('q', query); if (rating) params.set('min_rating', rating); if (service) params.set('service', service); setLoading(true); api<{ items: Hotel[] }>(`/hotels?${params}`).then((data) => { setHotels(data.items); setError(''); }).catch((reason: Error) => setError(reason.message)).finally(() => setLoading(false)); }
  useEffect(load, []); // Initial catalogue request.
  function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); load(); }
  return <main className="wrap py-10"><div className="mb-7"><p className="text-sm font-semibold uppercase tracking-widest text-teal-700">Stay finder</p><h1 className="text-4xl font-bold text-slate-900">Explore our hotels</h1><p className="mt-2 text-slate-600">Search five distinctive stays across India.</p></div>
    <form onSubmit={submit} className="mb-8 grid gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm md:grid-cols-4"><input className="input w-full" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Hotel name or location" /><select className="input w-full" value={rating} onChange={(event) => setRating(event.target.value)}><option value="">Any rating</option><option value="4.7">4.7+ rating</option><option value="4.8">4.8+ rating</option></select><select className="input w-full" value={service} onChange={(event) => setService(event.target.value)}><option value="">Any service</option><option>Spa</option><option>Swimming pool</option><option>Restaurant</option><option>Airport transfers</option></select><div className="flex gap-2"><select className="input min-w-0 flex-1" value={sort} onChange={(event) => setSort(event.target.value)}><option value="rating_desc">Top rated</option><option value="price_asc">Price: low to high</option><option value="price_desc">Price: high to low</option></select><button className="btn">Apply</button></div></form>
    {error ? <p className="rounded-lg bg-rose-50 p-4 text-rose-700">{error}</p> : loading ? <p className="text-slate-600">Loading hotels…</p> : hotels.length === 0 ? <p className="text-slate-600">No hotels match these filters.</p> : <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">{hotels.map((hotel) => <HotelCard key={hotel.id} hotel={hotel} />)}</div>}
  </main>;
}

export default function HotelsPage() {
  return <Suspense fallback={<main className="wrap py-10 text-slate-600">Loading hotels…</main>}><HotelsPageContent /></Suspense>;
}
