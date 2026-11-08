"""Immutable factual blocks; model text is advice, never citation authority.

Syntactic rejection is only a first screen. Manual review must reject unsupported
claims hidden in advice before any draft is accepted. No repair or text deletion.
"""
import re
from backend.app.writing import EssayError


def validate_facts(facts, sources):
    if not facts or len({f['id'] for f in facts}) != len(facts):
        raise EssayError('approved_facts_invalid')
    for f in facts:
        s=sources.get(f['source_id'])
        if not re.fullmatch(r'F\d+',f['id']) or not s or f['chunk_id']!=str(s['chunk_id']):
            raise EssayError('approved_fact_source_mismatch')
        if not f['statement'].strip() or re.search(r'[\[\]<>\n]',f['statement']):
            raise EssayError('approved_fact_text_invalid')
        if not f['evidence_anchor'] or f['evidence_anchor'] not in s['original_text']:
            raise EssayError('approved_fact_anchor_mismatch')


def render_approved(raw, facts):
    """Render standalone fact tokens atomically as statement + its fixed citation.

    Free blocks must be labelled advice. Never repair a changed token, accept
    model-authored citations, or silently drop extra output. These are Markdown
    source blocks only; HTML/browser artifact rendering remains outside Phase6.
    """
    if not isinstance(raw,str) or not raw.strip() or len(raw)>8000:
        raise EssayError('approved_draft_invalid')
    blocks=re.split(r'\n\s*\n',raw.strip()); seen=[];out=[];advice=[];placements=[]
    by_id={f['id']:f for f in facts}
    for block in blocks:
        m=re.fullmatch(r'\[\[(F\d+)\]\]',block)
        if m:
            key=m[1]
            if key not in by_id or key in seen:raise EssayError('approved_fact_token_invalid')
            f=by_id[key];seen.append(key)
            text=f['statement']+' ['+f['source_id']+']'
            placements.append({'block':len(out)+1,'fact_id':key,'source_id':f['source_id'],'chunk_id':f['chunk_id'],'rendered_text':text})
            out.append(text);continue
        clean=re.sub(r'^-\s+','',block)
        if not clean.startswith('Application: '):raise EssayError('unapproved_factual_block')
        if re.search(r'[\[\]<>`]|https?://|^\s*#|\b(?:Purpose|Target):',block,re.M|re.I):
            raise EssayError('advice_markup_or_instruction_invalid')
        # Reject obvious factual additions/guarantees even under an advice label.
        if re.search(r'\b(?:Lookout|Ellis|Xobni|proved|proven|guarantee\w*|ensur\w*|increas\w*|improv\w*|research shows|studies show|will lead|resulted|was|were|has been)\b|\d|%',clean,re.I):
            raise EssayError('new_factual_claim_in_advice')
        advice.append(clean);out.append(block)
    if seen!=[f['id'] for f in facts]:raise EssayError('approved_fact_missing_or_reordered')
    if not advice:raise EssayError('approved_advice_missing')
    return {'markdown':'\n\n'.join(out),'placements':placements,'advice':advice,
            'manual_review_required':True,'limits':'Exact fact/citation preservation and conservative syntax checks do not prove advice contains no implied factual claims.'}


def validate_application(raw):
    """A bounded plain paragraph; semantic advice review remains mandatory."""
    from backend.app.writing import word_count
    if not isinstance(raw,str) or not 20<=word_count(raw)<=65:
        raise EssayError('application_length_invalid')
    if '\n' in raw.strip() or re.search(r'[\[\]<>`#*]|https?://|\b(?:Application|Purpose|Target):',raw,re.I):
        raise EssayError('application_format_invalid')
    if not re.match(r'^(?:Try|Ask|Choose|Write|Compare|Consider|Review|Select|List|Sketch|Take|Start|Invite|Read|Pick|Map|Note|Record)\b',raw):
        raise EssayError('application_not_action_advice')
    if re.search(r'\b(?:Lookout|Ellis|Xobni|historically|proved|proven|guarantee\w*|ensur\w*|will|always|every product|was|were|has been)\b|\d|%',raw,re.I):
        raise EssayError('application_factual_or_outcome_claim')
    return raw.strip()


def assemble_server_section(heading,facts,raw_advice,validator=validate_application):
    """The model never supplies factual text, order, labels, or citation IDs."""
    if not re.fullmatch(r'[A-Za-z][A-Za-z ,:–-]{2,100}',heading):raise EssayError('approved_heading_invalid')
    advice=validator(raw_advice)
    blocks=[f['statement']+' ['+f['source_id']+']' for f in facts]
    placements=[{'fact_id':f['id'],'source_id':f['source_id'],'chunk_id':f['chunk_id'],'text':b} for f,b in zip(facts,blocks)]
    body='\n\n'.join(blocks+['Application: '+advice])
    return {'markdown':'## '+heading+'\n\n'+body,'body':body,'placements':placements,'advice':advice,'manual_review_required':True}


def validate_experiment(raw):
    """Syntax only: manual review must check hypothesis scope and factual support."""
    from backend.app.writing import word_count
    if not isinstance(raw,str) or not 65<=word_count(raw)<=75:
        raise EssayError('experiment_length_invalid')
    if '\n' in raw.strip() or re.search(r'[\[\]<>`#*]|https?://|\b(?:Application|Purpose|Target):',raw,re.I):
        raise EssayError('experiment_format_invalid')
    if re.search(r'\b(?:Lookout|Ellis|Xobni|historically|proved|proven|guarantee\w*|ensur\w*|always|was|were|has been)\b',raw,re.I):
        raise EssayError('experiment_history_or_guarantee')
    for pattern,code in [(r'\b(?:try|test|compare|experiment)\b','action'),(r'\b(?:track|measure|record)\b','measurement'),(r'\b(?:rate|percentage|proportion|fraction|time|count)\b','metric'),(r'\b(?:keep|revise|retain|revert|adopt|discard)\b','decision'),(r'\b(?:hypothesis|test whether|test the idea)\b','hypothesis')]:
        if not re.search(pattern,raw,re.I):raise EssayError('experiment_missing_'+code)
    return raw.strip()
