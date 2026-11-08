export type Chat={id:string;title:string;created_at:string;updated_at:string};
export type Run={id:string;status:string;error_code:string|null;attempt:number;output:null|{status:string}};
export type Message={id:string;client_message_id:string;content:string;role:string;created_at:string;run:Run|null;citations:{source_label:string;chunk_id:string}[]};
export type Source={source_label:string;chunk_id:string;original_text:string;quote_spans:{text:string}[];source_url:string|null;video_url:string|null;metadata:{provider?:string;title:string;guest:string|null;source_path:string;source_hash:string;version:number;start_seconds:number|null;end_seconds:number|null;sponsor:boolean;metadata_warnings:string[]}};
export type Essay={id:string;status:string;error_code:string|null;request:{topic:string};sections:{heading:string;body:string;advice?:string;source_ids:string[]}[];draft_md:string|null;validation:null|{word_count:number;passed_deterministic:boolean;errors:{code:string}[]};metadata:{provider?:string;model?:string;fact_sections?:{source_ids:string[];facts:{text:string}[]}[]};assistant_message_id:string|null};
export type EssaySummary={id:string;status:string;topic:string;error_code:string|null};
export async function api<T>(path:string,options:RequestInit={}):Promise<T>{
 const response=await fetch('/api'+path,{...options,headers:{'Content-Type':'application/json',...options.headers}});let data;try{data=await response.json()}catch{throw new Error('The service did not return a response. Your input is kept; refresh before retrying.')}
 if(!response.ok)throw new Error(data.error?`${data.error.message} Reference: ${data.error.request_id}`:'The service is unavailable. Your input is kept.');return data as T;
}
export function issue(code:string|null|undefined){
 if(code?.includes('timeout'))return 'The local model took too long. Your request is saved.';
 if(code==='app_restarted')return 'The app restarted before this draft finished. Your request is saved.';
 if(code?.includes('unavailable')||code==='rpc_rejected')return 'The local model could not answer. Check Ollama and the installed model, then refresh.';
 if(code==='cancelled')return 'Generation cancelled. Your request is saved.';
 if(code==='essay_evidence_too_thin')return 'There is not enough usable evidence for this essay. Try a narrower topic or another indexed interview.';
 return 'This draft needs attention. Your request and partial output are saved.';
}
export function safeLink(value:string|null){if(!value)return undefined;try{const u=new URL(value);return u.protocol==='https:'&&!u.username&&!u.password&&['github.com','youtube.com','www.youtube.com','youtu.be'].includes(u.hostname)?u.href:undefined}catch{return undefined}}
export function timestamp(value:number|null){if(value===null)return 'Unavailable';const s=Math.floor(value);return [Math.floor(s/3600),Math.floor(s%3600/60),s%60].map(x=>String(x).padStart(2,'0')).join(':')}
export function sourceSpan(original:string,quote:string){
 const start=original.indexOf(quote);if(start<0||!quote)throw new Error('Quoted evidence must match the stored source exactly. Copy an exact excerpt; put your own wording in Application.');
 // The API uses Unicode code-point offsets; JS string indices count UTF-16 units.
 const pointStart=Array.from(original.slice(0,start)).length;return {start:pointStart,end:pointStart+Array.from(quote).length};
}
