(() => {
  'use strict';
  const STATE_KEY = 'wvs_net_system_v1';
  const DATA_URL = new URL('./data/network-system-security.json', document.baseURI);
  const $ = id => document.getElementById(id);
  const dom = {list:$('ns-lesson-list'),lessons:$('ns-lessons'),search:$('ns-search-input'),filters:$('ns-track-filters'),notice:$('ns-notice')};
  let data, activeId = '', activeTrack = 'all', search = '';
  let state = {version:'1.0.0',attempts:0,lessons:{}};
  const clone = value => JSON.parse(JSON.stringify(value));
  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function notify(message) {dom.notice.textContent = message;dom.notice.hidden = false;}
  function loadState() {
    try {
      const saved = JSON.parse(localStorage.getItem(STATE_KEY));
      if (saved && saved.version === state.version && saved.lessons && typeof saved.lessons === 'object' && !Array.isArray(saved.lessons)) state = saved;
    } catch (_) {notify('이 브라우저에서는 진도를 불러올 수 없습니다. 실습은 계속할 수 있습니다.');}
  }
  function saveState() {
    state.updatedAt = new Date().toISOString();
    try {localStorage.setItem(STATE_KEY, JSON.stringify(state));}
    catch (_) {notify('진도를 저장하지 못했습니다. 현재 실습은 가능하지만 창을 닫으면 기록이 남지 않을 수 있습니다.');}
  }
  function lessonState(lesson) {
    const saved = state.lessons[lesson.id];
    if (!saved || typeof saved !== 'object') state.lessons[lesson.id] = {};
    const current = state.lessons[lesson.id];
    if (!current.selected || typeof current.selected !== 'object') current.selected = {};
    current.selected = Object.assign(clone(lesson.defaultConfig), current.selected);
    current.attempts = Number.isFinite(current.attempts) ? current.attempts : 0;
    current.bestScore = Number.isFinite(current.bestScore) ? current.bestScore : 0;
    current.quizSelection = Number.isInteger(current.quizSelection) ? current.quizSelection : -1;
    // Re-evaluate answers saved by the previous evaluator without adding an attempt.
    if (current.lastResult && current.evaluatorVersion !== 2) {
      current.lastResult = SecurityLabEvaluator.evaluate(lesson, current.selected, current.quizSelection);
      current.mastered = current.lastResult.mastered;
      current.bestScore = Math.min(current.bestScore, current.lastResult.maxScore);
      current.evaluatorVersion = 2;
    }
    return current;
  }
  function labelForTrack(id) {return data.module.tracks.find(track => track.id === id)?.label || id;}
  function passed(current) {return !!current.mastered && !current.dirty;}
  function statusLabel(current) {return current.dirty ? '재점검 필요' : passed(current) ? '통과 완료' : current.attempts ? '복습 중' : '시작 전';}
  function filtered() {
    return data.lessons.filter(lesson => (activeTrack === 'all' || lesson.track === activeTrack) && [lesson.title,lesson.code,lesson.scenario,lesson.goal,labelForTrack(lesson.track),...(lesson.tags || [])].join(' ').toLowerCase().includes(search));
  }
  function renderSummary() {
    const progress = data.lessons.map(lessonState);
    const done = progress.filter(passed).length;
    $('ns-total-lessons').textContent = data.lessons.length;
    $('ns-mastered-count').textContent = done;
    $('ns-best-score').textContent = progress.reduce((sum,item) => sum + item.bestScore, 0);
    $('ns-total-attempts').textContent = progress.reduce((sum,item) => sum + item.attempts, 0);
    $('ns-progress').max = data.lessons.length;
    $('ns-progress').value = done;
    $('ns-progress-text').textContent = Math.round(done / data.lessons.length * 100) + '%';
  }
  function renderFilters() {
    dom.filters.replaceChildren();
    const tracks = [{id:'all',label:'전체'},...data.module.tracks.map(track => ({id:track.id,label:{network:'네트워크',linux:'Linux',windows:'Windows'}[track.id] || track.label}))];
    tracks.forEach(track => {
      const button = el('button','ns-chip',track.label);
      button.type = 'button';
      button.setAttribute('aria-pressed',String(activeTrack === track.id));
      button.addEventListener('click',() => {activeTrack = track.id;renderFilters();renderLibrary(true);});
      dom.filters.append(button);
    });
  }
  function renderLibrary(chooseVisible = false) {
    const lessons = filtered();
    const oldId = activeId;
    if (chooseVisible && !lessons.some(lesson => lesson.id === activeId)) activeId = lessons[0]?.id || '';
    dom.list.replaceChildren();
    $('ns-library-count').textContent = lessons.length + '개 실습';
    lessons.forEach(lesson => {
      const current = lessonState(lesson);
      const button = el('button','ns-lesson-link');
      button.type = 'button';button.dataset.lesson = lesson.id;
      button.setAttribute('aria-current',String(lesson.id === activeId));
      const info = el('span','ns-lesson-info');
      info.append(el('strong','',lesson.title),el('small','',lesson.durationMin + '분 · ' + statusLabel(current)));
      button.append(el('span','ns-lesson-code',lesson.code),info);
      button.addEventListener('click',() => selectLesson(lesson.id));
      dom.list.append(button);
    });
    if (!lessons.length) dom.list.append(el('p','ns-empty','일치하는 실습이 없습니다.'));
    if (oldId !== activeId || !activeId) renderActive();
  }
  function selectLesson(id, updateHash = true) {
    if (!data.lessons.some(lesson => lesson.id === id)) return;
    activeId = id;
    if (updateHash) {try {history.replaceState(null,'','#' + id);} catch (_) { /* Some file previews restrict history. */ }}
    renderLibrary();renderActive();
  }
  function sectionTitle(number,text) {const title = el('h3','ns-section-title');title.append(el('span','ns-step',number),document.createTextNode(text));return title;}
  function controlField(lesson,control,current) {
    const field = el('fieldset','ns-control');
    field.append(el('legend','',control.label));
    if (control.description || control.hint) field.append(el('p','ns-control-description',control.description || control.hint));
    const name = lesson.id + '-' + control.id;
    const selected = current.selected[control.id];
    if (control.type === 'single' || control.type === 'multi') {
      const options = el('div','ns-options');
      control.options.forEach(option => {
        const label = el('label','ns-option');
        const input = document.createElement('input');
        input.type = control.type === 'multi' ? 'checkbox' : 'radio';
        input.name = name;input.value = String(option.value);
        input.checked = control.type === 'multi' ? (Array.isArray(selected) ? selected : []).map(String).includes(input.value) : String(selected) === input.value;
        label.append(input,el('span','',option.label));options.append(label);
      });
      field.append(options);
    } else {
      const input = document.createElement('input');
      input.name = name;input.type = control.type === 'number' ? 'number' : 'text';
      input.setAttribute('aria-label',control.label);
      input.value = selected == null ? '' : selected;input.placeholder = control.placeholder || '';
      if (control.min != null) input.min = control.min;
      if (control.max != null) input.max = control.max;
      field.append(input);
    }
    return field;
  }
  function readForm(lesson,form) {
    const values = new FormData(form);
    const answers = {};
    lesson.controls.forEach(control => {
      const key = lesson.id + '-' + control.id, value = values.get(key);
      answers[control.id] = control.type === 'multi' ? values.getAll(key) : control.type === 'number' ? value == null || value === '' ? null : Number(value) : value == null ? '' : String(value).trim();
    });
    const quiz = values.get('quiz-' + lesson.id);
    return {answers,quiz:quiz == null ? -1 : Number(quiz)};
  }
  function configurationText(lesson,current) {
    return lesson.controls.map(control => {
      const value = current.selected[control.id];
      return control.id + ' = ' + (Array.isArray(value) ? value.length ? value.join(', ') : '(없음)' : value == null || value === '' ? '(미설정)' : String(value));
    }).join('\n');
  }
  function renderResult(lesson,current,area) {
    area.replaceChildren();area.removeAttribute('data-state');
    if (!current.lastResult || current.dirty) {
      area.append(el('strong','',current.dirty ? '설정이 변경되었습니다. 다시 점검해 주세요.' : '설정을 구성한 뒤 보안 점검을 실행해 보세요.'),el('p','', '필수 설정 점검 + 개념 퀴즈 정답으로 실습을 완료합니다.'));
      return;
    }
    const result = current.lastResult;
    area.dataset.state = result.mastered ? 'pass' : 'fail';
    const head = el('div','ns-result-head');
    const score = el('span','ns-result-score',String(result.totalScore));score.append(el('small','',' / ' + result.maxScore));
    head.append(el('strong','',result.mastered ? '실습 통과! 안전한 설정을 완성했습니다.' : '다시 확인할 설정이 있습니다.'),score);
    const checks = el('div','ns-checks');
    result.checkResults.forEach(check => {
      const row = el('div','ns-check');row.dataset.pass = String(check.pass);
      const description = el('div','',check.label);
      description.append(el('small','',(check.required ? '필수' : '추가 점검') + ' · ' + (check.pass ? check.points : 0) + ' / ' + check.points + '점'));
      row.append(el('span','ns-check-mark',check.pass ? '통과' : '미달'),description);checks.append(row);
    });
    const explanation = el('div','ns-explanation');
    explanation.append(el('strong','',result.quizCorrect ? '퀴즈 정답 · +20점' : '퀴즈 ' + (current.quizSelection < 0 ? '미응답' : '오답')),el('p','',lesson.quiz.explanation));
    area.append(head,checks,explanation);
  }
  function renderActive() {
    dom.lessons.replaceChildren();
    const lesson = data.lessons.find(item => item.id === activeId);
    if (!lesson) {
      const empty = el('div','ns-empty','검색 결과가 없습니다. 검색어나 트랙을 바꿔보세요.');
      const clear = el('button','ns-btn ns-btn-secondary','전체 실습 보기');clear.type = 'button';
      clear.addEventListener('click',() => {search = '';dom.search.value = '';activeTrack = 'all';renderFilters();renderLibrary(true);});
      empty.append(document.createElement('br'),clear);dom.lessons.append(empty);return;
    }
    const current = lessonState(lesson);
    const card = el('article','ns-lesson-card');card.id = lesson.id;
    const head = el('header','ns-lesson-head');
    const meta = el('div','ns-lesson-meta');
    meta.append(el('span','ns-lesson-kicker',lesson.code + ' / ' + labelForTrack(lesson.track)),el('span','', 'CONFIGURATION LAB'));
    const badges = el('div','ns-lesson-badges');
    const status = el('span','ns-badge',statusLabel(current));status.dataset.status = passed(current) ? 'pass' : 'pending';
    badges.append(el('span','ns-badge',lesson.difficulty === 'beginner' ? '입문' : '중급'),el('span','ns-badge',lesson.durationMin + '분'),el('span','ns-badge',lesson.controls.length + '개 설정'),status);
    head.append(meta,el('h2','ns-lesson-title',lesson.title),badges);
    const body = el('div','ns-lesson-body'), brief = el('div','ns-brief');
    [['01','현재 상황',lesson.scenario],['02','해결 목표',lesson.goal]].forEach(([number,title,text]) => {const section = el('section');section.append(sectionTitle(number,title),el('p','',text));brief.append(section);});
    const form = document.createElement('form');form.noValidate = true;
    const controls = el('div','ns-controls-grid');
    lesson.controls.forEach(control => controls.append(controlField(lesson,control,current)));
    const preview = el('details','ns-config-preview'), previewText = el('pre','',configurationText(lesson,current));
    preview.append(el('summary','','현재 정책 미리보기'),previewText);
    const quiz = el('section','ns-quiz');quiz.append(sectionTitle('04','개념 확인'),el('p','',lesson.quiz.question));
    const quizOptions = el('div','ns-options');
    lesson.quiz.options.forEach((option,index) => {
      const label = el('label','ns-option'), radio = document.createElement('input');
      radio.type = 'radio';radio.name = 'quiz-' + lesson.id;radio.value = String(index);radio.checked = current.quizSelection === index;
      label.append(radio,el('span','',option));quizOptions.append(label);
    });
    quiz.append(quizOptions);
    const actions = el('div','ns-actions'), submit = el('button','ns-btn','보안 점검 실행'), reset = el('button','ns-btn ns-btn-secondary','설정 다시 시작');
    submit.type = 'submit';reset.type = 'button';actions.append(submit,reset);
    const result = el('section','ns-result');result.dataset.result = lesson.id;result.setAttribute('tabindex','-1');result.setAttribute('aria-label','채점 결과');
    form.append(sectionTitle('03','보안 설정 구성'),controls,preview,quiz,actions);
    const resources = el('div','ns-resources');
    (lesson.related || []).forEach(item => {
      const link = el('a','',item.title);
      const moduleLink = /^(?:network-system-security\.html)?#ns-[a-z][0-9]+$/.test(item.url);
      link.href = moduleLink ? '#' + item.url.split('#')[1] : new URL(item.url,location.protocol === 'file:' || ['localhost','127.0.0.1'].includes(location.hostname) ? 'https://vuln-sim.web.app/' : document.baseURI).href;resources.append(link);
    });
    (lesson.references || []).forEach(item => {
      if (!/^https?:\/\//i.test(item.url)) return;
      const link = el('a','',item.label);link.href = item.url;link.target = '_blank';link.rel = 'noopener noreferrer';resources.append(link);
    });
    body.append(brief);
    if (window.SecurityCasebook) window.SecurityCasebook.render(lesson,body);
    body.append(form,result);
    if (lesson.evidence) body.append(el('p','ns-evidence',lesson.evidence));
    body.append(resources);card.append(head,body);dom.lessons.append(card);renderResult(lesson,current,result);
    const updateStatus = () => {status.textContent = statusLabel(current);status.dataset.status = passed(current) ? 'pass' : 'pending';renderSummary();renderLibrary();};
    form.addEventListener('input',() => {
      const values = readForm(lesson,form);current.selected = values.answers;current.quizSelection = values.quiz;
      current.dirty = true;previewText.textContent = configurationText(lesson,current);saveState();renderResult(lesson,current,result);updateStatus();
    });
    form.addEventListener('submit',event => {
      event.preventDefault();const values = readForm(lesson,form);current.selected = values.answers;current.quizSelection = values.quiz;
      const computed = SecurityLabEvaluator.evaluate(lesson,values.answers,values.quiz);
      current.lastResult = computed;current.mastered = computed.mastered;current.dirty = false;
      current.lastScore = computed.totalScore;current.bestScore = Math.max(current.bestScore,computed.totalScore);current.attempts += 1;
      current.lastAt = computed.attemptsAt;current.evaluatorVersion = 2;
      state.attempts = data.lessons.reduce((sum,item) => sum + lessonState(item).attempts,0);
      saveState();renderResult(lesson,current,result);updateStatus();result.focus({preventScroll:true});
      result.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth',block:'nearest'});
    });
    reset.addEventListener('click',() => {
      current.selected = clone(lesson.defaultConfig);current.quizSelection = -1;current.mastered = false;current.dirty = false;current.lastResult = null;current.lastScore = 0;
      saveState();renderActive();renderLibrary();renderSummary();
    });
  }
  function validData(value) {return value && Array.isArray(value.module?.tracks) && Array.isArray(value.lessons) && value.lessons.length > 0 && value.lessons.every(lesson => lesson.id && Array.isArray(lesson.controls) && Array.isArray(lesson.checks) && lesson.quiz);}
  async function bootstrap() {
    try {
      if (location.protocol === 'file:') data = window.NETWORK_SYSTEM_SECURITY_DATA;
      else {
        try {
          const response = await fetch(DATA_URL,{cache:'no-store'});
          if (!response.ok) throw new Error('HTTP ' + response.status);
          data = await response.json();if (!validData(data)) throw new Error('Invalid data');
        } catch (_) {data = window.NETWORK_SYSTEM_SECURITY_DATA;notify('최신 콘텐츠를 불러오지 못해 패치에 포함된 콘텐츠를 표시합니다.');}
      }
      if (!validData(data) || !window.SecurityLabEvaluator) throw new Error('Missing content or evaluator');
      loadState();
      const hash = location.hash.slice(1);
      activeId = data.lessons.some(lesson => lesson.id === hash) ? hash : data.lessons[0].id;
      renderFilters();renderLibrary();renderActive();renderSummary();
      dom.search.addEventListener('input',() => {search = dom.search.value.trim().toLowerCase();renderLibrary(true);});
      window.addEventListener('hashchange',() => {
        const id = location.hash.slice(1);if (!data.lessons.some(lesson => lesson.id === id)) return;
        activeTrack = 'all';search = '';dom.search.value = '';renderFilters();selectLesson(id,false);
      });
    } catch (error) {
      dom.lessons.replaceChildren(el('p','ns-empty','실습을 불러오지 못했습니다. 패치의 public 폴더에 있는 HTML, CSS, JS, data 파일을 함께 적용해 주세요.'));
      notify('실습 콘텐츠 연결을 확인해 주세요.');console.error('Security lab initialization failed',error);
    }
  }
  bootstrap();
})();
