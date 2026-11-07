import {Fragment} from 'react';
// Small escaped-text renderer. No HTML sink or untrusted URL interpretation.
export function MessageText({text,labels=[],inspect}:{text:string;labels?:string[];inspect?:(label:string)=>void}){
 function inline(value:string){return value.split(/(\*\*[^*\n]+\*\*|\[S\d+\])/g).map((part,i)=>part.startsWith('**')?<strong key={i}>{part.slice(2,-2)}</strong>:/^\[S\d+\]$/.test(part)&&labels.includes(part.slice(1,-1))&&inspect?<button className="inline-citation" key={i} onClick={()=>inspect(part.slice(1,-1))}>{part}</button>:<Fragment key={i}>{part}</Fragment>)}
 return <div className="message-text">{text.split(/\n\s*\n/).map((block,i)=>/^#{1,6} /.test(block)?<h3 key={i}>{inline(block.replace(/^#{1,6} /,''))}</h3>:block.startsWith('> ')?<blockquote key={i}>{inline(block.replace(/^> ?/gm,''))}</blockquote>:/^[-*] /.test(block)?<ul key={i}>{block.split('\n').map((line,n)=><li key={n}>{inline(line.replace(/^[-*] /,''))}</li>)}</ul>:<p key={i}>{inline(block)}</p>)}</div>
}
