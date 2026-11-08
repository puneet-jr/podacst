import {useState} from 'react';
import {Brand,Signal} from './Brand';
import {MessageText} from './MessageText';
import './home.css';

const steps = [
  {
    label: 'Ask', title: 'Start with a question.',
    description: 'Explore a product or growth problem with answers grounded in indexed interviews.',
    previewTitle: 'A question worth testing',
    previewText: 'How can I learn what customers would miss most about my product?',
    detailTitle: 'A way to find out',
    detail: 'Ask what customers would miss if the product disappeared, then use follow-up questions to understand why.',
  },
  {
    label: 'Trace', title: 'Open the evidence.',
    description: 'Inspect the passage behind an answer and follow it back to the interview.',
    previewTitle: 'Source inspector',
    previewText: 'How the must-have survey works',
    detailTitle: 'Sean Ellis · Product-market fit',
    detail: 'Open the original passage to see how Ellis describes the survey and its follow-up questions.',
  },
  {
    label: 'Make', title: 'Turn it into work.',
    description: 'Draft an evidence-led essay, review the claims, and save a Markdown or HTML artifact.',
    previewTitle: 'Saved artifact · Example',
    previewText: 'What would customers miss?',
    detailTitle: 'A starting point for your essay',
    detail: 'Explain the question, review the supporting evidence, then propose an experiment your team can run.',
  },
] as const;

const wave = [8, 13, 17, 11, 24, 39, 18, 31, 52, 34, 19, 47, 65, 43, 20, 35, 72, 54, 31, 15, 26, 47, 61, 34, 15, 29, 45, 23, 12, 19, 10, 5];


const sampleQuote = 'how would you feel if you could no longer use this product?';
const sampleDocument = `# What would customers miss?

> ${sampleQuote} [S1]

## A small experiment

Ask a small group of customers what they would miss. Compare their answers before choosing one onboarding step to test.`;

export function Home() {
  const [active, setActive] = useState(0);
  const [format, setFormat] = useState<'html'|'markdown'>('html');
  const step = steps[active];

  return <div className="lenny-home">
    <a className="skip-link" href="#home-main">Skip to content</a>
    <header className="home-masthead">
      <a className="home-brand" href="/" aria-label="Lenny Growth Assistant home">
        <Brand/>
      </a>
      <nav aria-label="Home navigation">
        <a className="home-overview" href="#workflow">How it works</a>
        <a className="home-nav-cta" href="/workspace">Open workspace <span aria-hidden="true">↗</span></a>
      </nav>
    </header>
    <main id="home-main" className="home-main" tabIndex={-1}>
      <section className="home-hero" aria-labelledby="home-title">
        <div className="home-intro">
          <p className="home-kicker"><span/> Product research · Lenny’s Podcast</p>
          <h1 id="home-title">From podcast<br className="home-break"/> to <em>playbook.</em></h1>
          <p className="home-lede">Ask a growth question, read the interview passage behind the answer, and turn what you learn into a document you can use.</p>
          <div className="home-actions">
            <a className="home-primary" href="/workspace">Open workspace <span aria-hidden="true">↗</span></a>
            <a className="home-secondary" href="#workflow">See the workflow <span aria-hidden="true">↓</span></a>
          </div>
        </div>
        <section className="home-preview" aria-labelledby="preview-heading">
          <div className="home-preview-top"><span className="home-preview-mark"><Signal/></span><h2 id="preview-heading">Field notes</h2><span className="home-example">Example · not live</span></div>
          <svg className="home-wave" viewBox="0 0 320 80" aria-hidden="true">
            {wave.map((height, index) => <rect key={index} x={index * 10 + 2} y={(80 - height) / 2} width="5" height={height} rx="2.5"/>)}
          </svg>
          <div className="home-preview-controls" role="group" aria-label="Choose a workspace preview">
            {steps.map((item, index) => <button key={item.label} type="button" aria-pressed={index === active} aria-controls="home-preview-body" onClick={() => setActive(index)}>
              <span aria-hidden="true">0{index + 1}</span> {item.label}
            </button>)}
          </div>
          <div className="home-preview-body" id="home-preview-body" aria-live="polite" aria-atomic="true">
            <p className="home-preview-label">{step.previewTitle}</p>
            {active === 0 && <>
              <p className="home-preview-question">{step.previewText}</p>
              <div className="home-evidence"><span className="home-evidence-label">A research starting point</span><p>Look for the benefit customers would miss, then read the interview passage behind the answer.</p></div>
              <button className="home-preview-link" onClick={() => setActive(1)}>Trace the example <span aria-hidden="true">→</span></button>
            </>}
            {active === 1 && <>
              <div className="home-source-meta"><span className="home-source-id">[S1]</span><span>Sean Ellis · Transcript excerpt</span></div>
              <blockquote className="home-source-quote">“{sampleQuote}”</blockquote>
              <p className="home-preview-caption">A short excerpt, kept with its source. In the workspace, open the original passage for context.</p>
              <button className="home-preview-link" onClick={() => setActive(2)}>Make something useful <span aria-hidden="true">→</span></button>
            </>}
            {active === 2 && <>
              <div className="home-artifact-toolbar"><span>research-note.{format === 'html' ? 'html' : 'md'}</span><div role="group" aria-label="Example artifact format">{(['html', 'markdown'] as const).map(kind => <button key={kind} aria-pressed={format === kind} onClick={() => setFormat(kind)}>{kind === 'html' ? 'HTML' : 'Markdown'}</button>)}</div></div>
              <div className="home-artifact-preview">{format === 'markdown' ? <pre className="home-markdown">{sampleDocument}</pre> : <MessageText text={sampleDocument} labels={['S1']} inspect={() => setActive(1)}/>}</div>
              <p className="home-preview-caption">Example saved document · select [S1] to trace its source.</p>
            </>}
          </div>
          <div className="home-preview-bottom"><span>Research workspace</span><span>0{active + 1} / 03</span></div>
        </section>
      </section>
      <section className="home-workflow" id="workflow" aria-labelledby="workflow-title">
        <div className="home-workflow-heading"><p>THE WORKFLOW</p><h2 id="workflow-title">From question to artifact.</h2></div>
        <ol>{steps.map((item, index) => <li key={item.label}>
          <span className="home-step-index">0{index + 1} / {item.label}</span>
          <h3>{item.title}</h3><p>{item.description}</p>
        </li>)}</ol>
      </section>
    </main>
    <footer className="home-footer"><span>The Lenny Growth Assistant</span><span>Built around Lenny’s Podcast transcripts</span></footer>
  </div>;
}
