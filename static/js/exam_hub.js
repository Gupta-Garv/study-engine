/**
 * Term 7 Assessment Hub (Split-Pane Question Workbench + Exact Pattern Mock Exam Simulator)
 * Renders inside #view-exam alongside legacy Module Sets.
 */
window.ExamHub = {
  index: null,
  cache: {}, // slug -> { predicted, cla }
  mode: 'bank', // 'bank' | 'mock' | 'legacy'

  // Left sidebar & Question Bank state
  selectedSlug: 'family_business',
  expandedSubjects: new Set(['family_business']),
  activeCategory: 'subjective', // 'subjective' | 'case' | 'mcq' | 'msq' | 'cla'
  moduleFilter: 'all',
  viewStyle: 'focus', // 'focus' (1-by-1 + jump grid) | 'list'
  focusIdx: 0,

  revealedIds: new Set(),
  userSelections: {}, // uid -> index or number[]

  // Mock Exam state
  mock: {
    active: false,
    submitted: false,
    slug: 'family_business',
    questions: [],
    answers: {},
    currentIdx: 0,
    timerId: null,
    secondsLeft: 0,
  },

  async init() {
    if (!this.index) {
      try {
        const res = await fetch('./static/exam_bank/index.json?v=' + Date.now());
        if (res.ok) this.index = await res.json();
      } catch (e) {
        console.error('ExamHub index load failed:', e);
      }
    }
    if (!this.index) return;

    const withPred = this.index.subjects.find(s => s.has_predicted);
    if (withPred && !this.cache[this.selectedSlug]) {
      this.selectedSlug = withPred.slug;
      this.expandedSubjects = new Set([withPred.slug]);
    }

    await this.loadSubject(this.selectedSlug);
    this.ensureValidCategory();
    this.bindKeys();
    this.setMode(this.mode);
  },

  bindKeys() {
    if (this._keysBound) return;
    this._keysBound = true;
    document.addEventListener('keydown', (e) => {
      if (this.mode !== 'bank' || this.viewStyle !== 'focus') return;
      const viewExam = document.getElementById('view-exam');
      if (!viewExam || viewExam.classList.contains('hidden')) return;
      const tag = (e.target && e.target.tagName) || '';
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
      if (e.key === 'ArrowRight') { e.preventDefault(); this.stepFocus(1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); this.stepFocus(-1); }
    });
  },

  async loadSubject(slug) {
    if (this.cache[slug]) return this.cache[slug];
    const subjMeta = this.index?.subjects?.find(s => s.slug === slug);
    const entry = { predicted: null, cla: null };

    if (subjMeta?.has_predicted) {
      try {
        const r = await fetch(`./static/exam_bank/${slug}/exam_bank.json?v=` + Date.now());
        if (r.ok) entry.predicted = await r.json();
      } catch (e) { console.warn('Predicted load err:', e); }
    }
    if (subjMeta?.has_cla) {
      try {
        const r = await fetch(`./static/exam_bank/${slug}/cla_questions.json?v=` + Date.now());
        if (r.ok) entry.cla = await r.json();
      } catch (e) { console.warn('CLA load err:', e); }
    }
    this.cache[slug] = entry;
    return entry;
  },

  getSubjectCategories(slug) {
    const meta = this.index?.subjects?.find(s => s.slug === slug);
    const pc = meta?.predicted_counts || {};
    const cats = [];
    if ((pc.subjective || 0) > 0) cats.push({ key: 'subjective', label: 'Subjective Short', count: pc.subjective, badge: '5M' });
    if ((pc.case || 0) > 0) cats.push({ key: 'case', label: 'Case Studies', count: pc.case, badge: 'Case' });
    if ((pc.mcq || 0) > 0) cats.push({ key: 'mcq', label: 'MCQs (Exam-Level)', count: pc.mcq, badge: '1M' });
    if ((pc.msq || 0) > 0) cats.push({ key: 'msq', label: 'MSQs (Multi-Select)', count: pc.msq, badge: '2M' });
    if ((meta?.cla_count || 0) > 0) cats.push({ key: 'cla', label: 'CLA / Mid-Term Baseline', count: meta.cla_count, badge: 'Portal' });
    return cats;
  },

  ensureValidCategory() {
    const cats = this.getSubjectCategories(this.selectedSlug);
    if (!cats.length) return;
    if (!cats.some(c => c.key === this.activeCategory)) {
      this.activeCategory = cats[0].key;
    }
  },

  setMode(mode) {
    this.mode = mode;
    const bankEl = document.getElementById('hub-mode-bank');
    const mockEl = document.getElementById('hub-mode-mock');
    const legacyEl = document.getElementById('hub-mode-legacy');

    if (bankEl) bankEl.classList.toggle('hidden', mode !== 'bank');
    if (mockEl) mockEl.classList.toggle('hidden', mode !== 'mock');
    if (legacyEl) legacyEl.classList.toggle('hidden', mode !== 'legacy');

    ['bank', 'mock', 'legacy'].forEach(m => {
      const btn = document.getElementById(`hub-tab-${m}`);
      if (!btn) return;
      btn.className = m === mode
        ? 'px-3.5 py-1.5 rounded-full text-xs font-medium bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 shadow-soft-sm transition'
        : 'px-3.5 py-1.5 rounded-full text-xs font-medium text-ink-secondary hover:text-ink transition';
    });

    if (mode === 'bank') this.renderBank();
    if (mode === 'mock') this.renderMockSetup();
    if (window.lucide) window.lucide.createIcons();
  },

  async toggleSubjectDropdown(slug) {
    if (this.expandedSubjects.has(slug)) {
      if (this.selectedSlug === slug) {
        this.expandedSubjects.delete(slug);
      } else {
        this.selectedSlug = slug;
        await this.loadSubject(slug);
        this.ensureValidCategory();
      }
    } else {
      this.expandedSubjects.add(slug);
      this.selectedSlug = slug;
      this.moduleFilter = 'all';
      this.focusIdx = 0;
      await this.loadSubject(slug);
      this.ensureValidCategory();
    }
    this.renderBank();
  },

  async selectCategory(slug, catKey) {
    this.selectedSlug = slug;
    this.expandedSubjects.add(slug);
    this.activeCategory = catKey;
    this.moduleFilter = 'all';
    this.focusIdx = 0;
    await this.loadSubject(slug);
    this.renderBank();
  },

  setModuleFilter(val) {
    this.moduleFilter = val;
    this.focusIdx = 0;
    this.renderBank();
  },

  setViewStyle(style) {
    this.viewStyle = style;
    this.renderBank();
  },

  stepFocus(delta) {
    const qs = this.getActiveQuestions();
    if (!qs.length) return;
    this.focusIdx = Math.max(0, Math.min(qs.length - 1, this.focusIdx + delta));
    this.renderBank();
  },

  jumpToFocus(idx) {
    this.focusIdx = idx;
    this.renderBank();
  },

  getNormalizedQuestions(slug) {
    const data = this.cache[slug] || {};
    const list = [];

    if (data.predicted) {
      const p = data.predicted;
      (p.subjective_questions || []).forEach(q => {
        list.push({
          uid: `pred_sub_${slug}_${q.anticipation_rank}`,
          source: 'predicted',
          category: 'subjective',
          qType: 'subjective',
          rank: q.anticipation_rank,
          tier: q.anticipation_tier,
          moduleNum: q.module_number,
          moduleName: q.module_name,
          tag: q.framework,
          marks: q.marks || 5,
          targetWords: q.target_words || '≤100 words',
          question: q.question,
          modelAnswer: q.model_answer,
          wordCount: q.word_count,
          rubric: q.examiner_rubric || [],
          commonTrap: q.common_trap || '',
          images: q.images || [],
        });
      });

      (p.case_questions || []).forEach(q => {
        list.push({
          uid: `pred_case_${slug}_${q.anticipation_rank}`,
          source: 'predicted',
          category: 'case',
          qType: 'case',
          rank: q.anticipation_rank,
          tier: q.anticipation_tier,
          moduleNum: q.module_number,
          moduleName: q.module_name,
          tag: q.framework || 'Case Study',
          marks: q.marks || 3,
          targetWords: q.target_words || '40–50 words',
          question: q.question,
          caseContext: q.case_context || '',
          modelAnswer: q.model_answer,
          wordCount: q.word_count,
          rubric: q.examiner_rubric || [],
          commonTrap: q.common_trap || '',
          images: q.images || [],
        });
      });

      (p.mcq_questions || []).forEach(q => {
        list.push({
          uid: `pred_mcq_${slug}_${q.anticipation_rank}`,
          source: 'predicted',
          category: 'mcq',
          qType: 'mcq',
          rank: q.anticipation_rank,
          tier: q.anticipation_tier,
          moduleNum: q.module_number,
          moduleName: q.module_name,
          tag: q.key_concept,
          marks: q.marks || 1,
          question: q.question,
          options: q.options || [],
          correctIndices: [q.correct_index],
          explanation: q.explanation || '',
          distractorAnalysis: q.distractor_analysis || '',
          images: q.images || [],
        });
      });

      (p.msq_questions || []).forEach(q => {
        list.push({
          uid: `pred_msq_${slug}_${q.anticipation_rank}`,
          source: 'predicted',
          category: 'msq',
          qType: 'msq',
          rank: q.anticipation_rank,
          tier: q.anticipation_tier,
          moduleNum: q.module_number,
          moduleName: q.module_name,
          tag: q.key_concept,
          marks: q.marks || 2,
          question: q.question,
          options: q.options || [],
          correctIndices: q.correct_indices || [],
          explanation: q.explanation || '',
          distractorAnalysis: q.distractor_analysis || '',
          images: q.images || [],
        });
      });
    }

    if (data.cla) {
      let claIdx = 0;
      (data.cla.assessments || []).forEach(a => {
        if (a.status !== 'extracted') return;
        const mMatch = (a.module || '').match(/\d+/);
        const modNum = mMatch ? parseInt(mMatch[0], 10) : 0;
        (a.questions || []).forEach(q => {
          claIdx++;
          list.push({
            uid: `cla_${slug}_${claIdx}`,
            source: 'cla',
            category: 'cla',
            qType: q.type === 'multi_select' ? 'msq' : 'mcq',
            rank: claIdx,
            tier: `${a.module} (${a.assessment})`,
            moduleNum: modNum,
            moduleName: a.module,
            tag: 'Portal CLA / Mid-Term',
            marks: q.type === 'multi_select' ? 2 : 1,
            question: q.stem,
            options: (q.options || []).map(o => o.text),
            correctIndices: q.correct_indices || [],
            explanation: q.solution || '',
            distractorAnalysis: '',
            images: (q.images || []).map(img => `./static/exam_bank/${slug}/${img}`),
          });
        });
      });
    }

    return list;
  },

  getActiveQuestions() {
    const all = this.getNormalizedQuestions(this.selectedSlug);
    return all
      .filter(q => q.category === this.activeCategory)
      .filter(q => this.moduleFilter === 'all' || String(q.moduleNum) === String(this.moduleFilter))
      .sort((a, b) => a.rank - b.rank);
  },

  renderBank() {
    const container = document.getElementById('hub-mode-bank');
    if (!container || !this.index) return;

    const allInSubject = this.getNormalizedQuestions(this.selectedSlug);
    const catQuestions = allInSubject.filter(q => q.category === this.activeCategory);
    const modNums = [...new Set(catQuestions.map(q => q.moduleNum).filter(n => n > 0))].sort((a, b) => a - b);
    const filtered = this.getActiveQuestions();

    if (this.focusIdx >= filtered.length) this.focusIdx = Math.max(0, filtered.length - 1);

    const subjMeta = this.index.subjects.find(s => s.slug === this.selectedSlug);
    const cats = this.getSubjectCategories(this.selectedSlug);
    const activeCatObj = cats.find(c => c.key === this.activeCategory);

    // 1. Left Sidebar Accordion HTML
    const sidebarHtml = this.index.subjects.map(s => {
      const isExpanded = this.expandedSubjects.has(s.slug);
      const isSelected = s.slug === this.selectedSlug;
      const sCats = this.getSubjectCategories(s.slug);
      const predTotal = (s.predicted_counts?.subjective || 0) + (s.predicted_counts?.mcq || 0) + (s.predicted_counts?.msq || 0) + (s.predicted_counts?.case || 0);

      const subItemsHtml = isExpanded ? `
        <div class="mt-1.5 ml-2.5 pl-2.5 border-l border-border space-y-1">
          ${sCats.map(c => {
            const isCatActive = isSelected && this.activeCategory === c.key;
            return `<button onclick="ExamHub.selectCategory('${s.slug}', '${c.key}')"
              class="w-full text-left px-2.5 py-2 rounded-xl text-xs transition flex items-center justify-between gap-2 ${isCatActive
                ? 'bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 font-medium shadow-soft-sm'
                : 'text-ink-secondary hover:text-ink hover:bg-card-muted'}">
              <span class="truncate">${this.esc(c.label)}</span>
              <span class="text-[10px] font-mono shrink-0 px-1.5 py-0.5 rounded-md ${isCatActive ? 'bg-white/20 dark:bg-black/15' : 'bg-card-muted text-ink-secondary'}">${c.count}</span>
            </button>`;
          }).join('')}
        </div>` : '';

      return `
        <div class="rounded-2xl border ${isSelected ? 'border-neutral-400/60 dark:border-neutral-600 bg-card-muted/40' : 'border-transparent'} p-2 transition">
          <button onclick="ExamHub.toggleSubjectDropdown('${s.slug}')"
            class="w-full text-left px-2 py-1.5 rounded-xl flex items-center justify-between gap-2 hover:bg-card-muted transition">
            <div class="min-w-0">
              <div class="text-xs font-semibold text-ink truncate">${this.esc(s.name)}</div>
              <div class="text-[10px] font-mono text-ink-secondary mt-0.5">
                ${predTotal > 0 ? `${predTotal} Predicted • ${s.cla_count} CLA` : `${s.cla_count} CLA Baseline`}
              </div>
            </div>
            <i data-lucide="${isExpanded ? 'chevron-down' : 'chevron-right'}" class="w-3.5 h-3.5 text-ink-secondary shrink-0"></i>
          </button>
          ${subItemsHtml}
        </div>`;
    }).join('');

    // 2. Right Main Workspace
    let workspaceBody = '';
    if (!filtered.length) {
      workspaceBody = `
        <div class="rounded-2xl bg-card border border-border p-10 text-center space-y-2">
          <p class="text-sm font-medium text-ink">No questions in this view.</p>
          <p class="text-xs text-ink-secondary">Try selecting "All Modules" or pick another category from the left sidebar.</p>
        </div>`;
    } else if (this.viewStyle === 'focus') {
      const q = filtered[this.focusIdx];
      const jumpStrip = this.renderJumpStrip(filtered);
      workspaceBody = `
        <div class="space-y-4">
          ${this.renderQuestionCard(q, true, this.focusIdx, filtered.length)}
          ${jumpStrip}
        </div>`;
    } else {
      workspaceBody = `<div class="space-y-3">${filtered.map((q, i) => this.renderQuestionCard(q, false, i, filtered.length)).join('')}</div>`;
    }

    container.innerHTML = `
      <div class="grid grid-cols-1 lg:grid-cols-[260px_1fr] gap-6 items-start">
        <!-- Left Vertical Subject & Format Rail -->
        <aside class="rounded-2xl bg-card border border-border p-2.5 space-y-1 lg:sticky lg:top-16">
          <div class="px-2.5 py-2 flex items-center justify-between">
            <span class="text-xs font-medium text-ink">Subjects</span>
            <span class="text-[11px] font-mono text-ink-secondary">Term 7</span>
          </div>
          ${sidebarHtml}
        </aside>

        <!-- Right Main Workspace -->
        <section class="space-y-4 min-w-0">
          <!-- Workspace Header + Controls -->
          <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-border">
            <div class="min-w-0">
              <div class="text-xs text-ink-secondary">
                ${this.esc(subjMeta?.name || '')} / ${this.esc(activeCatObj?.label || '')}
              </div>
              <h2 class="text-base font-medium tracking-tight text-ink mt-0.5">
                ${this.activeCategory === 'cla' ? 'Portal CLA & Mid-Term Questions' : 'Predicted Exam Questions'}
              </h2>
            </div>

            <div class="flex flex-wrap items-center gap-2">
              <select onchange="ExamHub.setModuleFilter(this.value)"
                class="text-xs rounded-xl border border-border bg-card px-3 py-1.5 font-medium text-ink focus:outline-none">
                <option value="all" ${this.moduleFilter === 'all' ? 'selected' : ''}>All Modules (${catQuestions.length})</option>
                ${modNums.map(n => `<option value="${n}" ${String(this.moduleFilter) === String(n) ? 'selected' : ''}>Module ${n}</option>`).join('')}
              </select>

              <div class="inline-flex items-center p-0.5 rounded-xl bg-card border border-border">
                <button onclick="ExamHub.setViewStyle('focus')"
                  class="px-2.5 py-1 rounded-lg text-xs font-medium transition ${this.viewStyle === 'focus' ? 'bg-card-muted text-ink' : 'text-ink-secondary hover:text-ink'}">
                  Focus
                </button>
                <button onclick="ExamHub.setViewStyle('list')"
                  class="px-2.5 py-1 rounded-lg text-xs font-medium transition ${this.viewStyle === 'list' ? 'bg-card-muted text-ink' : 'text-ink-secondary hover:text-ink'}">
                  List
                </button>
              </div>
            </div>
          </div>

          ${workspaceBody}
        </section>
      </div>
    `;

    if (window.lucide) window.lucide.createIcons();
  },

  renderJumpStrip(filtered) {
    // Group by Tier if predicted, or flat if CLA
    const hasTiers = filtered.some(q => q.source === 'predicted');
    const pillFor = (q, i) => {
      const isCur = i === this.focusIdx;
      const isRev = this.revealedIds.has(q.uid);
      const sel = this.userSelections[q.uid];
      let statusCls = 'bg-card-muted text-ink-secondary border-border hover:border-neutral-400';
      if (isCur) {
        statusCls = 'bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 border-neutral-900 dark:border-white font-semibold';
      } else if (isRev && (q.qType === 'mcq' || q.qType === 'msq') && sel !== undefined) {
        const right = q.qType === 'mcq'
          ? sel === q.correctIndices[0]
          : Array.isArray(sel) && sel.length === q.correctIndices.length && sel.every(x => q.correctIndices.includes(x));
        statusCls = right
          ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border-emerald-500/30'
          : 'bg-rose-500/15 text-rose-700 dark:text-rose-300 border-rose-500/30';
      } else if (isRev) {
        statusCls = 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border-emerald-500/25';
      }
      return `<button onclick="ExamHub.jumpToFocus(${i})" title="#${q.rank} • Mod ${q.moduleNum}"
        class="w-8 h-8 rounded-lg border text-[11px] font-mono transition ${statusCls}">${q.rank}</button>`;
    };

    if (!hasTiers) {
      return `
        <div class="rounded-2xl bg-card border border-border p-4 space-y-2.5">
          <div class="flex items-center justify-between text-[11px] font-mono text-ink-secondary">
            <span>Quick Jump (${filtered.length} Questions)</span>
            <span>Use ← / → arrow keys</span>
          </div>
          <div class="flex flex-wrap gap-1.5">${filtered.map((q, i) => pillFor(q, i)).join('')}</div>
        </div>`;
    }

    const tiers = [
      { key: 'Tier 1', label: 'Tier 1: Most Anticipated', dot: 'bg-rose-500' },
      { key: 'Tier 2', label: 'Tier 2: High Probability', dot: 'bg-amber-500' },
      { key: 'Tier 3', label: 'Tier 3: Targeted Coverage', dot: 'bg-emerald-500' },
    ];

    const groupsHtml = tiers.map(t => {
      const items = filtered.map((q, i) => ({ q, i })).filter(x => (x.q.tier || '').includes(t.key));
      if (!items.length) return '';
      return `
        <div class="space-y-1.5">
          <div class="flex items-center gap-1.5 text-[11px] font-mono text-ink-secondary">
            <span class="w-1.5 h-1.5 rounded-full ${t.dot}"></span>
            <span>${t.label} (${items.length})</span>
          </div>
          <div class="flex flex-wrap gap-1.5">${items.map(x => pillFor(x.q, x.i)).join('')}</div>
        </div>`;
    }).join('');

    return `
      <div class="rounded-2xl bg-card border border-border p-4 space-y-3">
        <div class="flex items-center justify-between text-[11px] font-mono text-ink-secondary border-b border-border pb-2">
          <span>Question Navigator (Ordered Most → Least Anticipated)</span>
          <span>← / → keys</span>
        </div>
        ${groupsHtml}
      </div>`;
  },

  renderQuestionCard(q, isFocus, idx, total) {
    const isRevealed = this.revealedIds.has(q.uid);
    const isSubj = q.qType === 'subjective' || q.qType === 'case';

    const tierColor = q.source === 'cla'
      ? 'bg-card-muted text-ink-secondary border-border'
      : q.tier.includes('Tier 1')
        ? 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20'
        : q.tier.includes('Tier 2')
          ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20'
          : 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20';

    const typeLabel = q.qType === 'subjective' ? `${q.marks} Marks • ${q.targetWords}`
      : q.qType === 'case' ? `Case • ${q.marks}M (${q.targetWords})`
      : q.qType === 'msq' ? `MSQ • ${q.marks}M`
      : `MCQ • ${q.marks}M`;

    const imgsHtml = (q.images || []).length ? `
      <div class="flex flex-wrap gap-3 my-2">
        ${q.images.map(src => `<img src="${src}" class="max-h-72 rounded-xl border border-border bg-white p-1 object-contain" loading="lazy" />`).join('')}
      </div>` : '';

    let bodyHtml = '';
    if (isSubj) {
      bodyHtml = `
        <div class="pt-1">
          <button onclick="ExamHub.toggleReveal('${q.uid}')"
            class="px-4 py-2 rounded-full text-xs font-medium border border-border bg-card-muted hover:bg-muted text-ink transition inline-flex items-center gap-1.5">
            <i data-lucide="${isRevealed ? 'eye-off' : 'eye'}" class="w-3.5 h-3.5"></i>
            ${isRevealed ? 'Hide Model Answer & Rubric' : 'Reveal Max-Marks Model Answer & Rubric'}
          </button>
          ${isRevealed ? `
            <div class="mt-3 p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20 space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-[11px] font-mono uppercase tracking-wider text-emerald-600 dark:text-emerald-400 font-semibold">Max-Marks Model Answer</span>
                <span class="text-[11px] font-mono text-ink-secondary">${q.wordCount || ''} words</span>
              </div>
              <p class="text-sm leading-relaxed text-ink max-w-[75ch]">${this.esc(q.modelAnswer || '')}</p>
              ${(q.rubric && q.rubric.length) ? `
                <div class="pt-2 border-t border-emerald-500/15">
                  <span class="text-[10px] font-mono uppercase tracking-wider text-ink-secondary block mb-1">Examiner Rubric</span>
                  <ul class="list-disc list-inside text-xs text-ink-secondary space-y-1">
                    ${q.rubric.map(r => `<li>${this.esc(r)}</li>`).join('')}
                  </ul>
                </div>` : ''}
              ${q.commonTrap ? `
                <div class="pt-2 border-t border-emerald-500/15 text-xs text-amber-600 dark:text-amber-400">
                  <strong>Common Trap:</strong> ${this.esc(q.commonTrap)}
                </div>` : ''}
            </div>` : ''}
        </div>`;
    } else {
      const sel = this.userSelections[q.uid];
      const optsHtml = (q.options || []).map((opt, oIdx) => {
        const isCorrect = q.correctIndices.includes(oIdx);
        const isPicked = q.qType === 'msq' ? (Array.isArray(sel) && sel.includes(oIdx)) : sel === oIdx;
        let cls = 'border-border bg-canvas hover:border-neutral-400 text-ink';
        if (isRevealed) {
          if (isCorrect) cls = 'border-emerald-500 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 font-medium';
          else if (isPicked && !isCorrect) cls = 'border-rose-500 bg-rose-500/10 text-rose-700 dark:text-rose-300';
        } else if (isPicked) {
          cls = 'border-neutral-900 dark:border-white bg-card-muted font-medium text-ink';
        }
        const letter = String.fromCharCode(65 + oIdx);
        return `<button onclick="ExamHub.pickOption('${q.uid}', ${oIdx}, '${q.qType}')"
          class="w-full text-left px-3.5 py-2.5 rounded-xl border text-xs leading-relaxed transition flex items-start gap-2.5 ${cls}">
          <span class="font-mono font-semibold shrink-0 mt-0.5">${letter})</span>
          <span class="flex-1">${this.esc(opt)}</span>
          ${isRevealed && isCorrect ? '<span class="text-[10px] font-mono uppercase shrink-0 mt-0.5">✓ Correct</span>' : ''}
        </button>`;
      }).join('');

      bodyHtml = `
        <div class="space-y-2 pt-1">${optsHtml}</div>
        <div class="pt-1">
          <button onclick="ExamHub.toggleReveal('${q.uid}')"
            class="px-4 py-2 rounded-full text-xs font-medium border border-border bg-card-muted hover:bg-muted text-ink transition inline-flex items-center gap-1.5">
            <i data-lucide="${isRevealed ? 'eye-off' : 'check-circle-2'}" class="w-3.5 h-3.5"></i>
            ${isRevealed ? 'Hide Explanation' : 'Check / Reveal Answer'}
          </button>
          ${isRevealed && (q.explanation || q.distractorAnalysis) ? `
            <div class="mt-3 p-3.5 rounded-xl bg-card-muted border border-border space-y-1.5 text-xs">
              ${q.explanation ? `<p class="text-ink"><strong>Explanation:</strong> ${this.esc(q.explanation)}</p>` : ''}
              ${q.distractorAnalysis ? `<p class="text-ink-secondary"><strong>Trap / Distractors:</strong> ${this.esc(q.distractorAnalysis)}</p>` : ''}
            </div>` : ''}
        </div>`;
    }

    const focusFooter = isFocus ? `
      <div class="pt-4 border-t border-border flex items-center justify-between">
        <button onclick="ExamHub.stepFocus(-1)" ${idx === 0 ? 'disabled' : ''}
          class="pill-muted text-xs inline-flex items-center gap-1 ${idx === 0 ? 'opacity-40 cursor-not-allowed' : ''}">
          <i data-lucide="chevron-left" class="w-3.5 h-3.5"></i> Previous
        </button>
        <span class="text-xs font-mono text-ink-secondary">${idx + 1} / ${total}</span>
        <button onclick="ExamHub.stepFocus(1)" ${idx >= total - 1 ? 'disabled' : ''}
          class="pill-ink text-xs inline-flex items-center gap-1 ${idx >= total - 1 ? 'opacity-40 cursor-not-allowed' : ''}">
          Next <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
        </button>
      </div>` : '';

    return `
      <div class="rounded-[1.5rem] bg-card border border-border shadow-soft p-5 sm:p-6 space-y-4">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div class="flex flex-wrap items-center gap-1.5">
            <span class="text-[11px] font-mono font-semibold px-2.5 py-0.5 rounded-full border ${tierColor}">
              #${q.rank} • ${this.esc(q.tier)}
            </span>
            <span class="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-card-muted border border-border text-ink-secondary">
              ${this.esc(typeLabel)}
            </span>
            ${q.moduleNum ? `<span class="text-[11px] font-mono px-2 py-0.5 rounded-full bg-card-muted text-ink-secondary">Mod ${q.moduleNum}</span>` : ''}
          </div>
          <span class="text-[11px] font-mono text-ink-secondary">${this.esc(q.tag || '')}</span>
        </div>

        ${q.caseContext ? `<div class="p-3.5 rounded-xl bg-card-muted border border-border text-xs text-ink-secondary leading-relaxed">${this.esc(q.caseContext)}</div>` : ''}
        <p class="text-sm sm:text-[15px] font-medium leading-relaxed text-ink max-w-[75ch]">${this.esc(q.question)}</p>
        ${imgsHtml}
        ${bodyHtml}
        ${focusFooter}
      </div>`;
  },

  toggleReveal(uid) {
    if (this.revealedIds.has(uid)) this.revealedIds.delete(uid);
    else this.revealedIds.add(uid);
    this.renderBank();
  },

  pickOption(uid, idx, qType) {
    if (qType === 'msq') {
      const cur = Array.isArray(this.userSelections[uid]) ? [...this.userSelections[uid]] : [];
      const pos = cur.indexOf(idx);
      if (pos >= 0) cur.splice(pos, 1);
      else cur.push(idx);
      this.userSelections[uid] = cur;
    } else {
      this.userSelections[uid] = idx;
    }
    this.renderBank();
  },

  // -----------------------------------------------------------
  // Term 7 Mock Exam Simulator
  // -----------------------------------------------------------
  renderMockSetup() {
    const container = document.getElementById('hub-mode-mock');
    if (!container || !this.index) return;

    if (this.mock.active) {
      this.renderMockRunner();
      return;
    }

    const cards = this.index.subjects.map(s => {
      const ready = s.has_predicted;
      return `
        <div class="rounded-2xl bg-card border border-border shadow-soft p-5 flex flex-col justify-between gap-4">
          <div class="space-y-2">
            <div class="flex items-center justify-between gap-2">
              <span class="text-[10px] font-mono uppercase tracking-wider text-ink-secondary">${this.esc(s.exam_date)}</span>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded-full ${ready ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20' : 'bg-card-muted text-ink-secondary border border-border'}">
                ${ready ? 'Mock Ready' : 'Generating Soon'}
              </span>
            </div>
            <h3 class="text-base font-semibold tracking-tight text-ink">${this.esc(s.name)}</h3>
            <p class="text-xs text-ink-secondary leading-relaxed">${this.esc(s.pattern_summary)}</p>
            <div class="flex flex-wrap gap-2 pt-1 text-[11px] font-mono text-ink-secondary">
              <span>${s.duration_mins} mins</span> • <span>${s.total_marks} marks</span> • <span>${s.negative_marking ? 'MSQ Partial Neg' : 'No Neg Marking'}</span>
            </div>
          </div>
          <button ${ready ? `onclick="ExamHub.startMock('${s.slug}')"` : 'disabled'}
            class="${ready ? 'pill-ink cursor-pointer' : 'pill-muted opacity-40 cursor-not-allowed'} text-xs w-full justify-center inline-flex items-center gap-1.5">
            <i data-lucide="play" class="w-3.5 h-3.5"></i>
            ${ready ? 'Start Full Term 7 Mock Exam' : 'Question Bank Pending'}
          </button>
        </div>`;
    }).join('');

    container.innerHTML = `
      <div class="space-y-4">
        <div class="rounded-[1.5rem] bg-card border border-border shadow-soft p-6">
          <h2 class="text-lg font-semibold tracking-tight text-ink">Term 7 Full Mock Exam Simulator</h2>
          <p class="text-xs text-ink-secondary mt-1">Timed full-length simulation matching your exact BBA DBE Term 7 paper patterns, marks, word-count limits, and scoring rules.</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">${cards}</div>
      </div>`;
    if (window.lucide) window.lucide.createIcons();
  },

  async startMock(slug) {
    await this.loadSubject(slug);
    const data = this.cache[slug]?.predicted;
    if (!data) return;

    const pattern = data.exam_pattern || {};
    const sections = pattern.sections || [];
    const pool = [];

    const shuffle = arr => {
      const a = [...arr];
      for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
      }
      return a;
    };

    sections.forEach(sec => {
      if (sec.type === 'MCQ') {
        const mcqs = shuffle(data.mcq_questions || []).slice(0, sec.count);
        mcqs.forEach(q => pool.push({
          section: sec.name,
          qType: 'mcq',
          marks: sec.marks_each,
          question: q.question,
          options: q.options,
          correctIndices: [q.correct_index],
          explanation: q.explanation,
          distractorAnalysis: q.distractor_analysis,
          moduleName: q.module_name,
        }));
      } else if (sec.type === 'MSQ') {
        const msqs = shuffle(data.msq_questions || []).slice(0, sec.count);
        msqs.forEach(q => pool.push({
          section: sec.name,
          qType: 'msq',
          marks: sec.marks_each,
          question: q.question,
          options: q.options,
          correctIndices: q.correct_indices || [],
          explanation: q.explanation,
          distractorAnalysis: q.distractor_analysis,
          moduleName: q.module_name,
        }));
      } else if (sec.type === 'Short Answer') {
        const subs = shuffle(data.subjective_questions || []).slice(0, sec.count);
        subs.forEach(q => pool.push({
          section: sec.name,
          qType: 'subjective',
          marks: sec.marks_each,
          wordLimit: sec.indicative_word_limit || 100,
          question: q.question,
          modelAnswer: q.model_answer,
          rubric: q.examiner_rubric || [],
          commonTrap: q.common_trap || '',
          moduleName: q.module_name,
        }));
      }
    });

    if (this.mock.timerId) clearInterval(this.mock.timerId);
    this.mock = {
      active: true,
      submitted: false,
      slug,
      courseName: data.course_name,
      pattern,
      questions: pool,
      answers: {},
      currentIdx: 0,
      secondsLeft: (pattern.duration_mins || 120) * 60,
      timerId: null,
    };

    this.mock.timerId = setInterval(() => {
      if (!this.mock.active || this.mock.submitted) return;
      this.mock.secondsLeft = Math.max(0, this.mock.secondsLeft - 1);
      const tEl = document.getElementById('mock-timer-display');
      if (tEl) tEl.textContent = this.formatTime(this.mock.secondsLeft);
      if (this.mock.secondsLeft === 0) this.submitMock();
    }, 1000);

    this.renderMockRunner();
  },

  formatTime(sec) {
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    const s = sec % 60;
    return h > 0
      ? `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
      : `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  },

  renderMockRunner() {
    const container = document.getElementById('hub-mode-mock');
    if (!container) return;

    if (this.mock.submitted) {
      this.renderMockResults();
      return;
    }

    const q = this.mock.questions[this.mock.currentIdx];
    const total = this.mock.questions.length;
    const ans = this.mock.answers[this.mock.currentIdx];

    const navPills = this.mock.questions.map((item, i) => {
      const answered = this.mock.answers[i] !== undefined && this.mock.answers[i] !== '' && !(Array.isArray(this.mock.answers[i]) && this.mock.answers[i].length === 0);
      const isCur = i === this.mock.currentIdx;
      const cls = isCur
        ? 'bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 border-neutral-900'
        : answered
          ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border-emerald-500/30'
          : 'bg-card-muted text-ink-secondary border-border';
      return `<button onclick="ExamHub.jumpMock(${i})" class="w-8 h-8 rounded-lg border text-[11px] font-mono font-medium ${cls}">${i + 1}</button>`;
    }).join('');

    let inputHtml = '';
    if (q.qType === 'subjective') {
      const txt = typeof ans === 'string' ? ans : '';
      const wc = txt.trim() ? txt.trim().split(/\s+/).length : 0;
      const limit = q.wordLimit || 100;
      inputHtml = `
        <div class="space-y-2">
          <div class="flex items-center justify-between text-xs font-mono text-ink-secondary">
            <span>Write your structured answer (Target: ≤ ${limit} words)</span>
            <span id="mock-word-counter" class="${wc > limit ? 'text-amber-500 font-semibold' : ''}">${wc} / ${limit} words</span>
          </div>
          <textarea oninput="ExamHub.updateMockText(${this.mock.currentIdx}, this.value, ${limit})"
            rows="6" placeholder="State the framework, diagnose the core issue, and give a crisp recommendation..."
            class="w-full rounded-xl border border-border bg-canvas p-3.5 text-sm text-ink focus:outline-none focus:ring-1 focus:ring-ink">${this.esc(txt)}</textarea>
        </div>`;
    } else {
      inputHtml = `<div class="space-y-2">
        ${(q.options || []).map((opt, idx) => {
          const picked = q.qType === 'msq' ? (Array.isArray(ans) && ans.includes(idx)) : ans === idx;
          const letter = String.fromCharCode(65 + idx);
          return `<button onclick="ExamHub.pickMockOption(${this.mock.currentIdx}, ${idx}, '${q.qType}')"
            class="w-full text-left px-4 py-3 rounded-xl border text-xs leading-relaxed transition flex items-start gap-2.5 ${picked
              ? 'border-neutral-900 dark:border-white bg-card-muted font-medium text-ink'
              : 'border-border bg-canvas hover:border-neutral-400 text-ink'}">
            <span class="font-mono font-semibold shrink-0">${letter})</span>
            <span>${this.esc(opt)}</span>
          </button>`;
        }).join('')}
      </div>`;
    }

    container.innerHTML = `
      <div class="rounded-[1.5rem] bg-card border border-border shadow-soft p-6 space-y-5">
        <div class="flex flex-wrap items-center justify-between gap-3 border-b border-border pb-4">
          <div>
            <span class="text-[10px] font-mono uppercase tracking-wider text-ink-secondary">${this.esc(this.mock.courseName)} • ${this.esc(q.section)}</span>
            <h3 class="text-base font-semibold text-ink">Question ${this.mock.currentIdx + 1} of ${total} <span class="text-xs font-mono text-ink-secondary ml-2">(${q.marks} Marks • ${q.qType.toUpperCase()})</span></h3>
          </div>
          <div class="flex items-center gap-3">
            <span id="mock-timer-display" class="px-3 py-1 rounded-full bg-card-muted border border-border font-mono text-xs font-semibold text-ink">${this.formatTime(this.mock.secondsLeft)}</span>
            <button onclick="ExamHub.exitMock()" class="text-xs text-ink-secondary hover:text-ink">Exit</button>
          </div>
        </div>

        <p class="text-sm font-medium leading-relaxed text-ink">${this.esc(q.question)}</p>
        ${inputHtml}

        <div class="flex items-center justify-between pt-4 border-t border-border">
          <button onclick="ExamHub.jumpMock(${Math.max(0, this.mock.currentIdx - 1)})" ${this.mock.currentIdx === 0 ? 'disabled' : ''} class="pill-muted text-xs">Previous</button>
          <div class="flex gap-2">
            ${this.mock.currentIdx < total - 1
              ? `<button onclick="ExamHub.jumpMock(${this.mock.currentIdx + 1})" class="pill-muted text-xs">Next</button>`
              : ''}
            <button onclick="ExamHub.submitMock()" class="pill-ink text-xs">Submit & Evaluate Mock</button>
          </div>
        </div>

        <div class="pt-3 border-t border-border">
          <span class="text-[10px] font-mono uppercase text-ink-secondary block mb-2">Question Navigator</span>
          <div class="flex flex-wrap gap-1.5">${navPills}</div>
        </div>
      </div>`;
  },

  jumpMock(i) {
    this.mock.currentIdx = i;
    this.renderMockRunner();
  },

  pickMockOption(qIdx, optIdx, qType) {
    if (qType === 'msq') {
      const cur = Array.isArray(this.mock.answers[qIdx]) ? [...this.mock.answers[qIdx]] : [];
      const pos = cur.indexOf(optIdx);
      if (pos >= 0) cur.splice(pos, 1);
      else cur.push(optIdx);
      this.mock.answers[qIdx] = cur;
    } else {
      this.mock.answers[qIdx] = optIdx;
    }
    this.renderMockRunner();
  },

  updateMockText(qIdx, val, limit) {
    this.mock.answers[qIdx] = val;
    const wc = val.trim() ? val.trim().split(/\s+/).length : 0;
    const el = document.getElementById('mock-word-counter');
    if (el) {
      el.textContent = `${wc} / ${limit} words`;
      el.className = wc > limit ? 'text-amber-500 font-semibold' : '';
    }
  },

  submitMock() {
    if (this.mock.timerId) clearInterval(this.mock.timerId);
    this.mock.submitted = true;
    this.renderMockResults();
  },

  exitMock() {
    if (this.mock.timerId) clearInterval(this.mock.timerId);
    this.mock.active = false;
    this.renderMockSetup();
  },

  renderMockResults() {
    const container = document.getElementById('hub-mode-mock');
    if (!container) return;

    let objScore = 0;
    let objMax = 0;
    let subjMax = 0;

    const reviewHtml = this.mock.questions.map((q, i) => {
      const ans = this.mock.answers[i];
      if (q.qType === 'subjective') {
        subjMax += q.marks;
        const txt = (typeof ans === 'string' && ans.trim()) ? ans : '(Not attempted)';
        return `
          <div class="rounded-2xl bg-card border border-border p-5 space-y-3">
            <div class="flex items-center justify-between text-xs font-mono text-ink-secondary">
              <span>Q${i + 1} • ${this.esc(q.section)} (${q.marks} Marks)</span>
              <span>Self-Evaluate</span>
            </div>
            <p class="text-sm font-medium text-ink">${this.esc(q.question)}</p>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div class="p-3.5 rounded-xl bg-card-muted border border-border space-y-1">
                <span class="text-[10px] font-mono uppercase text-ink-secondary">Your Answer</span>
                <p class="text-xs text-ink leading-relaxed whitespace-pre-wrap">${this.esc(txt)}</p>
              </div>
              <div class="p-3.5 rounded-xl bg-emerald-500/5 border border-emerald-500/20 space-y-2">
                <span class="text-[10px] font-mono uppercase text-emerald-600 dark:text-emerald-400 font-semibold">Max-Marks Model Answer</span>
                <p class="text-xs text-ink leading-relaxed">${this.esc(q.modelAnswer)}</p>
                ${(q.rubric || []).length ? `<ul class="list-disc list-inside text-[11px] text-ink-secondary pt-1 border-t border-emerald-500/15">${q.rubric.map(r => `<li>${this.esc(r)}</li>`).join('')}</ul>` : ''}
              </div>
            </div>
          </div>`;
      } else {
        objMax += q.marks;
        let earned = 0;
        if (q.qType === 'mcq') {
          if (ans === q.correctIndices[0]) earned = q.marks;
        } else if (q.qType === 'msq') {
          const picked = Array.isArray(ans) ? ans : [];
          const k = q.correctIndices.length || 1;
          const unit = q.marks / k;
          let raw = 0;
          picked.forEach(p => { raw += q.correctIndices.includes(p) ? unit : -unit; });
          earned = Math.max(0, raw);
        }
        objScore += earned;
        const ok = earned === q.marks;
        const correctLetters = q.correctIndices.map(c => String.fromCharCode(65 + c) + ') ' + q.options[c]).join(' | ');
        const pickedLabel = q.qType === 'msq'
          ? (Array.isArray(ans) && ans.length ? ans.map(p => String.fromCharCode(65 + p)).join(', ') : 'None')
          : (ans !== undefined ? String.fromCharCode(65 + ans) : 'Unanswered');
        return `
          <div class="rounded-2xl bg-card border ${ok ? 'border-emerald-500/30' : 'border-rose-500/30'} p-4 space-y-2">
            <div class="flex items-center justify-between text-xs font-mono">
              <span class="text-ink-secondary">Q${i + 1} • ${this.esc(q.section)}</span>
              <span class="${ok ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'} font-semibold">${earned.toFixed(2)} / ${q.marks}</span>
            </div>
            <p class="text-xs font-medium text-ink">${this.esc(q.question)}</p>
            <p class="text-xs text-ink-secondary"><strong>Your choice:</strong> ${this.esc(pickedLabel)} &nbsp;|&nbsp; <strong class="text-emerald-600 dark:text-emerald-400">Correct:</strong> ${this.esc(correctLetters)}</p>
            ${q.explanation ? `<p class="text-[11px] text-ink-secondary">${this.esc(q.explanation)}</p>` : ''}
          </div>`;
      }
    }).join('');

    container.innerHTML = `
      <div class="space-y-5">
        <div class="rounded-[1.5rem] bg-card border border-border shadow-soft p-6 flex flex-wrap items-center justify-between gap-4">
          <div>
            <span class="text-[10px] font-mono uppercase tracking-wider text-ink-secondary">Mock Exam Submitted</span>
            <h2 class="text-xl font-bold text-ink">${this.esc(this.mock.courseName)}</h2>
            <p class="text-xs text-ink-secondary mt-1">Objective Score: <strong>${objScore.toFixed(2)} / ${objMax}</strong>${subjMax > 0 ? ` • Subjective (${subjMax}M): Compare side-by-side below` : ''}</p>
          </div>
          <div class="flex gap-2">
            <button onclick="ExamHub.startMock('${this.mock.slug}')" class="pill-muted text-xs">New Randomized Mock</button>
            <button onclick="ExamHub.exitMock()" class="pill-ink text-xs">Back to Mock Setup</button>
          </div>
        </div>
        <div class="space-y-3">${reviewHtml}</div>
      </div>`;
  },

  esc(s) {
    return String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }
};
