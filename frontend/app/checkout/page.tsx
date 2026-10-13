'use client';
import {Suspense,useState} from 'react';
import {useSearchParams,useRouter} from 'next/navigation';
import {api} from '../../lib/api';

function CheckoutForm(){
  const p=useSearchParams(),r=useRouter(); const [check_in,setIn]=useState(''),[check_out,setOut]=useState(''),[msg,setMsg]=useState('');
  const now=new Date(),today=`${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`;
  const updateDate=(setter:(value:string)=>void,value:string)=>{if(value===''||/^\d{4}-\d{2}-\d{2}$/.test(value))setter(value)};
  async function submit(e:React.FormEvent){e.preventDefault();setMsg('');const validDate=(v:string)=>{if(!/^\d{4}-\d{2}-\d{2}$/.test(v))return false;const d=new Date(`${v}T00:00:00.000Z`);return !Number.isNaN(d.valueOf())&&d.toISOString().slice(0,10)===v};if(!validDate(check_in)||!validDate(check_out)){setMsg('Enter valid check-in and check-out dates using a four-digit year.');return}if(check_in<today){setMsg('Check-in must be today or a future date.');return}if(check_out<=check_in){setMsg('Check-out must be later than check-in.');return}try{const b=await api('/bookings',{method:'POST',headers:{'Idempotency-Key':crypto.randomUUID()},body:JSON.stringify({hotel_id:p.get('hotel'),room_type_id:p.get('room'),check_in,check_out,guests:1})});const pay=await api('/payments/initiate?booking_id='+b.id,{method:'POST',headers:{'Idempotency-Key':crypto.randomUUID()}});const done=await api('/payments/'+pay.payment_id+'/verify',{method:'POST'});r.push('/bookings?confirmed='+done.booking.reference)}catch(e:any){setMsg(e.message)}}
  return <main className="wrap"><h1>Secure checkout</h1><p>Demo mode uses the mock payment provider. A booking is only confirmed after payment verification.</p><form className="card" onSubmit={submit}><label>Check-in <input className="input" type="date" min={today} max="9999-12-31" required value={check_in} onChange={e=>updateDate(setIn,e.target.value)}/></label><label>Check-out <input className="input" type="date" min={today} max="9999-12-31" required value={check_out} onChange={e=>updateDate(setOut,e.target.value)}/></label><button className="btn">Pay and confirm</button>{msg&&<p role="alert">{msg}</p>}</form></main>
}
export default function Checkout(){return <Suspense fallback={<main className="wrap">Loading checkout…</main>}><CheckoutForm/></Suspense>}
