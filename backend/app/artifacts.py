"""Owned immutable artifacts, server-derived formatting and layered isolation."""
from backend.app.observability import emit
import time
from html import escape
import re,json
from uuid import UUID,uuid4
from typing import Literal
import nh3
from markdown_it import MarkdownIt
from pydantic import Field
from sqlalchemy import text
from backend.app.schemas import Input
from backend.app.writing import EssayError

CSP="default-src 'none'; script-src 'none'; style-src 'unsafe-inline'; img-src 'none'; font-src 'none'; connect-src 'none'; media-src 'none'; object-src 'none'; frame-src 'none'; base-uri 'none'; form-action 'none'"
STYLE='body{font:17px/1.75 Georgia,serif;max-width:48em;margin:0 auto;padding:30px;color:#26382f;background:#fffdf8;overflow-wrap:anywhere}h1,h2,h3{line-height:1.3}blockquote{border-left:3px solid #6b8877;padding-left:1em;margin-left:0}li{margin:.6em 0}strong{font-weight:700}'
TAGS={'p','h1','h2','h3','h4','h5','h6','ul','ol','li','strong','em','blockquote','pre','code','br','hr','div','section','article','span','table','thead','tbody','tr','th','td'}
CLEANER=nh3.Cleaner(tags=TAGS,clean_content_tags={'script','style','title','iframe','object','embed','svg','math','form','template'},attributes={'*':{'style'}},filter_style_properties={'color','background-color','font-size','font-family','font-weight','font-style','line-height','text-align','margin','padding','border','border-radius','max-width'},url_schemes=set(),url_relative='deny',link_rel=None)
MD=MarkdownIt('commonmark',{'html':False,'linkify':False})


def document(body,title='Saved document'):
    safe=CLEANER.clean(body)
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="'+escape(CSP,quote=True)+'"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+escape(title)+'</title><style>'+STYLE+'</style></head><body>'+safe+'</body></html>'


def _preview(content,kind,title):
    if len(content)>100_000:raise EssayError('artifact_too_large',422)
    return document(MD.render(content) if kind=='markdown' else content,title)


class ArtifactCreate(Input):
    message_id: UUID
    format: Literal['markdown','html']


def owned(engine,settings,sid):
    with engine.connect() as c:
        if not c.scalar(text('SELECT id FROM sessions WHERE id=:id AND user_id=:user'),{'id':sid,'user':settings.local_user_id}):raise EssayError('session_not_found',404)


def artifact_out(row):
    v=dict(row);v['preview_html']=preview(v['content'],v['type'],v['title']);return v


def list_artifacts(engine,settings,sid):
    owned(engine,settings,sid)
    with engine.connect() as c:
        rows=c.execute(text('SELECT * FROM artifacts WHERE session_id=:sid ORDER BY created_at DESC,id DESC'),{'sid':sid}).mappings()
        return [artifact_out(r) for r in rows]


def get_artifact(engine,settings,sid,aid):
    owned(engine,settings,sid)
    with engine.connect() as c:r=c.execute(text('SELECT * FROM artifacts WHERE id=:id AND session_id=:sid'),{'id':aid,'sid':sid}).mappings().first()
    if not r:raise EssayError('artifact_not_found',404)
    return artifact_out(r)


def create_artifact(engine,settings,sid,body):
    owned(engine,settings,sid)
    with engine.begin() as c:
        m=c.execute(text("SELECT * FROM messages WHERE id=:id AND session_id=:sid AND role='assistant' AND status='completed' FOR UPDATE"),{'id':body.message_id,'sid':sid}).mappings().first()
        if not m:raise EssayError('artifact_source_not_found',404)
        existing=c.execute(text('SELECT * FROM artifacts WHERE session_id=:sid AND message_id=:mid AND type=:kind'),{'sid':sid,'mid':m['id'],'kind':body.format}).mappings().first()
        if existing:return artifact_out(existing)
        sources=list(c.execute(text('SELECT source_label,chunk_id,source_metadata FROM answer_sources WHERE message_id=:id ORDER BY source_label'),{'id':m['id']}).mappings())
        labels=set(re.findall(r'\[(S\d+)\]',m['content']))
        if labels-set(s['source_label'] for s in sources):raise EssayError('artifact_citation_unknown')
        run=c.execute(text('SELECT id,metadata,status FROM essay_runs WHERE assistant_message_id=:id'),{'id':m['id']}).mappings().first()
        provenance=('live_endpoint' if run['metadata'].get('workflow')=='evidence_first_v1' else 'reviewed_fixture') if run else 'saved_reply'
        title=(m['content'].splitlines()[0].lstrip('# ').strip() or 'Saved research')[:160]
        content=m['content'] if body.format=='markdown' else document(MD.render(m['content']),title)
        metadata={'provenance':provenance,'generation_run_id':str(run['id']) if run else None,'manual_edits':len(run['metadata'].get('advice_edits',[]))+len(run['metadata'].get('evidence_edits',[])) if run else 0,'formatting':'server conversion of owned accepted message; no new model call','sources':[dict(s) for s in sources],'citation_ids':sorted(labels),'policy':'static formatting only; scripts, forms, navigation and external resources disabled'}
        row=c.execute(text('INSERT INTO artifacts(id,session_id,message_id,type,title,content,source_metadata) VALUES(:id,:sid,:mid,:kind,:title,:content,CAST(:meta AS jsonb)) RETURNING *'),{'id':uuid4(),'sid':sid,'mid':m['id'],'kind':body.format,'title':title,'content':content,'meta':json.dumps(metadata,default=str)}).mappings().one()
        return artifact_out(row)


def artifact_source(engine,settings,sid,aid,label):
    a=get_artifact(engine,settings,sid,aid)
    if label not in a['source_metadata']['citation_ids']:raise EssayError('source_not_found',404)
    with engine.connect() as c:r=c.execute(text('SELECT * FROM answer_sources WHERE message_id=:mid AND source_label=:label'),{'mid':a['message_id'],'label':label}).mappings().first()
    if not r:raise EssayError('source_not_found',404)
    from backend.app.conversation import source_links
    links=source_links(r['source_metadata'])
    return {'source_label':label,'chunk_id':r['chunk_id'],'original_text':r['evidence_text'],'metadata':r['source_metadata'],'quote_spans':r['quote_spans'],'source_url':links[0],'video_url':links[1]}


def preview(content,kind,title):
    started=time.monotonic()
    try:
        result=_preview(content,kind,title)
        emit('render_operation',stage='rendering',code='ok',duration_ms=round((time.monotonic()-started)*1000,2))
        return result
    except Exception as exc:
        emit('render_operation',stage='rendering',code=getattr(exc,'code','artifact_render_failed'),error_type=type(exc).__name__,duration_ms=round((time.monotonic()-started)*1000,2))
        raise
