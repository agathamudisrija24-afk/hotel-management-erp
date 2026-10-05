import Image from 'next/image';
import Link from 'next/link';

export type Hotel = {
  id: string;
  name: string;
  city: string;
  address: string;
  description: string;
  rating: string;
  hotel_type: string;
  images: { url: string; alt: string }[];
  services: { name: string; description: string }[];
  room_types: { id: string; name: string; description?: string; rate: string; capacity: number; available_rooms: number }[];
};

export default function HotelCard({ hotel }: { hotel: Hotel }) {
  const startingPrice = Math.min(...hotel.room_types.map((room) => Number(room.rate)));
  const image = hotel.images[0];

  return (
    <article className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg">
      {image && <Image src={image.url} alt={image.alt} width={800} height={500} className="h-52 w-full object-cover" />}
      <div className="p-5">
        <div className="mb-2 flex items-start justify-between gap-3">
          <div>
            <p className="text-sm font-medium text-teal-700">{hotel.city}</p>
            <h2 className="text-xl font-semibold text-slate-900">{hotel.name}</h2>
          </div>
          <span className="shrink-0 rounded-full bg-amber-50 px-2.5 py-1 text-sm font-semibold text-amber-800">★ {hotel.rating}</span>
        </div>
        <p className="line-clamp-2 text-sm leading-6 text-slate-600">{hotel.description}</p>
        <div className="mt-4 flex flex-wrap gap-2">{hotel.services.slice(0, 3).map((service) => <span key={service.name} className="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-700">{service.name}</span>)}</div>
        <div className="mt-5 flex items-end justify-between gap-3">
          <p className="text-sm text-slate-500">From <strong className="text-lg text-slate-900">₹{startingPrice.toLocaleString('en-IN')}</strong><br />per night</p>
          <div className="flex gap-2"><Link href={`/hotels/${hotel.id}`} className="rounded-lg px-2 py-2 text-sm font-semibold text-teal-800 hover:bg-teal-50">Details</Link><Link href={`/hotels/${hotel.id}#rooms`} className="btn text-sm">Book now</Link></div>
        </div>
      </div>
    </article>
  );
}
