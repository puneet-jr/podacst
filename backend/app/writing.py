"""Typed essay contracts and deterministic checks; these do not certify factual support."""
from backend.app.source_paths import SOURCE_PATH_PATTERN
import json
from pathlib import Path
import re
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from backend.app.schemas import Input

ROOT=Path(__file__).resolve().parents[2]
POLICY=json.loads((ROOT/'agent/skills/ship30/config.json').read_text())
if not (POLICY['min_words']<=POLICY['target_words']<=POLICY['max_words'] and POLICY['sections']==6 and POLICY['max_repairs']==1):
    raise RuntimeError('Unsupported reviewed writing policy')


class EssayError(ValueError):
    def __init__(self,code,status=409):self.code,self.status=code,status;super().__init__(code)


class EssayCreate(Input):
    workflow: Literal['ship30']='ship30'
    topic: str=Field(min_length=8,max_length=350)
    audience: str=Field(min_length=3,max_length=180)
    constraints: str=Field(default='',max_length=1200)
    client_message_id: UUID
    source_path: str | None=Field(default=None,pattern=SOURCE_PATH_PATTERN,max_length=240)
    focus_questions: list[Annotated[str,Field(min_length=3,max_length=220)]]=Field(default_factory=list,max_length=3)
    timeout_seconds: float=Field(default=600,ge=1,le=900)
    use_session_context: bool=True


class OutlineSection(BaseModel):
    model_config=ConfigDict(extra='forbid')
    heading: str=Field(min_length=3,max_length=120)
    purpose: str=Field(min_length=8,max_length=350)
    source_ids: list[str]=Field(min_length=1,max_length=2)


class Outline(BaseModel):
    model_config=ConfigDict(extra='forbid')
    status: Literal['ready','insufficient_evidence']
    title: str=Field(min_length=3,max_length=180)
    sections: list[OutlineSection]=Field(max_length=6)


class SectionDraft(BaseModel):
    model_config=ConfigDict(extra='forbid')
    body: str=Field(min_length=1,max_length=8000)


class EssayReview(Input):
    reviewer: str=Field(min_length=3,max_length=100)
    hook: bool
    progression: bool
    factual_support: bool
    applications_distinct: bool
    complete: bool
    notes: list[str]=Field(min_length=1,max_length=40)


class EssayRunOut(BaseModel):
    id: UUID
    session_id: UUID
    user_message_id: UUID
    assistant_message_id: UUID | None
    status: Literal['running','needs_review','completed','failed','cancelled','insufficient_evidence']
    request: dict
    context_message_ids: list[str]
    outline: dict | None
    sections: list[dict]
    draft_md: str | None
    validation: dict | None
    review: dict | None
    metadata: dict
    error_code: str | None


class EssayEvent(BaseModel):
    type: Literal['started','retrieving','planning','drafting','validating','repairing','needs_review','completed','failed','cancelled','insufficient_evidence']
    run_id: UUID
    workflow: Literal['ship30']='ship30'
    data: dict=Field(default_factory=dict)


def word_count(body):
    # Reference metadata is separate; remove citation markers, Markdown syntax and list ordinals.
    body=re.sub(r'\[S[^\]\n]{0,20}\]|\[[A-Z][A-Za-z0-9]*\]','',body)
    body=re.sub(r'^\s*\d+[.)]\s+','',body,flags=re.M)
    return len(re.findall(r"[^\W_]+(?:['’\-][^\W_]+)*(?:\.\d+)?",body,re.UNICODE))


def parse_outline(raw,labels):
    try:plan=Outline.model_validate_json(raw)
    except ValueError as exc:raise EssayError('essay_outline_invalid',502) from exc
    if plan.status=='insufficient_evidence':
        if plan.sections:raise EssayError('essay_outline_invalid',502)
        return plan
    if len(plan.sections)!=6 or len(set(s.heading.casefold() for s in plan.sections))!=6:raise EssayError('essay_outline_incomplete',502)
    if any(len(set(s.source_ids))!=len(s.source_ids) or not set(s.source_ids)<=set(labels) for s in plan.sections):raise EssayError('essay_outline_source_invalid',502)
    return plan


def assemble(title,sections):
    return '# '+title+'\n\n'+'\n\n'.join('## '+s['heading']+'\n\n'+s['body'] for s in sections)


