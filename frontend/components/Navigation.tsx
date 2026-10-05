'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '../lib/api';

type Account = { name: string; roles: string[] };

export default function Navigation() {
  const [account, setAccount] = useState<Account | null>(null);
  const router = useRouter();
  useEffect(() => {
    const load = () => {
      if (!localStorage.getItem('token')) return setAccount(null);
      api<Account>('/auth/me').then(setAccount).catch(() => { localStorage.removeItem('token'); localStorage.removeItem('user'); setAccount(null); });
    };
    load(); window.addEventListener('harbor-auth-change', load); return () => window.removeEventListener('harbor-auth-change', load);
  }, []);
  async function logout() { try { await api('/auth/logout', { method: 'POST' }); } finally { localStorage.removeItem('token'); localStorage.removeItem('user'); window.dispatchEvent(new Event('harbor-auth-change')); router.push('/'); } }
  const initials = account?.name.split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase();
  return <nav className="sticky top-0 z-50 border-b border-white/10 bg-[#142B3B]/95 shadow-sm backdrop-blur" aria-label="Main navigation"><div className="wrap flex min-h-[4.5rem] items-center justify-between gap-4 py-3">
    <Link href="/" className="shrink-0 text-lg font-bold tracking-tight text-white"><span className="mr-2 text-[#C8A45D]">✦</span>Harbor Hotels</Link>
    <div className="hidden items-center gap-5 text-sm font-medium text-slate-100 lg:flex"><Link href="/">Home</Link><Link href="/hotels">Hotels</Link><Link href="/#services">Services</Link><Link href="/restaurant">Restaurants</Link><Link href="/feedback">Feedback</Link></div>
    {account ? <div className="hidden items-center gap-3 sm:flex"><span className="flex h-9 w-9 items-center justify-center rounded-full bg-[#C8A45D] text-sm font-bold text-[#142B3B]">{initials}</span><span className="text-sm font-semibold text-white">{account.name}</span><Link href="/profile" className="text-sm font-semibold text-white">My Account</Link><Link href="/bookings" className="text-sm font-semibold text-white">My Bookings</Link><Link href="/services" className="text-sm font-semibold text-white">Service Requests</Link><Link href="/feedback" className="text-sm font-semibold text-white">My Feedback</Link><button onClick={logout} className="rounded-lg border border-white/40 px-3 py-2 text-sm font-semibold text-white">Logout</button></div> : <div className="hidden items-center gap-3 sm:flex"><Link href="/login" className="text-sm font-semibold text-white">Sign in</Link><Link href="/register" className="rounded-lg border border-white/40 px-3 py-2 text-sm font-semibold text-white">Sign up</Link><Link href="/hotels" className="rounded-lg bg-[#C8A45D] px-3 py-2 text-sm font-bold text-[#142B3B]">Book now</Link></div>}
    <details className="relative sm:hidden"><summary className="cursor-pointer list-none rounded-lg border border-white/30 px-3 py-2 text-sm font-semibold text-white">Menu</summary><div className="absolute right-0 mt-2 grid w-52 gap-1 rounded-xl bg-white p-2 text-sm font-medium text-[#202833] shadow-xl"><Link className="rounded-lg px-3 py-2 hover:bg-slate-100" href="/">Home</Link><Link className="rounded-lg px-3 py-2 hover:bg-slate-100" href="/hotels">Hotels</Link><Link className="rounded-lg px-3 py-2 hover:bg-slate-100" href="/restaurant">Restaurants</Link><Link className="rounded-lg px-3 py-2 hover:bg-slate-100" href="/feedback">Feedback</Link>{account ? <><Link className="rounded-lg px-3 py-2 hover:bg-slate-100" href="/profile">My Account</Link><Link className="rounded-lg px-3 py-2 hover:bg-slate-100" href="/bookings">My Bookings</Link><Link className="rounded-lg px-3 py-2 hover:bg-slate-100" href="/services">Service Requests</Link><Link className="rounded-lg px-3 py-2 hover:bg-slate-100" href="/feedback">My Feedback</Link><button onClick={logout} className="rounded-lg px-3 py-2 text-left hover:bg-slate-100">Logout</button></> : <Link className="rounded-lg px-3 py-2 hover:bg-slate-100" href="/login">Sign in</Link>}</div></details>
  </div></nav>;
}
