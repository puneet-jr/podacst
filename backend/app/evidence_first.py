"""Topic retrieval -> immutable verbatim facts -> Pi advice -> explicit review.

No approved fixture injection. Quotes are traceable, not automatically relevant
or semantically certified; the reviewer must check every section before accept.
"""
import asyncio,re,time
from hashlib import sha256
from pathlib import Path
from backend.app.observability import emit
from backend.app.agent import PiRPC,ROOT
from backend.app.essays import EssayService,collect_evidence,save_progress,finish_cleanup
from backend.app.writing import EssayError,validate_essay,assemble,word_count


def balanced_quotation(quote):
    """A punctuation boundary inside a direct quotation is not its end.

    This is a syntax guard, not a grammatical or factual-support judgment.
    Apostrophes in contractions are intentionally not quotation delimiters.
    """
    straight=False;curly=0
    for char in quote:
        if char=='"':straight=not straight
        elif char=='“':curly+=1
        elif char=='”':
            curly-=1
            if curly<0:return False
    return not straight and curly==0


def fact_plan(sources,topic):
    result=[];used=set()
    names=['Ask the question before changing the journey','Read the case in its context','Find the benefit users describe','Choose what to investigate','Turn observations into a test','Keep the limits visible']
    for label,s in sources.items():
        original=s['original_text'];guest=s.get('guest') or ''
        markers=list(re.finditer(r'^([^\n]{1,90}) \(\d{2}:\d{2}:\d{2}\):\s*\n',original,re.M));candidates=[]
        for n,marker in enumerate(markers):
            if marker[1]!=guest:continue
            end=markers[n+1].start() if n+1<len(markers) else len(original)
            part=original[marker.end():end]
            for raw in re.split(r'\n\s*\n',part):
                raw=re.sub(r'^\(\d{2}:\d{2}:\d{2}\):\s*','',raw).strip()
                if len(raw)<70 or re.search(r'https?://|[<>\[\]]',raw):continue
                # End only on a complete sentence; never manufacture a quotation.
                matches=list(re.finditer(r'[.!?][”\"]?(?=\s|$)',raw))
                ends=[m.end() for m in matches if 20<=word_count(raw[:m.end()])<=130 and balanced_quotation(raw[:m.end()])]
                if not ends:continue
                quote=raw[:max(ends)]
                start=original.find(quote)
                if start<0 or sha256(quote.encode()).hexdigest() in used:continue
                terms=set(re.findall(r'[a-z]{4,}',topic.lower()))-{'users','product','improve','customer','feedback'}
                score=sum(t in quote.lower() for t in terms)
                candidates.append((score,word_count(quote),start,quote))
        candidates.sort(reverse=True)
        facts=[];count=0
        for _,wc,start,quote in candidates:
            if count>=100:break
            if count+wc>160:continue
            fingerprint=sha256(quote.encode()).hexdigest()
            if fingerprint in used:continue
            used.add(fingerprint);facts.append({'text':quote,'source_id':label,'chunk_id':s['id'],'start':start,'end':start+len(quote),'sha256':fingerprint});count+=wc
        if facts:result.append({'heading':names[len(result)],'facts':facts,'source_ids':[label]})
        if len(result)==6:break
    return result


def render_body(section,advice,index):
    factual='\n\n'.join('> '+f['text'].replace('\n','\n> ')+' ['+f['source_id']+']' for f in section['facts'])
    if index==5:
        lines=re.split(r'(?<=[.!?])\s+',advice.strip());application='\n'.join('- Application: '+line for line in lines if line)
    else:application='Application: '+('**Treat improvement as a hypothesis.** ' if index==2 else '')+advice.strip()
    return application+'\n\n'+factual if index==0 else factual+'\n\n'+application


