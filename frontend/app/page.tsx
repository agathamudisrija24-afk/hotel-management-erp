'use client';

import Image from 'next/image';
import Link from 'next/link';
import { FormEvent, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import HotelCard, { Hotel } from '../components/HotelCard';
import ServiceGrid, { Service } from '../components/ServiceGrid';
import { api } from '../lib/api';

export default function Home() {
  const [hotels, setHotels] = useState<Hotel[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [destination, setDestination] = useState('');
  const router = useRouter();

  useEffect(() => {
    api<{ items: Hotel[] }>('/hotels?sort=rating_desc')
      .then((data) => setHotels(data.items))
      .catch((reason: Error) => setError(reason.message))
      .finally(() => setLoading(false));
  }, []);
  function search(event: FormEvent<HTMLFormElement>) { event.preventDefault(); router.push(`/hotels?q=${encodeURIComponent(destination)}`); }
  const services = Array.from(new Map(hotels.flatMap((hotel) => hotel.services).map((service) => [service.name, service])).values()) as Service[];

  return <main>
    <section className="relative isolate min-h-[520px] overflow-hidden bg-slate-900 text-white">
      <Image src="https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1800&q=90" alt="Elegant resort overlooking a pool" fill priority className="-z-20 object-cover" sizes="100vw" />
      <div className="absolute inset-0 -z-10 bg-slate-950/60" />
      <div className="wrap flex min-h-[520px] flex-col justify-center py-16">
        <p className="mb-3 text-sm font-semibold uppercase tracking-[0.2em] text-teal-200">Curated stays across India</p>
        <h1 className="max-w-3xl text-4xl font-bold tracking-tight sm:text-6xl">Find a stay that feels like a getaway.</h1>
        <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-100">Book distinctive beach, heritage, mountain, city and nature escapes with secure online booking.</p>
        <form onSubmit={search} className="mt-8 grid max-w-4xl gap-3 rounded-2xl bg-white p-4 text-slate-900 shadow-2xl md:grid-cols-[1fr_0.8fr_0.8fr_auto]">
          <label className="text-sm font-medium">Destination<input value={destination} onChange={(event) => setDestination(event.target.value)} className="input mt-1 w-full" placeholder="Goa, Jaipur, Munnar..." /></label>
          <label className="text-sm font-medium">Check-in<input className="input mt-1 w-full" type="date" /></label>
          <label className="text-sm font-medium">Guests<select className="input mt-1 w-full" defaultValue="2"><option>1</option><option>2</option><option>3</option><option>4</option></select></label>
          <button className="btn mt-auto h-11">Search stays</button>
        </form>
      </div>
    </section>
    <section className="wrap py-14">
      <div className="mb-7 flex flex-wrap items-end justify-between gap-3"><div><p className="text-sm font-semibold uppercase tracking-widest text-teal-700">Five unique destinations</p><h2 className="text-3xl font-bold text-slate-900">Featured hotels</h2></div><Link className="font-semibold text-teal-700 hover:underline" href="/hotels">Explore all hotels →</Link></div>
      {error && <p className="rounded-lg bg-rose-50 p-4 text-rose-700">{error}</p>}
      {!error && loading && <p className="text-slate-600">Loading featured hotels…</p>}
      {!error && !loading && hotels.length === 0 && <p className="rounded-xl bg-slate-50 p-5 text-slate-600">No featured hotels are available right now.</p>}
      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">{hotels.map((hotel) => <HotelCard key={hotel.id} hotel={hotel} />)}</div>
    </section>
    <section id="services" className="bg-[#F2F3F5] py-14"><div className="wrap"><div className="mb-8 max-w-2xl"><p className="text-sm font-semibold uppercase tracking-widest text-[#C8A45D]">Thoughtfully included</p><h2 className="mt-2 text-3xl font-bold text-[#202833]">Exceptional services</h2><p className="mt-3 text-slate-600">Real services from our hotel catalogue, tailored to each destination.</p></div>{loading ? <p className="rounded-xl bg-white p-5 text-slate-600">Loading hotel services…</p> : error ? <p className="rounded-xl bg-rose-50 p-5 text-rose-700">We could not load hotel services: {error}</p> : services.length ? <ServiceGrid services={services} limit={9} /> : <p className="rounded-xl bg-white p-5 text-slate-600">No hotel services are currently available.</p>}</div></section>
    <section className="wrap grid gap-6 py-14 lg:grid-cols-2"><div className="overflow-hidden rounded-3xl"><Image src="https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=1200&q=85" alt="Fine dining table setting" width={1200} height={800} className="h-full min-h-72 w-full object-cover" /></div><div className="flex flex-col justify-center rounded-3xl bg-[#142B3B] p-8 text-white"><p className="text-sm font-semibold uppercase tracking-widest text-[#ead6a5]">Local flavours</p><h2 className="mt-3 text-3xl font-bold">Dining that belongs to the destination.</h2><p className="mt-4 leading-7 text-slate-200">From Goan seafood to Kerala feasts, every hotel has a distinct menu with regional specialties and all-day favourites.</p><Link href="/restaurant" className="mt-6 inline-block w-fit rounded-lg bg-[#C8A45D] px-5 py-3 font-semibold text-[#142B3B] transition hover:bg-[#ead6a5]">Explore restaurants</Link></div></section>
    <section id="about" className="bg-[#F2F3F5] py-14"><div className="wrap"><h2 className="text-3xl font-bold text-[#202833]">Why choose Harbor Hotels?</h2><div className="mt-7 grid gap-5 sm:grid-cols-2 lg:grid-cols-5">{[['▣', 'Comfortable rooms', 'Thoughtful rooms for every kind of stay.'], ['⌁', 'Easy booking', 'A simple, secure online booking journey.'], ['✦', 'Quality hospitality', 'Warm local service at every hotel.'], ['✧', 'Regional dining', 'Menus rooted in each destination.'], ['◷', 'Guest support', 'Help when you need it, around the clock.']].map(([icon, title, text]) => <article key={title} className="rounded-2xl bg-white p-5 shadow-sm"><span className="text-2xl text-[#C8A45D]">{icon}</span><h3 className="mt-3 font-semibold text-[#202833]">{title}</h3><p className="mt-2 text-sm leading-6 text-slate-600">{text}</p></article>)}</div></div></section>
    <footer className="bg-[#142B3B] py-10 text-sm text-slate-200"><div className="wrap grid gap-8 sm:grid-cols-3"><div><p className="text-lg font-bold text-white">Harbor Hotels</p><p className="mt-2 max-w-xs leading-6">Distinct stays, local hospitality and easy online booking across India.</p></div><div><p className="font-semibold text-white">Explore</p><div className="mt-3 grid gap-2"><Link href="/hotels">Hotels</Link><Link href="/restaurant">Restaurants</Link><Link href="/services">Guest services</Link></div></div><div><p className="font-semibold text-white">Contact</p><p className="mt-3">help@harborhotels.example<br />+91 80000 00000</p></div></div><div className="wrap mt-8 border-t border-white/20 pt-5">© 2026 Harbor Hotels. All rights reserved.</div></footer>
  </main>;
}
