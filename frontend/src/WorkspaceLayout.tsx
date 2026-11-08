import {useEffect,useRef,useState,type PointerEvent} from 'react';

const KEY='lenny.workspace.widths.v1';
const DEFAULTS={sessions:208,context:292};
const LIMITS={sessionsMin:184,sessionsMax:300,contextMin:260,contextMax:620,researchMin:480,dividers:20};
const clamp=(value:number,min:number,max:number)=>Math.min(Math.max(value,min),Math.max(min,max));
function savedWidths(){
 try{
  const value=JSON.parse(localStorage.getItem(KEY)||'null');
  if(Number.isFinite(value?.sessions)&&Number.isFinite(value?.context))return {sessions:clamp(value.sessions,184,300),context:clamp(value.context,260,620)};
 }catch{/* Storage is optional; layout remains usable when unavailable. */}
 return DEFAULTS;
}
export function useWorkspaceLayout(){
 const [widths,setWidths]=useState(savedWidths),[viewport,setViewport]=useState(innerWidth);
 const [collapsed,setCollapsed]=useState(false),[expanded,setExpanded]=useState(false),[readerWidth,setReaderWidth]=useState(720);
 useEffect(()=>{const resize=()=>setViewport(innerWidth);window.addEventListener('resize',resize);return()=>window.removeEventListener('resize',resize)},[]);
 useEffect(()=>{try{localStorage.setItem(KEY,JSON.stringify(widths))}catch{/* Private/restricted storage must not block resizing. */}},[widths]);
 const sessions=collapsed?60:clamp(widths.sessions,LIMITS.sessionsMin,LIMITS.sessionsMax);
 const contextMax=Math.min(expanded?800:LIMITS.contextMax,viewport-sessions-LIMITS.dividers-LIMITS.researchMin);
 const context=clamp(expanded?readerWidth:widths.context,LIMITS.contextMin,contextMax);
 const sessionsMax=Math.min(LIMITS.sessionsMax,viewport-context-LIMITS.dividers-LIMITS.researchMin);
 function resizeSessions(value:number){
  if(collapsed&&value<=60)return;
  setCollapsed(false);setWidths(old=>({...old,sessions:clamp(value,LIMITS.sessionsMin,sessionsMax)}));
 }
 function resizeContext(value:number){
  const next=clamp(value,LIMITS.contextMin,contextMax);
  if(expanded)setReaderWidth(next);else setWidths(old=>({...old,context:next}));
 }
 return {sessions,context,collapsed,setCollapsed,expanded,setExpanded,
  sessionsMax,contextMax,resizeSessions,resizeContext,
  resetSessions:()=>{setCollapsed(false);setWidths(old=>({...old,sessions:DEFAULTS.sessions}))},
  resetContext:()=>{if(expanded)setReaderWidth(720);else setWidths(old=>({...old,context:DEFAULTS.context}))}};
}

type DividerProps={panel:'Sessions'|'Sources and Documents';value:number;min:number;max:number;controls:string;reverse?:boolean;resize:(value:number)=>void;reset:()=>void};
export function PanelDivider({panel,value,min,max,controls,reverse=false,resize,reset}:DividerProps){
 const drag=useRef<{x:number;width:number;id:number}|null>(null);
 useEffect(()=>()=>{document.documentElement.classList.remove('resizing-panels')},[]);
 function end(e:PointerEvent<HTMLDivElement>){
  if(drag.current?.id!==e.pointerId)return;
  drag.current=null;document.documentElement.classList.remove('resizing-panels');
  if(e.currentTarget.hasPointerCapture(e.pointerId))e.currentTarget.releasePointerCapture(e.pointerId);
 }
 return <div className="panel-divider" role="separator" tabIndex={0} aria-label={`Resize ${panel}`} aria-orientation="vertical" aria-controls={controls} aria-valuemin={min} aria-valuemax={Math.max(min,Math.round(max))} aria-valuenow={Math.round(value)} aria-valuetext={`${Math.round(value)} pixels`} title={`Drag to resize ${panel}. Arrow keys resize; Shift for larger steps. Double-click or Enter to reset.`}
  onPointerDown={e=>{if(e.button!==0)return;e.preventDefault();e.currentTarget.focus();e.currentTarget.setPointerCapture(e.pointerId);drag.current={x:e.clientX,width:value,id:e.pointerId};document.documentElement.classList.add('resizing-panels')}}
  onPointerMove={e=>{const start=drag.current;if(start?.id===e.pointerId)resize(start.width+(e.clientX-start.x)*(reverse?-1:1))}}
  onPointerUp={end} onPointerCancel={end} onLostPointerCapture={()=>{drag.current=null;document.documentElement.classList.remove('resizing-panels')}}
  onDoubleClick={reset} onKeyDown={e=>{const step=e.shiftKey?40:10;const direction=reverse?-1:1;
   if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();resize(value+(e.key==='ArrowRight'?step:-step)*direction)}
   else if(e.key==='Home'||e.key==='End'){e.preventDefault();resize(e.key==='Home'?min:max)}
   else if(e.key==='Enter'){e.preventDefault();reset()}
  }}><span aria-hidden="true"/></div>;
}
