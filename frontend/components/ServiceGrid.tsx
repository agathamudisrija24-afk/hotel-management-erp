const icons: Record<string, string> = {
  'Free Wi-Fi': '⌁', 'Swimming pool': '◌', 'Spa and wellness': '✦', 'Beach access': '⌇', 'Fine dining': '✧', 'Airport transfers': '↗', 'Rooftop dining': '◒', 'Banquet hall': '◇', '24-hour front desk': '◷', 'Free parking': '▣', 'Mountain-view rooms': '△', 'Bonfire evenings': '♨', 'Trekking assistance': '↟', 'Restaurant and dining': '✧', Housekeeping: '✦', 'Business lounge': '▤', Gym: '◉', 'Multi-cuisine restaurant': '✧', 'Laundry service': '◫', 'Tea garden views': '♧', 'Nature walks': '⌁', 'Ayurvedic spa': '✦', 'Kerala restaurant': '✧',
};

export type Service = { name: string; description: string };

export default function ServiceGrid({ services, limit }: { services: Service[]; limit?: number }) {
  const visible = limit ? services.slice(0, limit) : services;
  if (!visible.length) return null;
  return <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{visible.map((service, index) => <article key={service.name} className={`rounded-2xl p-5 transition duration-300 hover:-translate-y-1 hover:shadow-lg ${index % 3 === 0 ? 'bg-[#142B3B] text-white' : index % 3 === 1 ? 'bg-[#f3ead8] text-[#202833]' : 'bg-white text-[#202833] shadow-sm ring-1 ring-slate-200'}`}><span className="flex h-11 w-11 items-center justify-center rounded-xl bg-white/20 text-2xl">{icons[service.name] ?? '✦'}</span><h3 className="mt-4 font-semibold">{service.name}</h3><p className="mt-2 text-sm leading-6 opacity-80">{service.description}</p></article>)}</div>;
}
