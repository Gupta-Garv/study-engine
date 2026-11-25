/**
 * Visual Cram & Interactive Flowchart Engine for One-Shot Revision
 * Designed for a 2-hour zero-to-pass sprint:
 *   - 1-Screen = 1-Sheet (no endless wall-of-text scroll)
 *   - Interactive Node-and-Edge Flowcharts with SVG connectors
 *   - Blur / Active-Recall Toggle
 *   - Pass-Floor vs Full-Depth Filter
 *   - Exam Trigger Decoder & Last-15-Min Trap Radar
 */
window.VisualCram = {
  mode: 'visual', // 'visual' | 'text'
  cache: {},      // courseId -> json
  courseMap: {
    'deb83564': 'data_visualisation',
    'db945ff9': 'family_business',
    'd9173426': 'critical_thinking',
    '2989cdfe': 'corporate_finance',
  },
  activeCourseId: null,
  activeSheetId: 'triggers',
  selectedNodeId: null,
  recallBlur: false,
  passFloorOnly: false,
  revealedBlurKeys: new Set(),

  async loadForCourse(courseId) {
    this.activeCourseId = courseId;
    const slug = this.courseMap[courseId];
    if (!slug) {
      this.setMode('text', true);
      return false;
    }
    if (!this.cache[courseId]) {
      try {
        const res = await fetch(`./static/cram_maps/${slug}.json?v=` + Date.now());
        if (res.ok) {
          this.cache[courseId] = await res.json();
        } else {
          this.cache[courseId] = null;
        }
      } catch (e) {
        this.cache[courseId] = null;
      }
    }

    const hasVisual = !!this.cache[courseId];
    const toggleWrap = document.getElementById('oneshot-visual-toggle');
    if (toggleWrap) toggleWrap.classList.toggle('hidden', !hasVisual);

    if (hasVisual) {
      const sheets = this.getSheets(this.cache[courseId]);
      if (!sheets.some(s => s.id === this.activeSheetId)) {
        this.activeSheetId = sheets[0]?.id || 'triggers';
      }
      this.selectedNodeId = null;
      this.setMode(this.mode, false);
      return true;
    } else {
      this.setMode('text', false);
      return false;
    }
  },

  getSheets(data) {
    if (!data) return [];
    const sheets = [];
    if (data.triggers && data.triggers.length) {
      sheets.push({ id: 'triggers', title: 'Exam Trigger Decoder', mins: '10 min', kind: 'triggers' });
    }
    (data.modules || []).forEach(m => {
      sheets.push({ id: m.id, title: m.title, mins: m.sprint_mins || '12 min', kind: 'flow', module: m });
    });
    if (data.formula_web) {
      sheets.push({ id: 'formula_web', title: 'Formula Dependency Web', mins: '15 min', kind: 'flow', module: data.formula_web });
    }
    if (data.traps && data.traps.length) {
      sheets.push({ id: 'traps', title: 'Last-15-Min Trap Radar', mins: '10 min', kind: 'traps' });
    }
    return sheets;
  },

  setMode(mode, rerender = true) {
    if (mode === 'visual' && !this.cache[this.activeCourseId]) mode = 'text';
    this.mode = mode;

    const visContainer = document.getElementById('oneshot-visual-container');
    const txtContainer = document.getElementById('oneshot-text-container');
    const btnVis = document.getElementById('btn-oneshot-mode-visual');
    const btnTxt = document.getElementById('btn-oneshot-mode-text');

    if (visContainer) visContainer.classList.toggle('hidden', mode !== 'visual');
    if (txtContainer) txtContainer.classList.toggle('hidden', mode !== 'text');

    if (btnVis && btnTxt) {
      const activeCls = 'px-3 py-1 rounded-full text-xs font-medium bg-ink text-canvas transition';
      const idleCls = 'px-3 py-1 rounded-full text-xs font-medium text-ink-secondary hover:text-ink transition';
      btnVis.className = mode === 'visual' ? activeCls : idleCls;
      btnTxt.className = mode === 'text' ? activeCls : idleCls;
    }

    if (mode === 'visual' && rerender !== false) {
      this.render();
    }
  },

  selectSheet(sheetId) {
    this.activeSheetId = sheetId;
    this.selectedNodeId = null;
    this.render();
  },

  selectNode(nodeId) {
    this.selectedNodeId = (this.selectedNodeId === nodeId) ? null : nodeId;
    this.render();
  },

  toggleBlur() {
    this.recallBlur = !this.recallBlur;
    this.revealedBlurKeys.clear();
    this.render();
  },

  togglePassFloor() {
    this.passFloorOnly = !this.passFloorOnly;
    this.render();
  },

  revealBlurKey(k) {
    this.revealedBlurKeys.add(k);
    this.render();
  },

  maskable(text, key) {
    if (!this.recallBlur || this.revealedBlurKeys.has(key)) return this.esc(text);
    return `<button onclick="event.stopPropagation(); VisualCram.revealBlurKey('${key}')" class="inline-flex items-center px-2 py-0.5 rounded bg-card-muted border border-border text-ink-secondary hover:text-ink font-mono text-[11px] transition" title="Tap to reveal">[ Tap to Recall ]</button>`;
  },

  render() {
    const root = document.getElementById('oneshot-visual-container');
    const data = this.cache[this.activeCourseId];
    if (!root || !data) return;

    const sheets = this.getSheets(data);
    const activeIdx = Math.max(0, sheets.findIndex(s => s.id === this.activeSheetId));
    const sheet = sheets[activeIdx];
    if (!sheet) return;

    const railHtml = sheets.map((s, idx) => {
      const active = s.id === sheet.id;
      return `<button onclick="VisualCram.selectSheet('${s.id}')"
        class="w-full text-left px-3 py-2.5 rounded-xl text-xs transition flex items-center justify-between gap-2 ${active
          ? 'bg-ink text-canvas font-medium'
          : 'text-ink-secondary hover:text-ink hover:bg-card-muted'}">
        <span class="truncate">${idx + 1}. ${this.esc(s.title)}</span>
        <span class="text-[10px] font-mono shrink-0 opacity-75">${this.esc(s.mins)}</span>
      </button>`;
    }).join('');

    let mainHtml = '';
    if (sheet.kind === 'triggers') {
      mainHtml = this.renderTriggers(data.triggers);
    } else if (sheet.kind === 'traps') {
      mainHtml = this.renderTraps(data.traps);
    } else if (sheet.kind === 'flow') {
      mainHtml = this.renderFlowchart(sheet.module);
    }

    root.innerHTML = `
      <div class="flex-1 overflow-hidden flex min-h-0">
        <!-- Left Sheet Rail -->
        <aside class="w-64 shrink-0 border-r border-border bg-card p-3 overflow-y-auto space-y-1.5 hidden md:block">
          <div class="px-2 py-1.5 flex items-center justify-between border-b border-border mb-1">
            <span class="text-xs font-medium text-ink">2-Hour Sprint Plan</span>
            <span class="text-[11px] font-mono text-ink-secondary">${activeIdx + 1}/${sheets.length}</span>
          </div>
          ${railHtml}
        </aside>

        <!-- Right Visual Canvas -->
        <main class="flex-1 overflow-y-auto bg-canvas p-4 sm:p-6 lg:p-8">
          <div class="max-w-5xl mx-auto space-y-5">
            <!-- Mobile Sheet Switcher + Top Controls -->
            <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-border">
              <div class="space-y-0.5">
                <div class="text-xs font-mono folio-accent-text">Sheet ${activeIdx + 1} of ${sheets.length} / Target ${this.esc(sheet.mins)}</div>
                <h2 class="text-lg font-medium tracking-tight text-ink">${this.esc(sheet.title)}</h2>
              </div>

              <div class="flex flex-wrap items-center gap-2">
                <select onchange="VisualCram.selectSheet(this.value)" class="md:hidden text-xs rounded-xl border border-border bg-card px-2.5 py-1.5 text-ink">
                  ${sheets.map((s, i) => `<option value="${s.id}" ${s.id === sheet.id ? 'selected' : ''}>${i + 1}. ${this.esc(s.title)}</option>`).join('')}
                </select>

                <button onclick="VisualCram.togglePassFloor()"
                  class="px-3 py-1.5 rounded-xl border text-xs font-medium transition ${this.passFloorOnly ? 'border-amber-500/50 folio-accent-bg' : 'border-border bg-card text-ink-secondary hover:text-ink'}">
                  ${this.passFloorOnly ? 'Core Pass-Floor: ON' : 'Core Pass-Floor'}
                </button>

                <button onclick="VisualCram.toggleBlur()"
                  class="px-3 py-1.5 rounded-xl border text-xs font-medium transition ${this.recallBlur ? 'bg-ink text-canvas border-ink' : 'border-border bg-card text-ink-secondary hover:text-ink'}">
                  ${this.recallBlur ? 'Recall Blur: ON' : 'Recall Blur'}
                </button>
              </div>
            </div>

            ${mainHtml}

            <!-- Bottom Sheet Pager -->
            <div class="pt-4 border-t border-border flex items-center justify-between">
              <button onclick="VisualCram.selectSheet('${sheets[Math.max(0, activeIdx - 1)].id}')" ${activeIdx === 0 ? 'disabled' : ''}
                class="pill-muted text-xs ${activeIdx === 0 ? 'opacity-40 cursor-not-allowed' : ''}">Previous Sheet</button>
              <button onclick="VisualCram.selectSheet('${sheets[Math.min(sheets.length - 1, activeIdx + 1)].id}')" ${activeIdx >= sheets.length - 1 ? 'disabled' : ''}
                class="pill-ink text-xs ${activeIdx >= sheets.length - 1 ? 'opacity-40 cursor-not-allowed' : ''}">Next Sheet</button>
            </div>
          </div>
        </main>
      </div>
    `;

    // Render KaTeX & SVG Connectors after DOM paint
    if (window.renderMathInElement) {
      window.renderMathInElement(root, {
        delimiters: [{ left: '$$', right: '$$', display: true }, { left: '$', right: '$', display: false }],
        throwOnError: false
      });
    }
    if (sheet.kind === 'flow') {
      requestAnimationFrame(() => this.drawFlowConnectors(sheet.module));
    }
    if (window.lucide) window.lucide.createIcons();
  },

  renderTriggers(triggers) {
    return `
      <div class="space-y-3">
        <p class="text-xs text-ink-secondary">Scan the exam symptom on the left, then lock in the exact framework and opening line on the right.</p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          ${triggers.map((t, i) => `
            <div class="rounded-2xl bg-card border border-border p-4 space-y-2">
              <div class="text-xs text-ink-secondary">If the question says:</div>
              <div class="text-sm font-medium text-ink">${this.esc(t.symptom)}</div>
              <div class="pt-2 border-t border-border space-y-1">
                <div class="text-xs font-mono folio-accent-text">${this.maskable(t.framework, 'trig_fw_' + i)}</div>
                <div class="text-xs text-ink-secondary leading-relaxed">${this.maskable(t.action, 'trig_act_' + i)}</div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  },

  renderTraps(traps) {
    return `
      <div class="space-y-3">
        <p class="text-xs text-ink-secondary">High-frequency mistakes tested in MCQs, MSQs, and numericals.</p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          ${traps.map((t, i) => `
            <div class="rounded-2xl bg-card border border-border p-4 space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-[11px] font-mono text-rose-500">Trap ${i + 1}</span>
                <span class="text-[11px] font-mono text-ink-secondary">${this.esc(t.module || '')}</span>
              </div>
              <div class="text-sm font-medium text-ink">${this.esc(t.trap)}</div>
              <div class="text-xs text-emerald-600 dark:text-emerald-400 pt-1 border-t border-border">
                Fix: ${this.maskable(t.fix, 'trap_' + i)}
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  },

  renderFlowchart(mod) {
    const nodes = mod.nodes || [];
    const maxRow = Math.max(...nodes.map(n => n.row || 1), 1);
    const activeNode = nodes.find(n => n.id === this.selectedNodeId) || nodes[0];

    let rowsHtml = '';
    for (let r = 1; r <= maxRow; r++) {
      const rowNodes = nodes.filter(n => (n.row || 1) === r);
      const colsCls = rowNodes.length === 1 ? 'grid-cols-1 max-w-md mx-auto'
        : rowNodes.length === 2 ? 'grid-cols-1 sm:grid-cols-2'
        : 'grid-cols-1 sm:grid-cols-3';
      rowsHtml += `
        <div class="grid ${colsCls} gap-4 relative z-10">
          ${rowNodes.map(n => {
            const isSel = activeNode && activeNode.id === n.id;
            const dimmed = this.passFloorOnly && !n.core;
            return `<button id="flow-node-${n.id}" onclick="VisualCram.selectNode('${n.id}')"
              class="text-left rounded-2xl p-4 border transition ${isSel
                ? 'bg-card-muted border-amber-500/60 shadow-soft-md'
                : 'bg-card border-border hover:border-neutral-400'} ${dimmed ? 'opacity-35' : ''}">
              <div class="flex items-center justify-between gap-2 mb-1">
                <span class="text-[10px] font-mono ${n.core ? 'folio-accent-text' : 'text-ink-secondary'}">${n.core ? 'Core Pass-Floor' : 'Nuance'}</span>
                ${n.tag ? `<span class="text-[10px] font-mono text-ink-secondary">${this.esc(n.tag)}</span>` : ''}
              </div>
              <div class="text-sm font-medium text-ink">${this.maskable(n.label, 'node_lbl_' + n.id)}</div>
              <div class="text-xs text-ink-secondary mt-1 line-clamp-2">${this.esc(n.short)}</div>
            </button>`;
          }).join('')}
        </div>`;
    }

    const detailHtml = activeNode ? `
      <div class="rounded-2xl bg-card border border-border p-5 space-y-3 shadow-soft">
        <div class="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-border">
          <div>
            <span class="text-[11px] font-mono folio-accent-text">${this.esc(activeNode.tag || 'Node Detail')}</span>
            <h3 class="text-base font-medium text-ink">${this.esc(activeNode.label)}</h3>
          </div>
          <span class="text-[11px] font-mono text-ink-secondary">Tap nodes above to inspect connections</span>
        </div>
        ${activeNode.formula ? `<div class="p-3 rounded-xl bg-card-muted border border-border text-sm font-mono text-ink overflow-x-auto">${this.esc(activeNode.formula)}</div>` : ''}
        <ul class="space-y-1.5 text-xs text-ink leading-relaxed list-disc list-inside">
          ${(activeNode.bullets || []).map((b, idx) => `<li>${this.maskable(b, `det_${activeNode.id}_${idx}`)}</li>`).join('')}
        </ul>
        ${activeNode.trap ? `<div class="pt-2 border-t border-border text-xs text-rose-500"><strong>Exam Trap:</strong> ${this.esc(activeNode.trap)}</div>` : ''}
      </div>` : '';

    return `
      <div class="space-y-5">
        ${mod.summary ? `<p class="text-xs text-ink-secondary leading-relaxed max-w-[70ch]">${this.esc(mod.summary)}</p>` : ''}
        <div id="flow-canvas-wrap" class="relative space-y-6 p-4 sm:p-6 rounded-3xl bg-card/40 border border-border">
          <svg id="flow-svg-layer" class="pointer-events-none absolute inset-0 w-full h-full z-0" aria-hidden="true"></svg>
          ${rowsHtml}
        </div>
        ${detailHtml}
      </div>
    `;
  },

  drawFlowConnectors(mod) {
    const wrap = document.getElementById('flow-canvas-wrap');
    const svg = document.getElementById('flow-svg-layer');
    if (!wrap || !svg) return;

    const wRect = wrap.getBoundingClientRect();
    svg.setAttribute('viewBox', `0 0 ${wRect.width} ${wRect.height}`);
    const edges = mod.edges || [];
    const paths = [];

    edges.forEach(([fromId, toId]) => {
      const a = document.getElementById(`flow-node-${fromId}`);
      const b = document.getElementById(`flow-node-${toId}`);
      if (!a || !b) return;
      const ra = a.getBoundingClientRect();
      const rb = b.getBoundingClientRect();
      const x1 = ra.left - wRect.left + ra.width / 2;
      const y1 = ra.bottom - wRect.top;
      const x2 = rb.left - wRect.left + rb.width / 2;
      const y2 = rb.top - wRect.top;
      const midY = (y1 + y2) / 2;
      paths.push(`<path d="M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2}" fill="none" stroke="var(--accent)" stroke-opacity="0.45" stroke-width="1.6" />`);
      paths.push(`<circle cx="${x2}" cy="${y2}" r="3" fill="var(--accent)" fill-opacity="0.75" />`);
    });

    svg.innerHTML = paths.join('');
  },

  esc(s) {
    return String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }
};