class EvidenceFirstService(EssayService):
    async def advice(self,run,index,prompt,metadata):
        stage={'stage':'application-'+str(index+1)+'-'+str(len(metadata['stages'])),'section':index+1,'model':self.settings.selected_model(essay=True)};metadata['stages'].append(stage)
        directory=Path('/app/evidence/private-chat/essays')/str(run['id'])/stage['stage']
        rpc=PiRPC(directory,settings=self.settings,tool_name='',extension=ROOT/'agent/application_advice.ts',system='Write proposed advice only.',model=self.settings.selected_model(essay=True),max_tokens=384,require_tool=False,extra_env={'LENNY_ADVICE_OUTPUT_TOKENS':'384'})
        t=time.monotonic()
        try:
            async with asyncio.timeout(90):
                state=await rpc.start();stage['initial_message_count']=state.get('messageCount');r=await rpc.ask(prompt)
                stage.update(model_text=r['model_text'],pi_session_id=r['session_id'])
                last=next(v for v in reversed(r['messages']) if v.get('role')=='assistant');stage['stop_reason']=last.get('stopReason');stage['usage']={k:v for k,v in last.get('usage',{}).items() if k!='cost'}
                if stage['stop_reason'] in {'length','maxTokens'}:raise EssayError('essay_output_truncated',502)
                return r['model_text']
        finally:
            await finish_cleanup(rpc.close());stage.update(duration_seconds=time.monotonic()-t,process_reaped=rpc.process.returncode is not None if rpc.process else True);stage.setdefault('model_text',rpc.last_model_text)
            await asyncio.to_thread(save_progress,self.engine,run['id'],metadata=metadata)

    async def execute(self,run,notify):
        started=time.monotonic();acquired=False;status='failed';error='essay_generation_failed';sections=[]
        meta={**run['metadata'],'model':self.settings.selected_model(essay=True),'provider':self.settings.provider_id,'workflow':'evidence_first_v1','retrieval_mode':'hybrid','stages':[],'repairs_used':0,'facts_are':'verbatim selected guest passages; relevance and qualifications require manual review','advice_edits':[]}
        try:
            if self.lock.locked():raise EssayError('local_generation_busy',503)
            await self.lock.acquire();acquired=True
            async with asyncio.timeout(run['request']['timeout_seconds']):
                await notify('retrieving',{})
                sources,packet,receipts=await asyncio.to_thread(collect_evidence,self.engine,self.settings,run);meta['retrievals']=receipts
                plan=fact_plan(sources,run['request']['topic']);meta['fact_sections']=plan
                if len(plan)!=6:status,error='insufficient_evidence','essay_evidence_too_thin';return
                title=run['request']['topic'].rstrip('.');outline={'status':'ready','title':title,'sections':[{'heading':s['heading'],'purpose':'Read this retrieved evidence and distinguish proposed application.','source_ids':s['source_ids']} for s in plan]}
                await asyncio.to_thread(save_progress,self.engine,run['id'],outline=outline,metadata=meta)
                facts=sum(word_count(f['text']) for s in plan for f in s['facts']);target=max(55,min(150,round((1250-facts-55)/6)))
                focuses=['Start with a reader question and propose a feedback research brief.','Propose comparing a current signup promise and first task with a revision.','Propose an open-ended benefit question and a way to review contradictory responses.','Propose choosing a single feature or benefit to investigate.','Propose a concrete experiment, a completion metric and a keep-or-revise decision.','Give at least four complete proposed action sentences with a practical final decision.']
                # Case history and factual constraints belong to server evidence, not the advice-only drafter.
                base='Audience: '+run['request']['audience']+'. Write ONLY a plain application paragraph, no headings/labels/IDs or citations. No history or factual claims. Do not restate transcript material. Any benefit must be an explicit hypothesis. Avoid promised effects, meta instructions and caveats about promises. Finish with a concrete next action. '
                for i,s in enumerate(plan):
                    await notify('drafting',{'section':i+1,'target_words':target})
                    raw=await self.advice(run,i,base+focuses[i]+f' Draft around {target} words.',meta)
                    sections.append({'heading':s['heading'],'body':render_body(s,raw,i),'source_ids':s['source_ids'],'error':None,'advice':raw})
                    await asyncio.to_thread(save_progress,self.engine,run['id'],sections=sections,draft_md=assemble(title,sections),metadata=meta)
                await notify('validating',{})
                validation=validate_essay(title,sections,sources)
                if not 1125<=validation['word_count']<=1375:
                    meta['repairs_used']=1;meta['pre_repair_sections']=sections.copy();meta['pre_repair_validation']=validation
                    i=4;old=word_count(sections[i]['advice']);new_target=max(35,min(245,old+1250-validation['word_count']))
                    await notify('repairing',{'section':i+1,'target_words':new_target})
                    raw=await self.advice(run,i,base+focuses[i]+f' This is the single length revision. Write around {new_target} words, adding useful measurement and review steps rather than repetition.',meta)
                    sections[i]={**sections[i],'body':render_body(plan[i],raw,i),'advice':raw}
                    validation=validate_essay(title,sections,sources)
                status,error=('needs_review',None) if validation['passed_deterministic'] else ('failed','essay_rubric_failed')
                await asyncio.to_thread(save_progress,self.engine,run['id'],sections=sections,draft_md=assemble(title,sections),validation=validation,metadata=meta)
        except asyncio.CancelledError:status,error='cancelled','cancelled'
        except TimeoutError:status,error='failed','essay_timeout'
        except Exception as exc:meta['failure_type']=type(exc).__name__;error=getattr(exc,'code','essay_generation_failed')
        finally:
            async def finalize():
                meta['elapsed_seconds']=time.monotonic()-started
                emit('essay_operation',run_id=run['id'],session_id=run['session_id'],provider=self.settings.provider_id,model=self.settings.selected_model(essay=True),status=status,code=error or 'ok',duration_ms=round(meta['elapsed_seconds']*1000,2))
                try:
                    await asyncio.to_thread(save_progress,self.engine,run['id'],status=status,error_code=error,metadata=meta)
                    from backend.app.essays import load_essay
                    current=await asyncio.to_thread(load_essay,self.engine,self.settings,run['session_id'],run['id']);await notify(status,{'run':current})
                finally:
                    if acquired:self.lock.release()
                    self.tasks.pop(run['id'],None)
            await finish_cleanup(finalize())


