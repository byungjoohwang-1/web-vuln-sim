// public/js/academy-state.js
// Shared state manager for the Security Academy Portal.
// Auto-saves to localStorage, which triggers Firebase Firestore sync via auth-widget.js.

const STATE_KEYS = {
  PROGRESS: 'sda_student_progress',
  WRONG_NOTES: 'sda_wrong_notes',
  CLASS: 'sda_active_class',
  CURRENT_ATTEMPT: 'sda_current_attempt'
};

const AcademyState = {
  // Initialize default empty state if not present
  init() {
    if (!localStorage.getItem(STATE_KEYS.PROGRESS)) {
      this.setProgress({
        completedConcepts: {}, // CWE-89: "done"
        completedPractical: {}, // CD-01: { score: 100, date: 17... }
        completedTheory: {}, // TH-01: true
        xp: 0,
        level: 1,
        badges: []
      });
    }
    if (!localStorage.getItem(STATE_KEYS.WRONG_NOTES)) {
      this.setWrongNotes({});
    }
  },

  // --- Getters & Setters ---
  getProgress() {
    this.init();
    try {
      return JSON.parse(localStorage.getItem(STATE_KEYS.PROGRESS));
    } catch (e) {
      return { completedConcepts: {}, completedPractical: {}, completedTheory: {}, xp: 0, level: 1, badges: [] };
    }
  },

  setProgress(progress) {
    localStorage.setItem(STATE_KEYS.PROGRESS, JSON.stringify(progress));
    // 통합 XP/레벨/스트릭(아레나 + 아카데미)을 리더보드에 발행. streak 하드코딩 제거.
    if (window.sdaBoard && window.sdaBoard.getUser()) {
      const a = this._readAcademy();
      const xp = (progress.xp || 0) + a.xp;
      window.sdaBoard.publish({
        xp: xp,
        level: Math.floor(Math.sqrt(xp / 100)) + 1,
        streak: a.streak || 1
      }).catch(err => console.error('Leaderboard sync error:', err));
    }
  },

  // ── 아카데미(SPA) 진도 브리지 ──────────────────────────────────────────
  // secure-dev-academy.html 은 sda_learned / sda_gam / sda_wrong / sda_wrongStats 등
  // 별도 키를 쓴다(아레나의 sda_student_progress 와 스키마가 다름). 아레나 화면(대시보드·
  // 클래스·미션)이 아카데미 학습까지 함께 반영하도록 읽기 전용으로 병합한다.
  _readAcademy() {
    const j = (k, d) => { try { const v = JSON.parse(localStorage.getItem('sda_' + k)); return (v === null || v === undefined) ? d : v; } catch (e) { return d; } };
    const learned = j('learned', {});
    const gam = j('gam', {});
    const wrong = j('wrong', []);
    const wrongStats = j('wrongStats', {});
    return {
      concepts: (learned && typeof learned === 'object') ? Object.keys(learned).length : 0,
      xp: (gam && +gam.xp) || 0,
      streak: (gam && +gam.streak) || 0,
      bestStreak: (gam && +gam.bestStreak) || 0,
      wrongDue: Array.isArray(wrong) ? wrong.filter(w => (w.due || 0) <= Date.now()).length : 0,
      wrongTotal: Array.isArray(wrong) ? wrong.length : 0,
      wrongStats: (wrongStats && typeof wrongStats === 'object') ? wrongStats : {}
    };
  },

  // 아레나 + 아카데미를 합친 표시용 통계(쓰기 없음 → 상태 오염/중복합산 방지).
  getUnifiedStats() {
    const p = this.getProgress();
    const notes = this.getWrongNotes();
    const a = this._readAcademy();
    const arenaConcepts = Object.keys(p.completedConcepts || {}).length;
    const arenaPractical = Object.keys(p.completedPractical || {}).length;
    const arenaWrong = Object.values(notes).filter(n => !n.mastered).length;
    const xp = (p.xp || 0) + a.xp; // 두 앱은 서로 다른 행위에 XP를 주므로 합산이 정확
    const byCat = {};
    Object.values(notes).forEach(n => { if (!n.mastered && n.category) byCat[n.category] = (byCat[n.category] || 0) + 1; });
    Object.keys(a.wrongStats).forEach(k => { byCat[k] = (byCat[k] || 0) + (+a.wrongStats[k] || 0); });
    return {
      concepts: Math.max(arenaConcepts, a.concepts),
      practical: arenaPractical, // 아카데미는 문항별 추적을 안 하므로 아레나 기준 유지
      xp: xp,
      level: Math.floor(Math.sqrt(xp / 100)) + 1,
      streak: a.streak || 0,
      wrong: arenaWrong + a.wrongTotal,
      wrongByCat: byCat
    };
  },

  getWrongNotes() {
    this.init();
    try {
      return JSON.parse(localStorage.getItem(STATE_KEYS.WRONG_NOTES));
    } catch (e) {
      return {};
    }
  },

  setWrongNotes(notes) {
    localStorage.setItem(STATE_KEYS.WRONG_NOTES, JSON.stringify(notes));
  },

  getActiveClass() {
    try {
      return JSON.parse(localStorage.getItem(STATE_KEYS.CLASS));
    } catch (e) {
      return null;
    }
  },

  setActiveClass(classData) {
    if (classData) {
      localStorage.setItem(STATE_KEYS.CLASS, JSON.stringify(classData));
    } else {
      localStorage.removeItem(STATE_KEYS.CLASS);
    }
  },

  // --- Core State Modifiers ---
  awardXp(amount, reason) {
    const p = this.getProgress();
    p.xp = (p.xp || 0) + amount;
    
    // Simple leveling formula: Level = Math.floor(sqrt(XP/100)) + 1
    const newLevel = Math.floor(Math.sqrt(p.xp / 100)) + 1;
    let leveledUp = false;
    if (newLevel > (p.level || 1)) {
      p.level = newLevel;
      leveledUp = true;
    }

    // Award badges based on milestones
    const badges = p.badges || [];
    if (p.xp >= 100 && !badges.includes('입문자')) badges.push('입문자');
    if (p.xp >= 500 && !badges.includes('보안 분석가')) badges.push('보안 분석가');
    if (p.xp >= 1500 && !badges.includes('코드 진단 마스터')) badges.push('코드 진단 마스터');

    p.badges = badges;
    this.setProgress(p);
    this.showToast(`✨ +${amount} XP 획득! (${reason})`);
    if (leveledUp) {
      this.showToast(`🎉 레벨 업! Level ${newLevel} 달성!`);
    }
    return { leveledUp, newLevel };
  },

  completeConcept(cwe) {
    const p = this.getProgress();
    if (!p.completedConcepts[cwe]) {
      p.completedConcepts[cwe] = new Date().toISOString();
      this.setProgress(p);
      this.awardXp(10, `${cwe} 개념 학습 완료`);
    }
  },

  completePractical(qId, score, earnedXp) {
    const p = this.getProgress();
    const existing = p.completedPractical[qId];
    if (!existing || score > existing.score) {
      p.completedPractical[qId] = {
        score: score,
        completedAt: new Date().toISOString()
      };
      this.setProgress(p);
      if (earnedXp) {
        this.awardXp(earnedXp, `${qId} 코드 진단 통과`);
      }
    }
  },

  addWrongNote(question) {
    const notes = this.getWrongNotes();
    if (!notes[question.id]) {
      notes[question.id] = {
        id: question.id,
        category: question.cat || '기타',
        title: question.title || '코드 분석',
        type: question.type || 'PRAC',
        stem: question.stem || '',
        weaknessId: question.cwe || '',
        lastWrongAt: new Date().toISOString(),
        retryCount: 0,
        mastered: false
      };
    } else {
      notes[question.id].lastWrongAt = new Date().toISOString();
      notes[question.id].retryCount++;
    }
    this.setWrongNotes(notes);
    this.showToast(`📝 오답노트에 기록되었습니다: ${question.id}`);
  },

  resolveWrongNote(qId) {
    const notes = this.getWrongNotes();
    if (notes[qId]) {
      notes[qId].mastered = true;
      this.setWrongNotes(notes);
      this.awardXp(15, `오답 복습 통과: ${qId}`);
      this.showToast(`✅ 오답 마스터 성공!`);
    }
  },

  // --- UI Helper ---
  showToast(message) {
    let tBox = document.getElementById('stateToast');
    if (!tBox) {
      tBox = document.createElement('div');
      tBox.id = 'stateToast';
      tBox.style.cssText = `
        position: fixed;
        bottom: 24px;
        left: 50%;
        transform: translateX(-50%) translateY(100px);
        background: rgba(17, 24, 39, 0.95);
        color: #fff;
        padding: 12px 24px;
        border-radius: 30px;
        font-size: 13.5px;
        font-weight: bold;
        z-index: 1000000;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        border: 1px solid rgba(255,255,255,0.1);
        transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        pointer-events: none;
        display: flex;
        align-items: center;
        gap: 8px;
      `;
      document.body.appendChild(tBox);
    }
    tBox.textContent = message;
    tBox.style.transform = 'translateX(-50%) translateY(0)';
    
    clearTimeout(window.toastTimer);
    window.toastTimer = setTimeout(() => {
      tBox.style.transform = 'translateX(-50%) translateY(100px)';
    }, 3000);
  }
};

// Initialize on load
AcademyState.init();
