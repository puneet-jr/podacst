/** Shared homepage/workspace waveform and editorial wordmark. */
export function Signal(){
 return <svg viewBox="0 0 32 32" fill="none" aria-hidden="true"><path d="M5 16h3l3-6 4 13 4-17 4 14 3-4h2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>;
}
export function Brand(){
 return <><span className="home-mark"><Signal/></span><span className="brand-wordmark">Lenny<small>Growth Assistant</small></span></>;
}
