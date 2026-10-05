'use client';

import { FormEvent, useEffect, useRef, useState } from 'react';
import { api } from '../lib/api';

const categories = [
  ['website_experience', 'Website Experience'],
  ['booking_experience', 'Booking Experience'],
  ['room_hotel_services', 'Room and Hotel Services'],
  ['payment', 'Payment'],
  ['technical_issue', 'Technical Issue'],
  ['feature_request', 'Feature Request'],
  ['other', 'Other'],
];

export default function GeneralFeedbackForm() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [category, setCategory] = useState('');
  const [rating, setRating] = useState(0);
  const [message, setMessage] = useState('');
  const [suggestions, setSuggestions] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const submittingRef = useRef(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (!localStorage.getItem('token')) return;
    api<{ name: string; email: string }>('/auth/me')
      .then((profile) => { setName(profile.name); setEmail(profile.email); })
      .catch(() => undefined);
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submittingRef.current) return;
    setSuccess('');
    setError('');
    if (!rating) { setError('Please choose an overall rating.'); return; }
    if (message.trim().length < 3) { setError('Feedback must be at least 3 characters.'); return; }
    submittingRef.current = true;
    setSubmitting(true);
    try {
      await api('/feedback', { method: 'POST', body: JSON.stringify({ name, email, category, rating, message, suggestions }) });
      setSuccess('Thank you. Your feedback has been submitted.');
      setCategory(''); setRating(0); setMessage(''); setSuggestions('');
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to submit feedback. Please try again.');
    } finally { submittingRef.current = false; setSubmitting(false); }
  }

  function clearForm() {
    setCategory(''); setRating(0); setMessage(''); setSuggestions(''); setSuccess(''); setError('');
    if (!localStorage.getItem('token')) { setName(''); setEmail(''); }
  }

  return <section className="mt-7 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
    <h2 className="text-2xl font-bold">Share your feedback</h2>
    <p className="mt-2 text-slate-600">Tell us how we can improve your experience.</p>
    <form onSubmit={submit} className="mt-5 grid gap-4 sm:grid-cols-2" aria-busy={submitting}>
      <label className="grid gap-1 text-sm font-semibold">Name<input className="input w-full" autoComplete="name" required maxLength={150} value={name} onChange={(e) => setName(e.target.value)} /></label>
      <label className="grid gap-1 text-sm font-semibold">Email<input className="input w-full" type="email" autoComplete="email" required maxLength={320} value={email} onChange={(e) => setEmail(e.target.value)} /></label>
      <label className="grid gap-1 text-sm font-semibold sm:col-span-2">Feedback category<select className="input w-full" required value={category} onChange={(e) => setCategory(e.target.value)}><option value="">Choose a category</option>{categories.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
      <fieldset className="sm:col-span-2"><legend className="text-sm font-semibold">Overall rating <span aria-hidden="true">*</span></legend><div className="mt-1 flex items-center gap-1" role="radiogroup" aria-label="Overall rating, required">{[1, 2, 3, 4, 5].map((value) => <button key={value} type="button" role="radio" aria-checked={rating === value} aria-label={`${value} ${value === 1 ? 'star' : 'stars'}`} onClick={() => setRating(value)} className={`min-h-11 min-w-11 text-3xl ${value <= rating ? 'text-amber-500' : 'text-slate-300'}`}>{value <= rating ? '★' : '☆'}</button>)}<span className="ml-2 text-sm text-slate-600">{rating ? `${rating} / 5` : 'Select 1 to 5 stars'}</span></div></fieldset>
      <label className="grid gap-1 text-sm font-semibold sm:col-span-2">Feedback message<textarea className="input w-full" required minLength={3} maxLength={5000} rows={5} value={message} onChange={(e) => setMessage(e.target.value)} /></label>
      <label className="grid gap-1 text-sm font-semibold sm:col-span-2">Suggestions for improvement <span className="font-normal text-slate-500">(optional)</span><textarea className="input w-full" maxLength={2000} rows={3} value={suggestions} onChange={(e) => setSuggestions(e.target.value)} /></label>
      <div className="flex flex-wrap items-center gap-3 sm:col-span-2"><button className="btn" disabled={submitting}>{submitting ? 'Submitting…' : 'Submit Feedback'}</button><button type="button" disabled={submitting} onClick={clearForm} className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700">Clear form</button></div>
    </form>
    {success && <p role="status" className="mt-4 rounded-lg bg-emerald-50 p-3 text-emerald-800">{success}</p>}
    {error && <p role="alert" className="mt-4 rounded-lg bg-rose-50 p-3 text-rose-700">{error}</p>}
  </section>;
}
