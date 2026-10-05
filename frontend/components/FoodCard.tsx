'use client';

import Image from 'next/image';
import { useState } from 'react';

export type FoodItem = {
  id: string;
  name: string;
  description: string;
  price: string;
  vegetarian: boolean;
  image_url: string;
  available: boolean;
};

export default function FoodCard({ item, onAdd }: { item: FoodItem; onAdd: (item: FoodItem) => void }) {
  // Existing database seeds point at loremflickr, which now rejects requests.
  // Skip that host entirely so Next's image optimizer doesn't emit 401 errors.
  const [imageFailed, setImageFailed] = useState(() => item.image_url.includes('loremflickr.com'));
  return <article className="group overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition duration-300 hover:-translate-y-1 hover:shadow-xl">
    <div className="relative h-48 overflow-hidden bg-[#142B3B]">
      {!imageFailed && item.image_url ? <Image src={item.image_url} alt={item.name} fill sizes="(max-width: 768px) 100vw, 33vw" className="object-cover transition duration-500 group-hover:scale-105" onError={() => setImageFailed(true)} /> : <div className="flex h-full items-center justify-center bg-gradient-to-br from-[#142B3B] to-[#31566a] px-6 text-center font-semibold text-white">{item.name}</div>}
      <span className={`absolute left-3 top-3 rounded-full px-3 py-1 text-xs font-semibold ${item.vegetarian ? 'bg-emerald-50 text-emerald-800' : 'bg-rose-50 text-rose-800'}`}>{item.vegetarian ? '● Vegetarian' : '● Non-vegetarian'}</span>
    </div>
    <div className="p-5"><div className="flex gap-3"><h3 className="flex-1 text-lg font-semibold text-[#202833]">{item.name}</h3><span className="text-lg font-bold text-[#142B3B]">₹{item.price}</span></div><p className="mt-2 min-h-12 text-sm leading-6 text-slate-600">{item.description}</p><div className="mt-4 flex items-center justify-between"><span className={`text-xs font-medium ${item.available ? 'text-emerald-700' : 'text-rose-700'}`}>{item.available ? 'Available today' : 'Currently unavailable'}</span><button onClick={() => onAdd(item)} disabled={!item.available} className="rounded-lg border border-[#C8A45D] px-3 py-1.5 text-sm font-semibold text-[#142B3B] transition hover:bg-[#C8A45D] disabled:cursor-not-allowed disabled:opacity-50">Add to order</button></div></div>
  </article>;
}
