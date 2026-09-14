(function(){
 'use strict';
 const cache=new Map(),NOTE_KEY='wvs_net_system_notes_v1';
 const make=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
 const button=(text,fn)=>{const b=make('button','ns-btn ns-btn-secondary',text);b.type='button';b.addEventListener('click',fn);return b;};
 function loadCase(id){
  if(!/^(firewall|dns|authentication|integrity|windows|backup)$/.test(id))return Promise.reject(new Error('Unknown case'));
  if(cache.has(id))return cache.get(id);
  const promise=new Promise((resolve,reject)=>{
   const script=document.createElement('script');
   script.src=new URL('./data/evidence/'+id+'.js',document.baseURI).href;
   script.onload=()=>{const payload=window.NETWORK_SYSTEM_EVIDENCE&&window.NETWORK_SYSTEM_EVIDENCE[id];if(!payload||!Array.isArray(payload.records)){cache.delete(id);reject(new Error('Invalid evidence'));return;}resolve(payload);};
   script.onerror=()=>{cache.delete(id);script.remove();reject(new Error('Evidence loading failed'));};
   document.head.append(script);
  });
  cache.set(id,promise);return promise;
 }
 function exportCsv(spec,records){
  const columns=Object.keys(records[0]||{});
  const cell=value=>{let text=value==null?'':String(value);if(/^[=+@-]/.test(text))text="'"+text;return '"'+text.replace(/"/g,'""')+'"';};
  const csv='\uFEFF'+[columns.map(cell).join(','),...records.map(r=>columns.map(k=>cell(r[k])).join(','))].join('\r\n');
  const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
  const a=document.createElement('a');a.href=url;a.download='synthetic-'+spec.id+'.csv';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),30000);
 }
 function tableView(parent,spec,payload){
  const rows=payload.records;
  const search=make('input');search.type='search';search.placeholder='값 검색 또는 필드=값 (예: user=ops-review)';search.setAttribute('aria-label','사건 로그 검색');
  const toolbar=make('div','ns-case-toolbar');
  const count=make('p','ns-case-count');count.setAttribute('role','status');
  const download=button('전체 로그 CSV 내려받기',()=>exportCsv(spec,rows));
  toolbar.append(search,download);
  const wrap=make('div','ns-case-table-wrap');wrap.tabIndex=0;wrap.setAttribute('aria-label','모의 사건 로그 표');
  const table=make('table','ns-case-table'),head=make('thead'),hr=make('tr'),body=make('tbody');
  spec.columns.forEach(key=>{const th=make('th','',key);th.scope='col';hr.append(th);});head.append(hr);table.append(head,body);wrap.append(table);
  let filtered=rows,page=0,timer;
  const prev=button('이전 기록',()=>{page--;draw();}),next=button('다음 기록',()=>{page++;draw();});
  const pages=make('div','ns-case-toolbar');pages.append(prev,next);
  const draw=()=>{body.replaceChildren();const start=page*50;filtered.slice(start,start+50).forEach(r=>{const tr=make('tr');spec.columns.forEach(key=>{const td=make('td','',r[key]==null?'—':String(r[key]));tr.append(td);});body.append(tr);});count.textContent=filtered.length?'검색 결과 '+filtered.length.toLocaleString()+'건 · '+(start+1)+'–'+Math.min(start+50,filtered.length)+'번째 기록':'일치하는 기록이 없습니다.';prev.disabled=page===0;next.disabled=start+50>=filtered.length;};
  search.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(()=>{const q=search.value.trim().toLowerCase(),m=q.match(/^([a-z_]+)=(.*)$/);filtered=!q?rows:rows.filter(r=>m?String(r[m[1]]??'').toLowerCase().includes(m[2].trim()):Object.values(r).some(v=>String(v??'').toLowerCase().includes(q)));page=0;draw();},160);});
  parent.append(toolbar,count,wrap,pages);draw();
 }
 function render(lesson,parent){
  const book=window.NETWORK_SYSTEM_CASEBOOK;
  const spec=book&&book.cases.find(c=>c.id===lesson.caseId);
  if(!spec)return;
  const panel=make('details','ns-case-panel');
  panel.append(make('summary','','사건 분석 · '+spec.title));
  const body=make('div','ns-case-body');
  body.append(make('p','ns-case-label','모의 증거로 판단 연습'),make('p','',spec.intro),make('p','ns-case-disclaimer','아래 기록은 가상 자산으로 만든 교육 자료입니다. 실제 수집 로그·EVTX·명령 실행 결과가 아니며, 시각은 UTC입니다. 이 패널과 관찰 노트는 점수를 바꾸지 않습니다.'));
  const tasks=make('ol','ns-case-questions');spec.questions.forEach(q=>tasks.append(make('li','',q)));body.append(tasks);
  const config=make('details','ns-case-hint');config.append(make('summary','','상황에 주어진 설정·운영 조건'),make('pre','',spec.config));body.append(config);
  spec.hints.forEach((hint,i)=>{const item=make('details','ns-case-hint');item.append(make('summary','','힌트 '+(i+1)),make('p','',hint));body.append(item);});
  const answer=make('details','ns-case-hint');answer.append(make('summary','','분석 해설'),make('p','',spec.answer));body.append(answer);
  const logArea=make('section','ns-case-log'),status=make('p','ns-case-count');
  const open=button('모의 로그 열기',async()=>{open.disabled=true;status.textContent='사건 기록을 불러오고 있습니다.';try{const payload=await loadCase(spec.id);logArea.replaceChildren();tableView(logArea,spec,payload);open.hidden=true;status.textContent='';}catch(_){status.textContent='자료를 불러오지 못했습니다. public/data/evidence 폴더를 함께 적용했는지 확인해 주세요.';open.disabled=false;}});
  body.append(open,status,logArea);
  const noteLabel=make('label','ns-case-note-label','관찰 노트');
  const note=make('textarea');note.rows=5;note.placeholder='확인한 사실 / 추가 확인할 가설 / 조치와 검증 계획';note.setAttribute('aria-label','사건 관찰 노트');
  const noteState=make('p','ns-case-count');let saved={};
  try{const stored=JSON.parse(localStorage.getItem(NOTE_KEY)||'{}');if(stored&&typeof stored==='object'&&!Array.isArray(stored))saved=stored;note.value=typeof saved[lesson.id]==='string'?saved[lesson.id]:'';}catch(_){noteState.textContent='이 브라우저에서는 저장한 노트를 불러올 수 없습니다.';}
  note.addEventListener('input',()=>{try{const latest=JSON.parse(localStorage.getItem(NOTE_KEY)||'{}');const notes=latest&&typeof latest==='object'&&!Array.isArray(latest)?latest:{};notes[lesson.id]=note.value;localStorage.setItem(NOTE_KEY,JSON.stringify(notes));noteState.textContent='이 브라우저에 저장됨';}catch(_){noteState.textContent='저장하지 못했습니다. 현재 입력은 유지되지만 창을 닫으면 사라질 수 있습니다.';}});
  noteLabel.append(note);body.append(noteLabel,noteState);
  const glossary=make('details','ns-case-hint');glossary.append(make('summary','','분석 용어 사전'));
  const defs=make('dl');book.glossary.forEach(([term,meaning])=>{defs.append(make('dt','',term),make('dd','',meaning));});glossary.append(defs);body.append(glossary);
  panel.append(body);parent.append(panel);
 }
 window.SecurityCasebook={render};
})();