def parse_markdown_section(raw):
    if not isinstance(raw,str) or not raw.strip() or len(raw)>8000:raise EssayError('section_output_invalid',502)
    value=raw.strip()
    if value.startswith(('{','```')):raise EssayError('section_not_plain_markdown',502)
    return value


def validate_essay(title,sections,sources,policy=POLICY):
    body=assemble(title,sections);errors=[]
    def fail(code,**detail):errors.append({'code':code,**detail})
    count=word_count(body)
    if not policy['min_words']<=count<=policy['max_words']:fail('word_count_outside_range',actual=count,minimum=policy['min_words'],maximum=policy['max_words'])
    if len(sections)!=policy['sections']:fail('incomplete_sections',actual=len(sections),expected=policy['sections'])
    all_citations=[];section_counts=[]
    for i,section in enumerate(sections):
        text=section['body'];section_counts.append(word_count(text))
        if word_count(text)<80:fail('section_too_short',section=i+1,actual=word_count(text))
        if re.search(r'^\s*#{1,6}\s',text,re.M):fail('unexpected_nested_heading_or_reference_block',section=i+1)
        if re.search(r'<\s*/?\s*[A-Za-z][^>]*>|https?://|\]\(',text):fail('unsupported_html_or_external_link',section=i+1)
        if re.search(r'ignore.{0,30}(instructions|system)|reveal.{0,30}(secret|key)',text,re.I):fail('source_instruction_in_draft',section=i+1)
        labels=re.findall(r'\[(S[^\]\n]{0,20}|[A-Z][A-Za-z0-9]*)\]',text);all_citations+=labels
        if any(label not in sources for label in labels):fail('unknown_citation',section=i+1,labels=sorted(set(labels)-set(sources)))
        if set(labels)-set(section.get('source_ids',[])):fail('citation_not_in_section_evidence',section=i+1)
        if not labels:fail('section_missing_citation',section=i+1)
        for block in re.split(r'\n\s*\n',text):
            application=block.strip().startswith('Application:') or bool(block.strip()) and all(re.match(r'^\s*[-*]\s+Application:',line) for line in block.splitlines() if line.strip())
            if not block.strip() or application:continue
            cited=[label for label in re.findall(r'\[(S[^\]\n]{0,20})\]',block) if label in sources]
            if not cited:fail('unattributed_paragraph',section=i+1)
            evidence=' '.join(sources[x]['original_text'] for x in cited if x in sources)
            clean=re.sub(r'\[S\d+\]','',block)
            for number in re.findall(r'\b\d+(?:\.\d+)?\s*%|\$\s*\d+(?:[,.]\d+)*',clean):
                if number.replace(' ','') not in evidence.replace(' ',''):fail('unsupported_numeric_claim',section=i+1,value=number)
            for quote in re.findall(r'“([^”]+)”|"([^"\n]+)"',block):
                value=next(q for q in quote if q)
                if word_count(value)>=5 and ' '.join(value.casefold().split()) not in ' '.join(evidence.casefold().split()):fail('unmatched_direct_quote',section=i+1)
    bullets=len(re.findall(r'^\s*[-*]\s+',body,re.M));bold=re.findall(r'\*\*([^*\n]+)\*\*',body)
    if bullets<3:fail('missing_action_bullets',actual=bullets)
    if not 1<=len(bold)<=8:fail('bold_not_selective',actual=len(bold))
    sentences=[' '.join(s.casefold().split()) for s in re.split(r'(?<=[.!?])\s+',body) if word_count(s)>=8]
    repeats=len(sentences)-len(set(sentences))
    if sentences and repeats/len(sentences)>.15:fail('excessive_repetition',repeated_sentences=repeats)
    return {'passed_deterministic':not errors,'word_count':count,'accepted_range':[policy['min_words'],policy['max_words']],
        'section_word_counts':section_counts,'section_count':len(sections),'bullets':bullets,'bold_spans':len(bold),
        'incomplete_sections':[i+1 for i,s in enumerate(sections) if word_count(s['body'])<80 or s.get('error')]+list(range(len(sections)+1,policy['sections']+1)),
        'citation_ids':sorted(set(all_citations)),'errors':errors,'manual_review_required':True,
        'limits':'ID/count/format screens are not semantic support, hook quality, meaningful progression or completeness proof.'}
