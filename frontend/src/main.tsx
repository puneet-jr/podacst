import { StrictMode, useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

type Chat = {id:string;title:string;created_at:string;updated_at:string};
type Run = {id:string;status:string;error_code:string|null;retrieval_mode:string;attempt:number;output:null|{status:string}};
type Message = {id:string;client_message_id:string;content:string;role:string;created_at:string;run:Run|null;citations:{source_label:string;chunk_id:string}[]};
type Readiness = {status:string;checks:Record<string,{ready:boolean;status?:string}>};
type Corpus = {active_episodes:number;active_chunks:number;pending_items:number;latest:null|{status:string;discovered:number;selected:number;loaded:number;skipped:number;failed:number}};
type Providers = {selected:string;model:string;automatic_fallback:boolean};
type Source = {source_label:string;chunk_id:string;original_text:string;quote_spans:{text:string}[];source_url:string|null;video_url:string|null;metadata:{title:string;guest:string|null;source_path:string;source_hash:string;version:number;start_seconds:number|null;end_seconds:number|null;sponsor:boolean;metadata_warnings:string[]}};
type ChatEvent = {type:string;run_id:string;retrieval_mode:string;data:{run?:Run;sentence_count?:number}};
async function api<T>(path:string, options:RequestInit={}):Promise<T> {
  const response = await fetch('/api'+path,{...options,headers:{'Content-Type':'application/json',...options.headers}});
  const data = await response.json();
  if(!response.ok) throw new Error(data.error ? `${data.error.message} Reference: ${data.error.request_id}` : 'The service is not ready. Try again.');
  return data as T;
}
function timestamp(value:number|null){if(value===null)return 'Unavailable';const s=Math.floor(value);return [Math.floor(s/3600),Math.floor(s%3600/60),s%60].map(x=>String(x).padStart(2,'0')).join(':')}
function safeLink(value:string|null){if(!value)return undefined;try{const u=new URL(value);return u.protocol==='https:'&&!u.username&&!u.password&&['github.com','youtube.com','www.youtube.com','youtu.be'].includes(u.hostname)?u.href:undefined}catch{return undefined}}
function App(){
  const [chats,setChats]=useState<Chat[]>([]),[current,setCurrent]=useState<Chat|null>(null),[messages,setMessages]=useState<Message[]>([]);
  const [draft,setDraft]=useState(''),[title,setTitle]=useState(''),[error,setError]=useState(''),[busy,setBusy]=useState(false),[saving,setSaving]=useState(false),[stage,setStage]=useState('');
  const [readiness,setReadiness]=useState<Readiness|null>(null),[provider,setProvider]=useState<Providers|null>(null),[corpus,setCorpus]=useState<Corpus|null>(null);
  const [source,setSource]=useState<Source|null>(null),[sourceBusy,setSourceBusy]=useState(false);
  const pendingId=useRef<string|null>(null),loadSequence=useRef(0),sourceSequence=useRef(0),controller=useRef<AbortController|null>(null),activeRun=useRef<string|null>(null),retry=useRef(false);
  async function refresh(){
    try{const [sessions,settings]=await Promise.all([api<Chat[]>('/sessions'),api<Providers>('/providers')]);setChats(sessions);setProvider(settings)}catch(e){setError((e as Error).message)}
    try{setCorpus(await api<Corpus>('/ingestion/status'))}catch{setCorpus(null)}
    try{const r=await fetch('/api/health/ready');setReadiness(await r.json())}catch{setReadiness(null)}
  }
  useEffect(()=>{void refresh();const timer=setInterval(()=>{void api<Corpus>('/ingestion/status').then(setCorpus).catch(()=>setCorpus(null))},5000);return()=>{clearInterval(timer);controller.current?.abort()}},[]);
  async function open(chat:Chat){
    if(saving)return;
    const sequence=++loadSequence.current;++sourceSequence.current;setSourceBusy(false);setBusy(true);setError('');setSource(null);
    try{const items=await api<Message[]>(`/sessions/${chat.id}/messages`);if(sequence===loadSequence.current){setCurrent(chat);setMessages(items);setDraft('');pendingId.current=null;retry.current=false}}
    catch(e){setError((e as Error).message)}finally{if(sequence===loadSequence.current)setBusy(false)}
  }
  async function create(){
    if(!title.trim())return;
    ++loadSequence.current;++sourceSequence.current;setSourceBusy(false);setBusy(true);setError('');
    try{const chat=await api<Chat>('/sessions',{method:'POST',body:JSON.stringify({title})});setTitle('');setCurrent(chat);setMessages([]);setDraft('');setSource(null);pendingId.current=null;retry.current=false;await refresh()}
    catch(e){setError((e as Error).message)}finally{setBusy(false)}
  }
  async function ask(){
    if(!current||!draft.trim())return;
    const chat=current;setSaving(true);setError('');setStage('Saving your question…');pendingId.current??=crypto.randomUUID();controller.current=new AbortController();activeRun.current=null;
    let complete=false,terminal=false;
    try{
      const response=await fetch(`/api/sessions/${chat.id}/answers`,{method:'POST',headers:{'Content-Type':'application/json'},signal:controller.current.signal,body:JSON.stringify({content:draft,client_message_id:pendingId.current,retry:retry.current,retrieval_mode:'hybrid'})});
      if(!response.ok){const data=await response.json();throw new Error(data.error?.message||'The reply could not start.')}
      if(!response.body)throw new Error('The response stream is unavailable. Your saved question can be reopened.');
      const reader=response.body.getReader(),decoder=new TextDecoder();let buffer='';
      const receive=async(event:ChatEvent)=>{
        activeRun.current=event.run_id;
        if(event.type==='started'){setStage('Question saved. Starting local research…');setMessages(await api<Message[]>(`/sessions/${chat.id}/messages`))}
        if(event.type==='retrieving')setStage('Searching fresh transcript evidence…');
        if(event.type==='evidence_ready')setStage('Evidence found. Checking the question…');
        if(event.type==='generating')setStage('Selecting supported source excerpts…');
        if(['completed','failed','cancelled'].includes(event.type)){
          terminal=true;complete=event.type==='completed';setMessages(await api<Message[]>(`/sessions/${chat.id}/messages`));
          if(!complete){setError(event.type==='cancelled'?'Reply cancelled. Your question is saved. You can retry.':'The local reply failed. Your question is saved. You can retry.');retry.current=true}
        }
      };
      while(true){const item=await reader.read();if(item.done)break;buffer+=decoder.decode(item.value,{stream:true});let index:number;while((index=buffer.indexOf('\n'))>=0){const line=buffer.slice(0,index);buffer=buffer.slice(index+1);if(line.trim())await receive(JSON.parse(line))}}
      buffer+=decoder.decode();if(buffer.trim())await receive(JSON.parse(buffer));
      if(!terminal)throw new Error('The connection ended before a final result. Reopen the saved question and check its status.');
      if(complete){setDraft('');pendingId.current=null;retry.current=false}
      await refresh();
    }catch(e){setError((e as Error).name==='AbortError'?'Connection closed. Your question remains saved; refresh its status before retrying.':(e as Error).message);retry.current=true;try{setMessages(await api<Message[]>(`/sessions/${chat.id}/messages`))}catch{/* Retain draft while unavailable. */}}
    finally{setSaving(false);setStage('');activeRun.current=null;controller.current=null}
  }
  async function cancel(){if(!current)return;if(activeRun.current){try{await api(`/sessions/${current.id}/runs/${activeRun.current}/cancel`,{method:'POST'});setStage('Cancelling local reply…')}catch(e){setError((e as Error).message)}}else controller.current?.abort()}
  async function inspect(message:Message,label:string){if(!current)return;const sequence=++sourceSequence.current;setSourceBusy(true);setError('');try{const found=await api<Source>(`/sessions/${current.id}/messages/${message.id}/sources/${label}`);if(sequence===sourceSequence.current)setSource(found)}catch(e){if(sequence===sourceSequence.current)setError((e as Error).message)}finally{if(sequence===sourceSequence.current)setSourceBusy(false)}}
  function retryMessage(message:Message){setDraft(message.content);pendingId.current=message.client_message_id;retry.current=true;setError('')}
  return <div className="workspace">
    <aside className="sidebar"><div className="brand"><span className="mark">L</span><div>Lenny<span>GROWTH ASSISTANT</span></div></div>
      <div className="section-label">YOUR WORKSPACE</div><h1>Good questions.<br/>Saved thinking.</h1><p className="muted">Keep a separate space for every line of research.</p>
      <form className="new-chat" onSubmit={e=>{e.preventDefault();void create()}}><label htmlFor="title">Start a research session</label><input id="title" maxLength={160} value={title} onChange={e=>setTitle(e.target.value)} placeholder="e.g. Improving activation" disabled={busy||saving}/><button disabled={busy||saving||!title.trim()}>+ New session</button></form>
      <nav aria-label="Saved sessions"><div className="section-label">SAVED SESSIONS <span>{chats.length}</span></div>{chats.length===0?<p className="muted small">Your sessions will appear here.</p>:chats.map(chat=><button className={'session '+(current?.id===chat.id?'selected':'')} aria-current={current?.id===chat.id?'page':undefined} key={chat.id} disabled={busy||saving} onClick={()=>void open(chat)}><span>{chat.title}</span><small>{new Date(chat.updated_at).toLocaleDateString(undefined,{month:'short',day:'numeric'})}</small></button>)}</nav>
      <div className="local-badge"><span className="dot"/> LOCAL EVALUATOR<span>Private instance · independent sessions</span></div>
    </aside>
    <main><header><div><div className="section-label">RESEARCH WORKSPACE</div><h2>{current?.title||'A place to build your thinking'}</h2></div><button className="secondary" onClick={()=>{void refresh();if(current)void open(current)}} disabled={busy||saving}>Refresh</button></header>
      <div className="phase-note"><span>LOCAL RESEARCH</span> Replies quote selected transcript sentences. Inspect each source; related passages can still leave an evidence gap. Essays and artifacts arrive later.</div>
      {error&&<div role="alert" className="error">{error}</div>}
      <section className="conversation" aria-label="Session messages" aria-busy={busy||saving}>
        {!current?<div className="empty"><div className="empty-symbol">↗</div><div className="section-label">START WITH A QUESTION</div><h2>Give your next idea<br/>a little room.</h2><p>Create a session, ask about an indexed interview,<br/>then open the source behind each excerpt.</p></div>:messages.length===0?<div className="empty"><div className="empty-symbol">✎</div><h2>What would you like to explore?</h2><p>Ask a focused product or growth question.<br/>Name the guest when you have one in mind.</p></div>:messages.map(message=><article className={'message '+(message.role==='assistant'?'assistant':'')} key={message.id}><div className="message-meta"><strong>{message.role==='assistant'?'Lenny · source excerpts':'You'}</strong><time dateTime={message.created_at}>{new Date(message.created_at).toLocaleTimeString(undefined,{hour:'2-digit',minute:'2-digit'})}</time><span>{message.run?.status||'Saved'}</span></div><p>{message.content}</p>{message.role==='assistant'&&message.citations.length>0&&<div className="citations">{message.citations.map(c=><button key={c.source_label} className="secondary" onClick={()=>void inspect(message,c.source_label)} disabled={sourceBusy}>{c.source_label} · View source</button>)}</div>}{message.role==='user'&&message.run&&['failed','cancelled'].includes(message.run.status)&&<button className="secondary retry" disabled={saving} onClick={()=>retryMessage(message)}>Retry saved question</button>}</article>)}
      </section>
      {saving&&<div className="chat-progress" role="status" aria-live="polite">{stage}<button className="secondary" onClick={()=>void cancel()}>Cancel reply</button></div>}
      <form className="composer" onSubmit={e=>{e.preventDefault();void ask()}}><label htmlFor="draft">Your question</label><textarea id="draft" value={draft} maxLength={1000} onChange={e=>{setDraft(e.target.value);pendingId.current=null;retry.current=false}} placeholder={current?'Ask about an indexed interview…':'Create or open a session to begin'} disabled={!current||busy||saving}/><div><small>Local Ollama · fresh hybrid evidence search · saved to this session</small><button disabled={!current||busy||saving||!draft.trim()}>{saving?'Researching…':retry.current?'Retry question ↗':'Ask ↗'}</button></div></form>
    </main>
    <aside className="context" aria-label="Sources and workspace status">
      {source&&<section className="source-inspector" aria-label="Original source passage"><div className="section-label">SOURCE {source.source_label}<button className="secondary" onClick={()=>setSource(null)}>Close</button></div><h3>{source.metadata.title}</h3><p>{source.metadata.guest||'Guest not recorded'}</p><p>Observed markers: {timestamp(source.metadata.start_seconds)}{source.metadata.end_seconds!==null?' – '+timestamp(source.metadata.end_seconds):''}. These are transcript markers, not precise speech end times.</p>{source.metadata.sponsor&&<p className="source-warning">This passage may mix sponsored material and discussion. A promotion is not proof of effectiveness.</p>}{source.metadata.metadata_warnings.length>0&&<p className="source-warning">Source metadata needs review: {source.metadata.metadata_warnings.join(', ')}.</p>}<div className="source-links">{safeLink(source.source_url)&&<a href={safeLink(source.source_url)} target="_blank" rel="noopener noreferrer">Original transcript</a>}{safeLink(source.video_url)&&<a href={safeLink(source.video_url)} target="_blank" rel="noopener noreferrer">Video at observed marker</a>}</div><h4>Selected evidence</h4>{source.quote_spans.map((q,i)=><blockquote key={i}>{q.text}</blockquote>)}<h4>Stored original passage</h4><pre>{source.original_text}</pre><details><summary>Passage identity</summary><p>{source.chunk_id}<br/>{source.metadata.source_path}<br/>Version {source.metadata.version}<br/>SHA-256 {source.metadata.source_hash}</p></details></section>}
      <div className="section-label">WORKSPACE STATUS</div><h3>Ready for your work.</h3><dl>{['database','agent','ollama'].map(key=><div key={key}><dt>{key==='database'?'Saved sessions':key==='agent'?'Pi runtime':'Local model connection'}</dt><dd><span className={'dot '+(readiness?.checks[key]?.ready?'':'offline')}/>{readiness?.checks[key]?.ready?'Available':'Not ready'}</dd></div>)}</dl><div className="model"><div className="section-label">SELECTED PROVIDER</div><strong>{provider?.selected==='ollama'?'Ollama · local':'Checking…'}</strong><span>{provider?.model||'—'}</span><small>Automatic cloud fallback is off.</small></div><div className="corpus"><span className="section-label">TRANSCRIPT LIBRARY</span><h3>{corpus?`${corpus.active_episodes} episodes indexed`:'Index status unavailable'}</h3><p>{corpus?`${corpus.active_chunks} passages · ${corpus.latest?.discovered??0} source files discovered.`:'Refresh to check the local index.'}</p><p>Partial library. An available model does not establish answer quality.</p></div>
    </aside>
  </div>;
}
createRoot(document.getElementById('root')!).render(<StrictMode><App/></StrictMode>);