def edit_advice(engine,settings,sid,rid,changes):
    """Explicit editorial changes only; immutable factual excerpts cannot change."""
    from backend.app.essays import load_essay,read_essay_sources
    run=load_essay(engine,settings,sid,rid)
    if run['status'] not in {'failed','needs_review'} or run['metadata'].get('workflow')!='evidence_first_v1':raise EssayError('essay_not_editable')
    sections=[dict(s) for s in run['sections']];meta=dict(run['metadata']);history=list(meta.get('advice_edits',[]));plan=meta['fact_sections']
    for key,value in changes.items():
        if not key.isdigit():raise EssayError('invalid_advice_edit',422)
        i=int(key)-1
        if not 0<=i<len(sections) or not value.strip() or len(value)>4000 or re.search(r'[\[\]<>`#*]|https?://',value):raise EssayError('invalid_advice_edit',422)
        history.append({'section':i+1,'before':sections[i]['advice'],'after':value,'editor':'explicit API editorial update; not raw model output'})
        sections[i].update(advice=value,body=render_body(plan[i],value,i))
    sources={s['source_label']:{'original_text':s['original_text']} for s in read_essay_sources(engine,settings,sid,rid)}
    v=validate_essay(run['outline']['title'],sections,sources);meta['advice_edits']=history
    save_progress(engine,rid,sections=sections,draft_md=assemble(run['outline']['title'],sections),validation=v,metadata=meta,status='needs_review' if v['passed_deterministic'] else 'failed',error_code=None if v['passed_deterministic'] else 'essay_rubric_failed')
    return load_essay(engine,settings,sid,rid)


def source_fact(source,label,start,end):
    if not 0<=start<end<=len(source['original_text']):raise EssayError('invalid_evidence_span',422)
    quote=source['original_text'][start:end]
    if not quote.strip() or len(quote)>4500 or re.search(r'[<>\[\]]|https?://',quote):raise EssayError('invalid_evidence_span',422)
    return {'text':quote,'source_id':label,'chunk_id':str(source['chunk_id']),'start':start,'end':end,'sha256':sha256(quote.encode()).hexdigest()}


def edit_evidence(engine,settings,sid,rid,changes):
    from backend.app.essays import load_essay,read_essay_sources
    run=load_essay(engine,settings,sid,rid)
    if run['status'] not in {'failed','needs_review'} or run['metadata'].get('workflow')!='evidence_first_v1':raise EssayError('essay_not_editable')
    sections=[dict(s) for s in run['sections']];meta=dict(run['metadata']);plan=meta['fact_sections'];sources={s['source_label']:s for s in read_essay_sources(engine,settings,sid,rid)};history=list(meta.get('evidence_edits',[]))
    for key,spans in changes.items():
        if not key.isdigit() or not 1<=int(key)<=len(sections) or not 1<=len(spans)<=8:raise EssayError('invalid_evidence_edit',422)
        i=int(key)-1;label=plan[i]['source_ids'][0];new=[source_fact(sources[label],label,s['start'],s['end']) for s in spans]
        history.append({'section':i+1,'before':plan[i]['facts'],'after':new,'editor':'explicit source-span selection; not model-generated or arbitrary factual text'})
        plan[i]['facts']=new;sections[i]['body']=render_body(plan[i],sections[i]['advice'],i)
    meta['evidence_edits']=history;meta['fact_sections']=plan;validation=validate_essay(run['outline']['title'],sections,{l:{'original_text':s['original_text']} for l,s in sources.items()})
    save_progress(engine,rid,sections=sections,draft_md=assemble(run['outline']['title'],sections),validation=validation,metadata=meta,status='needs_review' if validation['passed_deterministic'] else 'failed',error_code=None if validation['passed_deterministic'] else 'essay_rubric_failed')
    return load_essay(engine,settings,sid,rid)
