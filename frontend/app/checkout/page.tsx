'use client';
import {Suspense,useState} from 'react';
import {useSearchParams,useRouter} from 'next/navigation';
import {api} from '../../lib/api';

function CheckoutForm(){
  const p=useSearchParams(),r=useRouter(); const [check_in,setIn]=useState(''),[check_out,setOut]=useState(''),[msg,setMsg]=useState('');
  async function submit(e:React.FormEvent){e.preventDefault();try{const b=await api('/bookings',{method:'POST',headers:{'Idempotency-Key':crypto.randomUUID()},body:JSON.stringify({hotel_id:p.get('hotel'),room_type_id:p.get('room'),check_in,check_out,guests:1})});const pay=await api('/payments/initiate?booking_id='+b.id,{method:'POST',headers:{'Idempotency-Key':crypto.randomUUID()}});const done=await api('/payments/'+pay.payment_id+'/verify',{method:'POST'});r.push('/bookings?confirmed='+done.booking.reference)}catch(e:any){setMsg(e.message)}}
  return <main className="wrap"><h1>Secure checkout</h1><p>Demo mode uses the mock payment provider. A booking is only confirmed after payment verification.</p><form className="card" onSubmit={submit}><label>Check-in <input className="input" type="date" required value={check_in} onChange={e=>setIn(e.target.value)}/></label><label>Check-out <input className="input" type="date" required value={check_out} onChange={e=>setOut(e.target.value)}/></label><button className="btn">Pay and confirm</button>{msg&&<p>{msg}</p>}</form></main>
}
export default function Checkout(){return <Suspense fallback={<main className="wrap">Loading checkout…</main>}><CheckoutForm/></Suspense>}
