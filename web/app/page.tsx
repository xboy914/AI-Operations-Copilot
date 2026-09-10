"use client";
import {FormEvent,useEffect,useState} from "react";
type Run={thread_id:string;status:string;request:string;tool_name?:string;approval?:{description:string;arguments:Record<string,unknown>}};
const API=process.env.NEXT_PUBLIC_API_URL??"http://localhost:8000";
export default function Home(){
 const[token,setToken]=useState("");const[request,setRequest]=useState("Follow up with the delayed supplier");const[runs,setRuns]=useState<Run[]>([]);const[error,setError]=useState("");
 async function call(path:string,init?:RequestInit){const response=await fetch(`${API}${path}`,{...init,headers:{"Content-Type":"application/json",Authorization:`Bearer ${token}`,...init?.headers}});if(!response.ok)throw new Error(`Request failed: ${response.status}`);return response.json()}
 async function refresh(){if(!token)return;try{setRuns(await call("/agent/runs"));setError("")}catch(reason){setError(reason instanceof Error?reason.message:"Unable to load runs")}}
 useEffect(()=>{const timer=window.setInterval(refresh,1500);refresh();return()=>window.clearInterval(timer)},[token]);
 async function start(event:FormEvent){event.preventDefault();await call("/agent/runs",{method:"POST",body:JSON.stringify({request})});await refresh()}
 async function decide(id:string,approved:boolean){await call(`/agent/runs/${id}/decision`,{method:"POST",body:JSON.stringify({approved})});await refresh()}
 const waiting=runs.filter(run=>run.status==="waiting_approval");
 return <main><header><span className="eyebrow">AGENTIC OPERATIONS / LIVE CONTROL</span><h1>AI Operations<br/><em>Copilot</em></h1><p>Auditable agent workflows with human control.</p></header>
 <section className="panel"><div><span className="live">● CONTROL PLANE ONLINE</span><h2>Agent command center</h2></div><input aria-label="Access token" type="password" value={token} onChange={e=>setToken(e.target.value)} placeholder="Paste JWT access token"/><form onSubmit={start}><input value={request} onChange={e=>setRequest(e.target.value)}/><button disabled={!token}>Run agent</button></form>{error&&<p>{error}</p>}</section>
 <section className="grid two"><div><h2>Approval inbox · {waiting.length}</h2>{waiting.map(run=><article key={run.thread_id}><small>{run.tool_name}</small><h3>{run.request}</h3><p>{run.approval?.description}</p><pre>{JSON.stringify(run.approval?.arguments,null,2)}</pre><button onClick={()=>decide(run.thread_id,true)}>Approve</button> <button onClick={()=>decide(run.thread_id,false)}>Reject</button></article>)}</div>
 <div><h2>Live execution · {runs.length}</h2>{runs.map(run=><article key={run.thread_id}><small>{run.status.replaceAll("_"," ")}</small><h3>{run.request}</h3><p>{run.tool_name??"Planning"} · {run.thread_id.slice(0,8)}</p></article>)}</div></section></main>
}