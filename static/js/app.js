/**
 * StudyEngine Frontend Application Controller
 * Handles Subjects, Modules, Batch Ingestion, Live Curation, Notes Reader, and Exam Arena.
 */

const App = {
  currentView: 'dashboard',
  courses: [],
  selectedCourseId: null,
  selectedModuleId: null,
  selectedTopicId: null,
  expandedModuleIds: new Set(),
  isSidebarOpen: true,
  isCopilotOpen: true,
  copilotMessages: [],
  isCopilotLoading: false,
  searchDebounceTimer: null,
  activeSearchResultIndex: -1,
  searchResults: [],
  lastSearchQuery: '',
  studiedTopicIds: new Set(),
  lastStudiedTopicId: null,
  examSchedule: {
    title: 'Term Examinations',
    targetDate: '2026-11-05T09:30',
    notes: 'Nov 5–6 Degree Examinations'
  },
  checklistFilter: 'all',
  checklistItems: [],
  countdownInterval: null,
  paneState: { video: true, notes: true, canvas: false, copilot: false },
  activePreset: 'lecture',
  videoSpeed: 1,
  currentTopicCanvas: { cards: [], connections: [] },
  draggingCardId: null,
  dragOffset: { x: 0, y: 0 },
  connectingFromCardId: null,

  isStaticHost() {
    return window.location.hostname.includes('github.io');
  },

  notifyStaticViewer(action = "curate or modify content") {
    alert(
      `⚠️ Static Viewer Notice:\n\n` +
      `You are currently on the GitHub Pages static viewer (gupta-garv.github.io).\n\n` +
      `GitHub Pages is a static file host for reading notes and taking mock exams 24/7. It cannot run the local Python server, Whisper AI, or FFmpeg OCR.\n\n` +
      `To ${action}, please open http://127.0.0.1:8000 on your Mac where your Python engine runs. Once curated, the notes will sync here!`
    );
  },

  async init() {
    this.initTheme();
    if (this.isStaticHost()) {
      const banner = document.getElementById('static-viewer-banner');
      if (banner) banner.classList.remove('hidden');
    }
    this.initResizers();
    this.initSearch();
    this.initDashboard();
    this.initCanvasListeners();
    this.updateStudioLayout();
    await this.loadCourses();
    this.switchView('dashboard');
    if (window.lucide) window.lucide.createIcons();
    this.startPolling();
  },

  // -------------------------------------------------------------
  // Theme Management
  // -------------------------------------------------------------
  initTheme() {
    const isDark = localStorage.getItem('study_engine_theme') === 'dark' ||
      (!localStorage.getItem('study_engine_theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);
    if (isDark) document.documentElement.classList.add('dark');
    else document.documentElement.classList.remove('dark');
  },

  toggleTheme() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('study_engine_theme', isDark ? 'dark' : 'light');
    if (window.lucide) window.lucide.createIcons();
  },

  // -------------------------------------------------------------
  // Global Search Controller (Cross-Subject & Multi-Occurrence)
  // -------------------------------------------------------------
  initSearch() {
    // Global hotkey: Cmd+K / Ctrl+K or '/'
    document.addEventListener('keydown', (e) => {
      const tag = (e.target && e.target.tagName) || '';
      const isInput = tag === 'INPUT' || tag === 'TEXTAREA' || e.target.isContentEditable;
      
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        const input = document.getElementById('global-search-input');
        if (input) {
          input.focus();
          input.select();
        }
      } else if (e.key === '/' && !isInput) {
        e.preventDefault();
        const input = document.getElementById('global-search-input');
        if (input) {
          input.focus();
          input.select();
        }
      }
    });

    // Close search dropdown on click outside
    document.addEventListener('click', (e) => {
      const container = document.getElementById('global-search-container');
      if (container && !container.contains(e.target)) {
        this.closeSearchDropdown();
      }
    });
  },

  onSearchFocus() {
    const input = document.getElementById('global-search-input');
    if (input && input.value.trim().length >= 1) {
      const dropdown = document.getElementById('search-results-dropdown');
      if (dropdown) dropdown.classList.remove('hidden');
      if (this.searchResults.length === 0) {
        this.executeSearch(input.value.trim());
      }
    }
  },

  onSearchInput(value) {
    const clearBtn = document.getElementById('global-search-clear');
    if (clearBtn) {
      clearBtn.classList.toggle('hidden', !value || value.length === 0);
    }

    clearTimeout(this.searchDebounceTimer);
    const query = value.trim();
    if (!query) {
      this.closeSearchDropdown();
      this.searchResults = [];
      return;
    }

    this.searchDebounceTimer = setTimeout(() => {
      this.executeSearch(query);
    }, 120);
  },

  clearSearch() {
    const input = document.getElementById('global-search-input');
    if (input) {
      input.value = '';
      input.focus();
    }
    const clearBtn = document.getElementById('global-search-clear');
    if (clearBtn) clearBtn.classList.add('hidden');
    this.closeSearchDropdown();
    this.searchResults = [];
  },

  closeSearchDropdown() {
    const dropdown = document.getElementById('search-results-dropdown');
    if (dropdown) dropdown.classList.add('hidden');
    this.activeSearchResultIndex = -1;
  },

  onSearchKeydown(event) {
    const dropdown = document.getElementById('search-results-dropdown');
    if (!dropdown || dropdown.classList.contains('hidden') || this.searchResults.length === 0) {
      if (event.key === 'Escape') {
        const input = document.getElementById('global-search-input');
        if (input) input.blur();
      }
      return;
    }

    if (event.key === 'ArrowDown') {
      event.preventDefault();
      this.activeSearchResultIndex = (this.activeSearchResultIndex + 1) % this.searchResults.length;
      this.updateActiveSearchItem();
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      if (this.activeSearchResultIndex <= 0) {
        this.activeSearchResultIndex = this.searchResults.length - 1;
      } else {
        this.activeSearchResultIndex--;
      }
      this.updateActiveSearchItem();
    } else if (event.key === 'Enter') {
      event.preventDefault();
      const idx = this.activeSearchResultIndex >= 0 ? this.activeSearchResultIndex : 0;
      const target = this.searchResults[idx];
      if (target) {
        this.jumpToSearchResult(target.topic_id, this.lastSearchQuery, target.heading);
      }
    } else if (event.key === 'Escape') {
      event.preventDefault();
      this.closeSearchDropdown();
      const input = document.getElementById('global-search-input');
      if (input) input.blur();
    }
  },

  updateActiveSearchItem() {
    const items = document.querySelectorAll('.search-result-item');
    items.forEach((item, idx) => {
      if (idx === this.activeSearchResultIndex) {
        item.classList.add('search-item-active');
        item.scrollIntoView({ block: 'nearest' });
      } else {
        item.classList.remove('search-item-active');
      }
    });
  },

  getCourseColor(courseName) {
    const lower = (courseName || '').toLowerCase();
    if (lower.includes('corporate finance')) {
      return { bg: 'bg-blue-500/10 dark:bg-blue-400/15 text-blue-600 dark:text-blue-400 border-blue-500/20' };
    }
    if (lower.includes('family business')) {
      return { bg: 'bg-amber-500/10 dark:bg-amber-400/15 text-amber-600 dark:text-amber-400 border-amber-500/20' };
    }
    if (lower.includes('critical thinking')) {
      return { bg: 'bg-emerald-500/10 dark:bg-emerald-400/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/20' };
    }
    if (lower.includes('startup dilemma')) {
      return { bg: 'bg-purple-500/10 dark:bg-purple-400/15 text-purple-600 dark:text-purple-400 border-purple-500/20' };
    }
    if (lower.includes('data visual')) {
      return { bg: 'bg-rose-500/10 dark:bg-rose-400/15 text-rose-600 dark:text-rose-400 border-rose-500/20' };
    }
    return { bg: 'bg-neutral-500/10 text-neutral-600 dark:text-neutral-400 border-neutral-500/20' };
  },

  async executeSearch(query) {
    this.lastSearchQuery = query;
    const queryLower = query.toLowerCase();
    const dropdown = document.getElementById('search-results-dropdown');
    const list = document.getElementById('search-results-list');
    const countEl = document.getElementById('search-results-count');
    if (!dropdown || !list) return;

    dropdown.classList.remove('hidden');
    list.innerHTML = '<div class="p-4 text-center text-xs text-neutral-400 font-mono">Searching vault...</div>';
    if (countEl) countEl.textContent = `Searching for "${query}"...`;

    let results = [];

    // 1. Try local server /api/search if online
    try {
      const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
      if (res.ok) {
        results = await res.json();
      }
    } catch (e) {
      // Offline / GitHub Pages fallback
    }

    // 2. Client-side fallback if fetch failed or returned empty while window.STUDY_DATA exists
    if ((!results || results.length === 0) && window.STUDY_DATA && window.STUDY_DATA.topics) {
      results = this.searchInMemory(queryLower);
    }

    this.searchResults = results || [];
    this.activeSearchResultIndex = -1;

    if (this.searchResults.length === 0) {
      if (countEl) countEl.textContent = `0 results found`;
      list.innerHTML = `
        <div class="p-6 text-center space-y-2">
          <div class="w-8 h-8 rounded-full bg-muted mx-auto flex items-center justify-center text-neutral-400">
            <i data-lucide="search-x" class="w-4 h-4"></i>
          </div>
          <p class="text-xs font-medium text-ink">No lectures or sections match "${this.escapeHtml(query)}"</p>
          <p class="text-[11px] text-neutral-400 max-w-xs mx-auto">Try searching for concepts like "DCF", "galaxy", "fallacy", "governance", or "box plot".</p>
        </div>
      `;
      if (window.lucide) window.lucide.createIcons();
      return;
    }

    // Count distinct lectures
    const uniqueTopics = new Set(this.searchResults.map(r => r.topic_id));
    if (countEl) {
      countEl.innerHTML = `Found <span class="font-semibold text-ink">${this.searchResults.length}</span> places across <span class="font-semibold text-ink">${uniqueTopics.size}</span> lectures for "<span class="text-ink">${this.escapeHtml(query)}</span>"`;
    }

    // Render result items
    list.innerHTML = this.searchResults.map((r, idx) => {
      const courseStyle = this.getCourseColor(r.course_name);
      const highlightedSnippet = this.highlightSnippet(r.snippet, query);
      const highlightedTitle = this.highlightSnippet(r.title, query);
      const isTitleMatch = r.heading === 'Lecture Title';

      return `
        <div 
          class="search-result-item p-3 rounded-xl border border-transparent hover:border-border cursor-pointer select-none space-y-1.5"
          data-index="${idx}"
          onclick="App.jumpToSearchResult('${r.topic_id}', '${App.escapeHtml(query)}', '${App.escapeHtml(r.heading)}')"
        >
          <!-- Course & Module Badges -->
          <div class="flex items-center justify-between gap-2">
            <div class="flex items-center gap-1.5 min-w-0">
              <span class="text-[10px] font-mono px-2 py-0.5 rounded-full border ${courseStyle.bg} shrink-0">
                ${this.escapeHtml(r.course_name)}
              </span>
              <span class="text-[10px] font-mono text-neutral-400 truncate">
                ${this.escapeHtml(r.module_name)}
              </span>
            </div>
            ${r.match_count > 1 ? `<span class="text-[9px] font-mono text-neutral-400 px-1.5 py-0.5 rounded bg-card-muted shrink-0">${r.match_count} matches</span>` : ''}
          </div>

          <!-- Lecture Title -->
          <div class="text-xs font-semibold text-ink flex items-center gap-2">
            <i data-lucide="video" class="w-3.5 h-3.5 text-neutral-400 shrink-0"></i>
            <span class="truncate">${highlightedTitle}</span>
          </div>

          <!-- Section Heading -->
          ${!isTitleMatch && r.heading ? `
            <div class="text-[11px] font-medium text-ink-secondary flex items-center gap-1.5 pl-5">
              <span class="text-amber-500 font-mono text-xs">§</span>
              <span class="truncate text-neutral-600 dark:text-neutral-300">${this.escapeHtml(r.heading)}</span>
            </div>
          ` : ''}

          <!-- Context Snippet -->
          <div class="text-[11px] text-neutral-500 dark:text-neutral-400 pl-5 leading-relaxed line-clamp-2">
            ${highlightedSnippet}
          </div>
        </div>
      `;
    }).join('');

    if (window.lucide) window.lucide.createIcons();
  },

  searchInMemory(queryLower) {
    if (!window.STUDY_DATA || !window.STUDY_DATA.topics) return [];
    
    // Build module mapping
    const moduleMap = {};
    if (this.courses) {
      for (const c of this.courses) {
        for (const m of (c.modules || [])) {
          moduleMap[m.id] = {
            course_id: c.id,
            course_name: c.name,
            module_id: m.id,
            module_name: m.name,
            module_number: m.number || 1
          };
        }
      }
    }

    const results = [];
    for (const [tId, t] of Object.entries(window.STUDY_DATA.topics)) {
      if (t.status !== 'completed') continue;
      const title = t.title || '';
      const notes = t.notes_markdown || '';
      const tLower = title.toLowerCase();
      const nLower = notes.toLowerCase();

      const titleMatches = tLower.includes(queryLower);
      const notesMatches = nLower.includes(queryLower);
      if (!titleMatches && !notesMatches) continue;

      const mInfo = moduleMap[t.module_id] || {
        course_name: 'Course',
        module_name: 'Module',
        course_id: '',
        module_id: t.module_id
      };

      // Count occurrences
      let count = 0;
      try {
        const matches = notes.match(new RegExp(this.escapeRegExp(queryLower), 'gi'));
        count = matches ? matches.length : 0;
      } catch (e) {
        count = 1;
      }
      if (titleMatches) count++;

      // Title hit
      if (titleMatches) {
        results.push({
          topic_id: tId,
          title: title,
          course_id: mInfo.course_id,
          course_name: mInfo.course_name,
          module_id: mInfo.module_id,
          module_name: mInfo.module_name,
          heading: 'Lecture Title',
          snippet: title,
          match_count: count,
          score: queryLower === tLower ? 300 : 200
        });
      }

      // Section hits
      const sections = notes.split(/\n(?=#{1,4}\s+)/);
      let secIdx = 0;
      for (const sec of sections) {
        const secLower = sec.toLowerCase();
        if (secLower.includes(queryLower)) {
          const hdgMatch = sec.match(/^#{1,4}\s+([^\n]+)/);
          const heading = hdgMatch ? hdgMatch[1].trim() : 'Overview';
          if (heading.toLowerCase() === tLower && titleMatches) continue;

          const pos = secLower.indexOf(queryLower);
          const start = Math.max(0, pos - 45);
          const end = Math.min(sec.length, pos + queryLower.length + 55);
          let snip = sec.slice(start, end).replace(/\n/g, ' ').trim();
          if (start > 0) snip = '...' + snip;
          if (end < sec.length) snip = snip + '...';

          results.push({
            topic_id: tId,
            title: title,
            course_id: mInfo.course_id,
            course_name: mInfo.course_name,
            module_id: mInfo.module_id,
            module_name: mInfo.module_name,
            heading: heading,
            snippet: snip,
            match_count: count,
            score: 100 - Math.min(secIdx, 30)
          });
          secIdx++;
        }
      }
    }

    results.sort((a, b) => b.score - a.score);
    return results.slice(0, 50);
  },

  highlightSnippet(text, query) {
    if (!text || !query) return this.escapeHtml(text || '');
    const escaped = this.escapeHtml(text);
    const regex = new RegExp(`(${this.escapeRegExp(this.escapeHtml(query))})`, 'gi');
    return escaped.replace(regex, '<mark class="search-highlight">$1</mark>');
  },

  escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  },

  escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  },

  async jumpToSearchResult(topicId, searchText, headingText) {
    this.closeSearchDropdown();
    const input = document.getElementById('global-search-input');
    if (input) input.blur();

    // 1. Switch view to Study Hall (Notes)
    this.switchView('notes');

    // 2. Load the notes for the target topic
    await this.loadTopicNotes(topicId);

    // 3. Highlight and smooth scroll to the specific match
    this.highlightAndScrollToMatch(searchText, headingText);
  },

  highlightAndScrollToMatch(searchText, headingText) {
    const container = document.getElementById('notes-content-body');
    if (!container) return;

    setTimeout(() => {
      // 1. Apply highlights to text nodes matching searchText
      if (searchText && searchText.trim().length >= 2) {
        this.applyTextHighlights(container, searchText.trim());
      }

      // 2. Locate target element (by heading or text content)
      let targetElement = null;

      if (headingText && headingText !== 'Lecture Title' && headingText !== 'Overview') {
        const cleanHeading = headingText.toLowerCase().replace(/^[0-9.]+\s*/, '').trim();
        const headings = container.querySelectorAll('h1, h2, h3, h4');
        for (const h of headings) {
          const hText = h.textContent.toLowerCase().replace(/^[0-9.]+\s*/, '').trim();
          if (hText.includes(cleanHeading) || cleanHeading.includes(hText)) {
            targetElement = h;
            break;
          }
        }
      }

      // If heading match was not found or not specified, search for element containing searchText
      if (!targetElement && searchText) {
        const queryLower = searchText.toLowerCase();
        const candidateElements = container.querySelectorAll('h1, h2, h3, h4, p, li, blockquote, tr, td');
        for (const el of candidateElements) {
          if (el.textContent.toLowerCase().includes(queryLower)) {
            targetElement = el;
            break;
          }
        }
      }

      // Fallback: first mark element if any
      if (!targetElement) {
        targetElement = container.querySelector('mark.search-highlight');
      }

      // 3. Scroll and pulse
      if (targetElement) {
        targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        targetElement.classList.add('search-target-pulse');
        setTimeout(() => {
          targetElement.classList.remove('search-target-pulse');
        }, 4000);
      }
    }, 150);
  },

  applyTextHighlights(rootElement, query) {
    if (!rootElement || !query) return;
    const regex = new RegExp(`(${this.escapeRegExp(query)})`, 'gi');

    // Safe TreeWalker across text nodes, ignoring KaTeX, code blocks, and math
    const walker = document.createTreeWalker(
      rootElement,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode(node) {
          const parent = node.parentElement;
          if (!parent) return NodeFilter.FILTER_REJECT;
          const tag = parent.tagName.toLowerCase();
          if (tag === 'script' || tag === 'style' || tag === 'mark') return NodeFilter.FILTER_REJECT;
          if (parent.closest('.katex') || parent.closest('.mermaid') || parent.closest('pre')) return NodeFilter.FILTER_REJECT;
          if (node.nodeValue && regex.test(node.nodeValue)) {
            return NodeFilter.FILTER_ACCEPT;
          }
          return NodeFilter.FILTER_SKIP;
        }
      }
    );

    const nodesToReplace = [];
    while (walker.nextNode()) {
      nodesToReplace.push(walker.currentNode);
    }

    nodesToReplace.forEach(textNode => {
      const val = textNode.nodeValue;
      if (!val) return;
      const frag = document.createDocumentFragment();
      let lastIdx = 0;
      regex.lastIndex = 0;
      let match;
      while ((match = regex.exec(val)) !== null) {
        if (match.index > lastIdx) {
          frag.appendChild(document.createTextNode(val.slice(lastIdx, match.index)));
        }
        const mark = document.createElement('mark');
        mark.className = 'search-highlight';
        mark.textContent = match[0];
        frag.appendChild(mark);
        lastIdx = regex.lastIndex;
      }
      if (lastIdx < val.length) {
        frag.appendChild(document.createTextNode(val.slice(lastIdx)));
      }
      if (textNode.parentNode) {
        textNode.parentNode.replaceChild(frag, textNode);
      }
    });
  },

  // -------------------------------------------------------------
  // Degree Command Dashboard & Exam Countdown
  // -------------------------------------------------------------
  initDashboard() {
    try {
      const savedStudied = localStorage.getItem('study_engine_studied_topics');
      if (savedStudied) {
        this.studiedTopicIds = new Set(JSON.parse(savedStudied));
      }
      this.lastStudiedTopicId = localStorage.getItem('study_engine_last_studied_topic');

      const savedSchedule = localStorage.getItem('study_engine_exam_schedule');
      if (savedSchedule) {
        this.examSchedule = JSON.parse(savedSchedule);
      }

      const savedChecklist = localStorage.getItem('study_engine_checklist');
      if (savedChecklist) {
        this.checklistItems = JSON.parse(savedChecklist);
      } else {
        this.checklistItems = this.getDefaultChecklist();
      }
    } catch (e) {
      this.checklistItems = this.getDefaultChecklist();
    }

    this.startExamCountdown();
  },

  getDefaultChecklist() {
    return [
      { id: 'task-1', text: 'Corporate Finance: Master DCF & WACC formula mechanics', subject: 'corporate-finance', completed: false },
      { id: 'task-2', text: 'Corporate Finance: Review Beta vs Standalone Project Risk Examiner Gotchas', subject: 'corporate-finance', completed: false },
      { id: 'task-3', text: 'Family Business Strategy: Master Entrepreneurial Family Galaxy & Orbital Ventures', subject: 'family-business', completed: false },
      { id: 'task-4', text: 'Family Business Strategy: Review 3-Circle Governance Alignment Matrix', subject: 'family-business', completed: false },
      { id: 'task-5', text: 'Critical Thinking: Master Top 10 Fallacy Traps in MCQ radar', subject: 'critical-thinking', completed: false },
      { id: 'task-6', text: 'Startup Dilemmas: Compare Founder Equity Split Models & Vesting Pitfalls', subject: 'startup-dilemmas', completed: false },
      { id: 'task-7', text: 'Data Visualisation: Memorize Chart Selection Matrix (Distribution vs Composition)', subject: 'data-visualisation', completed: false }
    ];
  },

  startExamCountdown() {
    clearInterval(this.countdownInterval);
    const update = () => {
      const now = new Date().getTime();
      const target = new Date(this.examSchedule.targetDate).getTime();
      const diff = target - now;

      const titleEl = document.getElementById('exam-countdown-title');
      const targetDisplay = document.getElementById('countdown-target-display');
      if (titleEl) titleEl.textContent = this.examSchedule.title || 'Term Exams';
      if (targetDisplay) targetDisplay.textContent = this.examSchedule.notes || 'Target: Nov 5–6';

      const daysEl = document.getElementById('countdown-days');
      const hoursEl = document.getElementById('countdown-hours');
      const minsEl = document.getElementById('countdown-mins');

      if (diff <= 0) {
        if (daysEl) daysEl.textContent = '00';
        if (hoursEl) hoursEl.textContent = '00';
        if (minsEl) minsEl.textContent = '00';
        return;
      }

      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

      if (daysEl) daysEl.textContent = String(days).padStart(2, '0');
      if (hoursEl) hoursEl.textContent = String(hours).padStart(2, '0');
      if (minsEl) minsEl.textContent = String(mins).padStart(2, '0');
    };

    update();
    this.countdownInterval = setInterval(update, 30000);
  },

  openExamDateModal() {
    const modal = document.getElementById('modal-exam-dates');
    if (!modal) return;
    const titleInput = document.getElementById('exam-modal-title');
    const dtInput = document.getElementById('exam-modal-datetime');
    const notesInput = document.getElementById('exam-modal-notes');

    if (titleInput) titleInput.value = this.examSchedule.title || 'Term Examinations';
    if (dtInput) dtInput.value = this.examSchedule.targetDate || '2026-11-05T09:30';
    if (notesInput) notesInput.value = this.examSchedule.notes || 'Nov 5–6 Degree Examinations';

    modal.classList.remove('hidden');
    if (window.lucide) window.lucide.createIcons();
  },

  closeExamDateModal() {
    const modal = document.getElementById('modal-exam-dates');
    if (modal) modal.classList.add('hidden');
  },

  saveExamDates() {
    const titleInput = document.getElementById('exam-modal-title');
    const dtInput = document.getElementById('exam-modal-datetime');
    const notesInput = document.getElementById('exam-modal-notes');

    if (titleInput && titleInput.value.trim()) {
      this.examSchedule.title = titleInput.value.trim();
    }
    if (dtInput && dtInput.value) {
      this.examSchedule.targetDate = dtInput.value;
    }
    if (notesInput) {
      this.examSchedule.notes = notesInput.value.trim();
    }

    localStorage.setItem('study_engine_exam_schedule', JSON.stringify(this.examSchedule));
    this.closeExamDateModal();
    this.startExamCountdown();
  },

  renderDashboard() {
    this.renderRecentLectureBanner();
    this.renderSubjectMasteryCards();
    this.renderChecklist();
    if (window.lucide) window.lucide.createIcons();
  },

  renderRecentLectureBanner() {
    const banner = document.getElementById('dashboard-recent-lecture-banner');
    if (!banner) return;

    let recentTopic = null;
    let recentCourse = null;

    if (this.lastStudiedTopicId && this.courses) {
      for (const c of this.courses) {
        for (const m of (c.modules || [])) {
          const t = (m.topics || []).find(x => x.id === this.lastStudiedTopicId);
          if (t) {
            recentTopic = t;
            recentCourse = c;
            break;
          }
        }
        if (recentTopic) break;
      }
    }

    if (recentTopic && recentCourse) {
      banner.innerHTML = `
        <div class="inline-flex items-center gap-3 p-2.5 px-4 rounded-2xl bg-card border border-border shadow-soft-sm">
          <div class="w-8 h-8 rounded-xl bg-ink text-canvas flex items-center justify-center shrink-0">
            <i data-lucide="play" class="w-3.5 h-3.5 fill-current"></i>
          </div>
          <div class="min-w-0 pr-2">
            <div class="text-[10px] font-mono text-neutral-400 uppercase truncate">Continue where you left off &bull; ${this.escapeHtml(recentCourse.name)}</div>
            <div class="text-xs font-semibold text-ink truncate max-w-sm">${this.escapeHtml(recentTopic.title)}</div>
          </div>
          <button onclick="App.jumpToTopic('${recentTopic.id}')" class="pill-ink text-xs px-3.5 py-1.5 shrink-0 flex items-center gap-1">
            <span>Resume Lecture</span>
            <i data-lucide="arrow-right" class="w-3 h-3"></i>
          </button>
        </div>
      `;
    } else {
      banner.innerHTML = `
        <button onclick="App.switchView('notes')" class="pill-ink text-xs px-4 py-2 inline-flex items-center gap-2">
          <i data-lucide="sparkles" class="w-3.5 h-3.5"></i>
          <span>Launch Study Studio (463 Lectures Ready)</span>
        </button>
      `;
    }
  },

  renderSubjectMasteryCards() {
    const container = document.getElementById('dashboard-subject-cards');
    const overallProgressEl = document.getElementById('overall-degree-progress');
    if (!container) return;

    if (!this.courses || this.courses.length === 0) {
      container.innerHTML = '<div class="col-span-3 text-center py-8 text-neutral-400 text-xs">Loading curriculum...</div>';
      return;
    }

    let totalDegreeLectures = 0;
    let totalDegreeStudied = 0;

    container.innerHTML = this.courses.map(c => {
      const courseStyle = this.getCourseColor(c.name);
      const totalLectures = (c.modules || []).reduce((acc, m) => acc + (m.topics ? m.topics.length : 0), 0);
      const studiedCount = (c.modules || []).reduce((acc, m) => {
        return acc + (m.topics ? m.topics.filter(t => this.studiedTopicIds.has(t.id)).length : 0);
      }, 0);

      totalDegreeLectures += totalLectures;
      totalDegreeStudied += studiedCount;

      const pct = totalLectures > 0 ? Math.round((studiedCount / totalLectures) * 100) : 0;
      const firstTopicId = (c.modules && c.modules[0] && c.modules[0].topics && c.modules[0].topics[0]) ? c.modules[0].topics[0].id : null;
      const firstModuleId = (c.modules && c.modules[0]) ? c.modules[0].id : null;

      return `
        <div class="rounded-[1.5rem] bg-card border border-border shadow-soft p-5 flex flex-col justify-between space-y-4 hover:shadow-soft-md transition">
          <div class="space-y-2">
            <div class="flex items-center justify-between gap-2">
              <span class="text-[10px] font-mono px-2.5 py-0.5 rounded-full border ${courseStyle.bg} font-medium">
                ${c.modules ? c.modules.length : 0} Modules
              </span>
              <span class="text-xs font-mono font-semibold text-ink">${pct}%</span>
            </div>
            <div>
              <h3 class="text-base font-semibold text-ink tracking-tight">${this.escapeHtml(c.name)}</h3>
              <p class="text-xs text-neutral-400 line-clamp-1 mt-0.5">${this.escapeHtml(c.description || `${totalLectures} comprehensive video lectures & notes`)}</p>
            </div>
          </div>

          <div class="space-y-2">
            <!-- Progress Bar -->
            <div class="w-full h-1.5 rounded-full bg-card-muted overflow-hidden">
              <div class="h-full bg-ink rounded-full transition-all duration-300" style="width: ${pct}%"></div>
            </div>
            <div class="flex items-center justify-between text-[11px] font-mono text-neutral-400">
              <span>${studiedCount} / ${totalLectures} studied</span>
              <span>${totalLectures - studiedCount} remaining</span>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="grid grid-cols-2 gap-2 pt-2 border-t border-border/60">
            <button onclick="App.launchCourseStudy('${firstTopicId}')" class="pill-muted text-xs py-1.5 px-3 flex items-center justify-center gap-1.5 font-medium">
              <i data-lucide="book-open" class="w-3.5 h-3.5"></i>
              <span>Study Studio</span>
            </button>
            <button onclick="App.launchCourseExam('${firstModuleId}')" class="px-3 py-1.5 rounded-full border border-border hover:bg-card-muted text-xs text-ink flex items-center justify-center gap-1.5 font-medium transition">
              <i data-lucide="award" class="w-3.5 h-3.5"></i>
              <span>Mock Quiz</span>
            </button>
          </div>
        </div>
      `;
    }).join('');

    const overallPct = totalDegreeLectures > 0 ? Math.round((totalDegreeStudied / totalDegreeLectures) * 100) : 0;
    if (overallProgressEl) {
      overallProgressEl.innerHTML = `Degree Progress: <span class="font-semibold text-ink">${overallPct}%</span> (${totalDegreeStudied}/${totalDegreeLectures} studied)`;
    }
  },

  launchCourseStudy(topicId) {
    this.switchView('notes');
    if (topicId) {
      this.loadTopicNotes(topicId);
    }
  },

  launchCourseExam(moduleId) {
    this.switchView('exam');
    if (moduleId) {
      const select = document.getElementById('exam-module-select');
      if (select) {
        select.value = moduleId;
        this.loadModuleExam(moduleId);
      }
    }
  },

  jumpToTopic(topicId) {
    this.switchView('notes');
    this.loadTopicNotes(topicId);
  },

  // -------------------------------------------------------------
  // Degree Study Checklist Controller
  // -------------------------------------------------------------
  filterChecklist(subject) {
    this.checklistFilter = subject;
    const pills = document.querySelectorAll('.checklist-filter-pill');
    pills.forEach(p => {
      if (p.getAttribute('data-filter') === subject) {
        p.className = 'checklist-filter-pill px-3 py-1 rounded-full text-xs font-medium bg-neutral-900 text-white dark:bg-white dark:text-neutral-900';
      } else {
        p.className = 'checklist-filter-pill px-3 py-1 rounded-full text-xs font-medium text-neutral-500 hover:text-ink bg-card-muted';
      }
    });
    this.renderChecklist();
  },

  renderChecklist() {
    const container = document.getElementById('checklist-items-container');
    const progressText = document.getElementById('checklist-progress-text');
    if (!container) return;

    const filtered = this.checklistItems.filter(item => {
      if (this.checklistFilter === 'all') return true;
      return item.subject === this.checklistFilter;
    });

    const completedTotal = this.checklistItems.filter(i => i.completed).length;
    if (progressText) {
      progressText.textContent = `${completedTotal} of ${this.checklistItems.length} completed`;
    }

    if (filtered.length === 0) {
      container.innerHTML = '<div class="py-6 text-center text-xs text-neutral-400">No tasks in this category. Add your goals above!</div>';
      return;
    }

    const subjectLabels = {
      'corporate-finance': 'Corporate Finance',
      'family-business': 'Family Business',
      'critical-thinking': 'Critical Thinking',
      'startup-dilemmas': 'Startup Dilemmas',
      'data-visualisation': 'Data Visualisation'
    };

    container.innerHTML = filtered.map(item => {
      const courseStyle = this.getCourseColor(subjectLabels[item.subject] || item.subject);
      return `
        <div class="flex items-center justify-between gap-3 py-2.5 group">
          <div class="flex items-center gap-3 min-w-0">
            <button onclick="App.toggleChecklistItem('${item.id}')" class="w-5 h-5 rounded-md border ${item.completed ? 'bg-ink border-ink text-canvas' : 'border-neutral-300 dark:border-neutral-700 bg-card'} flex items-center justify-center transition shrink-0">
              ${item.completed ? '<i data-lucide="check" class="w-3.5 h-3.5 stroke-[3]"></i>' : ''}
            </button>
            <span class="text-xs ${item.completed ? 'line-through text-neutral-400' : 'text-ink font-medium'} truncate">
              ${this.escapeHtml(item.text)}
            </span>
            <span class="text-[9px] font-mono px-2 py-0.5 rounded-full border ${courseStyle.bg} shrink-0 hidden sm:inline-block">
              ${subjectLabels[item.subject] || item.subject}
            </span>
          </div>
          <button onclick="App.deleteChecklistItem('${item.id}')" class="text-neutral-400 hover:text-rose-500 opacity-0 group-hover:opacity-100 transition p-1 shrink-0" title="Delete task">
            <i data-lucide="trash" class="w-3.5 h-3.5"></i>
          </button>
        </div>
      `;
    }).join('');

    if (window.lucide) window.lucide.createIcons();
  },

  toggleChecklistItem(id) {
    const item = this.checklistItems.find(i => i.id === id);
    if (item) {
      item.completed = !item.completed;
      this.saveChecklist();
      this.renderChecklist();
    }
  },

  addChecklistItem() {
    const input = document.getElementById('new-checklist-input');
    const select = document.getElementById('new-checklist-subject');
    if (!input || !input.value.trim()) return;

    const newTask = {
      id: 'task-' + Date.now(),
      text: input.value.trim(),
      subject: select ? select.value : 'corporate-finance',
      completed: false
    };

    this.checklistItems.unshift(newTask);
    this.saveChecklist();
    input.value = '';
    this.renderChecklist();
  },

  deleteChecklistItem(id) {
    this.checklistItems = this.checklistItems.filter(i => i.id !== id);
    this.saveChecklist();
    this.renderChecklist();
  },

  resetDefaultChecklist() {
    if (confirm('Reset to the default high-yield exam tasks?')) {
      this.checklistItems = this.getDefaultChecklist();
      this.saveChecklist();
      this.renderChecklist();
    }
  },

  saveChecklist() {
    localStorage.setItem('study_engine_checklist', JSON.stringify(this.checklistItems));
  },

  // -------------------------------------------------------------
  // Multi-Pane Active Study Studio Controller
  // -------------------------------------------------------------
  applyLayoutPreset(preset) {
    this.activePreset = preset;
    if (preset === 'lecture') {
      this.paneState = { video: true, notes: true, canvas: false, copilot: false };
    } else if (preset === 'studio') {
      this.paneState = { video: false, notes: true, canvas: true, copilot: false };
    } else if (preset === 'tutor') {
      this.paneState = { video: false, notes: true, canvas: false, copilot: true };
    } else if (preset === 'zen') {
      this.paneState = { video: false, notes: false, canvas: true, copilot: false };
    }

    const presetBtns = ['lecture', 'studio', 'tutor', 'zen'];
    presetBtns.forEach(p => {
      const btn = document.getElementById(`preset-${p}`);
      if (btn) {
        if (p === preset) {
          btn.className = 'px-2.5 py-1 rounded-full bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 font-medium transition shadow-soft-sm';
        } else {
          btn.className = 'px-2.5 py-1 rounded-full text-neutral-500 hover:text-ink transition';
        }
      }
    });

    this.updateStudioLayout();
  },

  togglePane(pane) {
    this.paneState[pane] = !this.paneState[pane];
    this.updateStudioLayout();
  },

  updateStudioLayout() {
    ['video', 'notes', 'canvas'].forEach(p => {
      const el = document.getElementById(`pane-${p}`);
      const btn = document.getElementById(`toggle-${p}-btn`);
      if (el) el.classList.toggle('hidden', !this.paneState[p]);
      if (btn) {
        if (this.paneState[p]) {
          btn.className = 'tool-toggle-pill px-2.5 py-1 rounded-lg border text-xs font-mono flex items-center gap-1.5 transition active font-semibold border-neutral-900 dark:border-white bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 shadow-soft-sm';
        } else {
          btn.className = 'tool-toggle-pill px-2.5 py-1 rounded-lg border text-xs font-mono flex items-center gap-1.5 transition border-border bg-card text-neutral-400 hover:text-ink';
        }
      }
    });

    const copilotEl = document.getElementById('copilot-panel');
    const copilotResizer = document.getElementById('resizer-copilot');
    const copilotBtn = document.getElementById('toggle-copilot-btn');
    if (copilotEl) copilotEl.classList.toggle('hidden', !this.paneState.copilot);
    if (copilotResizer) copilotResizer.classList.toggle('hidden', !this.paneState.copilot);
    if (copilotBtn) {
      if (this.paneState.copilot) {
        copilotBtn.className = 'tool-toggle-pill px-2.5 py-1 rounded-lg border text-xs font-mono flex items-center gap-1.5 transition active font-semibold border-neutral-900 dark:border-white bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 shadow-soft-sm';
      } else {
        copilotBtn.className = 'tool-toggle-pill px-2.5 py-1 rounded-lg border text-xs font-mono flex items-center gap-1.5 transition border-border bg-card text-neutral-400 hover:text-ink';
      }
    }
    this.isCopilotOpen = !!this.paneState.copilot;

    if (this.paneState.canvas) {
      this.renderCanvas();
    }
    if (window.lucide) window.lucide.createIcons();
  },

  loadTopicVideo(topic) {
    const iframe = document.getElementById('lecture-video-iframe');
    const placeholder = document.getElementById('video-placeholder');
    const placeholderTitle = document.getElementById('video-placeholder-title');
    const extLink = document.getElementById('video-external-link');
    if (!iframe) return;

    if (topic && topic.video_id) {
      const embedUrl = `https://www.youtube.com/embed/${topic.video_id}?enablejsapi=1&rel=0`;
      if (iframe.src !== embedUrl) {
        iframe.src = embedUrl;
      }
      iframe.classList.remove('hidden');
      if (placeholder) placeholder.classList.add('hidden');
      if (extLink) {
        extLink.href = topic.youtube_url || `https://www.youtube.com/watch?v=${topic.video_id}`;
        extLink.classList.remove('pointer-events-none', 'opacity-50');
      }
    } else {
      iframe.src = '';
      iframe.classList.add('hidden');
      if (placeholder) {
        placeholder.classList.remove('hidden');
        if (placeholderTitle) {
          placeholderTitle.textContent = topic ? topic.title : 'Select a lecture to play video';
        }
      }
      if (extLink) {
        extLink.href = '#';
        extLink.classList.add('pointer-events-none', 'opacity-50');
      }
    }
    if (window.lucide) window.lucide.createIcons();
  },

  setVideoSpeed(speed) {
    this.videoSpeed = speed;
    const iframe = document.getElementById('lecture-video-iframe');
    if (iframe && iframe.contentWindow) {
      iframe.contentWindow.postMessage(JSON.stringify({
        event: 'command',
        func: 'setPlaybackRate',
        args: [speed]
      }), '*');
    }
    const speedBtns = document.querySelectorAll('.speed-btn');
    speedBtns.forEach(btn => {
      const s = parseFloat(btn.getAttribute('data-speed'));
      if (s === speed) {
        btn.className = 'speed-btn px-1.5 py-0.5 rounded bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 font-semibold';
      } else {
        btn.className = 'speed-btn px-1.5 py-0.5 rounded bg-card-muted hover:bg-muted text-ink-secondary';
      }
    });
  },

  seekVideoToSeconds(seconds) {
    if (!this.paneState.video) {
      this.paneState.video = true;
      this.updateStudioLayout();
    }
    const iframe = document.getElementById('lecture-video-iframe');
    if (iframe && iframe.contentWindow) {
      iframe.contentWindow.postMessage(JSON.stringify({
        event: 'command',
        func: 'seekTo',
        args: [seconds, true]
      }), '*');
    }
  },

  // -------------------------------------------------------------
  // Option A Visual Card Canvas ("Ledger Board")
  // -------------------------------------------------------------
  initCanvasListeners() {
    document.addEventListener('mousemove', (e) => this.onCanvasMouseMove(e));
    document.addEventListener('mouseup', (e) => this.onCanvasMouseUp(e));

    const viewport = document.getElementById('canvas-viewport');
    if (viewport) {
      viewport.addEventListener('dblclick', (e) => {
        if (e.target.id === 'canvas-viewport' || e.target.id === 'canvas-cards-container' || e.target.tagName === 'svg') {
          const rect = viewport.getBoundingClientRect();
          const x = e.clientX - rect.left + viewport.scrollLeft;
          const y = e.clientY - rect.top + viewport.scrollTop;
          this.addCustomCanvasCardAt(x, y);
        }
      });
    }
  },

  async loadTopicCanvas(topicId) {
    let canvasData = null;

    // 1. Try local storage
    const saved = localStorage.getItem(`canvas_${topicId}`);
    if (saved) {
      try { canvasData = JSON.parse(saved); } catch (e) {}
    }

    // 2. Try window.STUDY_DATA static bundle
    if (!canvasData && window.STUDY_DATA && window.STUDY_DATA.canvases && window.STUDY_DATA.canvases[topicId]) {
      canvasData = window.STUDY_DATA.canvases[topicId];
    }

    // 3. Try backend API
    if (!canvasData) {
      try {
        const res = await fetch(`/api/topics/${topicId}/canvas`);
        if (res.ok) canvasData = await res.json();
      } catch (e) {}
    }

    this.currentTopicCanvas = (canvasData && canvasData.cards) ? canvasData : { cards: [], connections: [] };
    this.renderCanvas();
  },

  saveTopicCanvas(topicId) {
    if (!topicId) return;
    localStorage.setItem(`canvas_${topicId}`, JSON.stringify(this.currentTopicCanvas));
    fetch(`/api/topics/${topicId}/canvas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(this.currentTopicCanvas)
    }).catch(() => {});

    const counter = document.getElementById('canvas-card-counter');
    if (counter) {
      const len = this.currentTopicCanvas.cards.length;
      counter.textContent = `${len} ${len === 1 ? 'card' : 'cards'}`;
    }
  },

  renderCanvas() {
    const container = document.getElementById('canvas-cards-container');
    const svgLayer = document.getElementById('canvas-svg-layer');
    const counter = document.getElementById('canvas-card-counter');
    if (!container) return;

    const cards = this.currentTopicCanvas.cards || [];
    if (counter) {
      counter.textContent = `${cards.length} ${cards.length === 1 ? 'card' : 'cards'}`;
    }

    if (cards.length === 0) {
      container.innerHTML = `
        <div class="absolute inset-0 flex flex-col items-center justify-center text-center p-8 text-neutral-400 space-y-2 pointer-events-none">
          <div class="w-10 h-10 rounded-2xl bg-card border border-border shadow-soft flex items-center justify-center text-neutral-400">
            <i data-lucide="layout" class="w-5 h-5"></i>
          </div>
          <p class="text-xs font-medium text-ink">Personal Mindmap & Note Board</p>
          <p class="text-[11px] text-neutral-400 max-w-sm">
            Hover over any note heading or AI explanation to click <strong>[📌 Pin]</strong>, or double-click anywhere here to create your own formula and concept cards.
          </p>
        </div>
      `;
      if (svgLayer) svgLayer.innerHTML = `
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#a3a3a3"/>
          </marker>
        </defs>
      `;
      if (window.lucide) window.lucide.createIcons();
      return;
    }

    container.innerHTML = cards.map(c => {
      const isFormula = c.type === 'formula';
      const isCopilot = c.type === 'copilot';
      const badgeStyle = isFormula 
        ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20' 
        : isCopilot 
          ? 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20' 
          : 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20';

      const typeLabel = isFormula ? 'FORMULA' : isCopilot ? 'AI EXPLANATION' : 'NOTE';

      let parsedContent = c.content || '';
      if (window.marked) {
        try { parsedContent = marked.parse(parsedContent); } catch (e) {}
      }

      return `
        <div 
          id="card-el-${c.id}" 
          class="ledger-canvas-card bg-card border border-border shadow-soft rounded-2xl p-3.5 space-y-2 select-text" 
          style="left: ${c.x}px; top: ${c.y}px; width: ${c.width || 300}px;"
          data-id="${c.id}"
        >
          <!-- Card Header & Drag Handle -->
          <div class="flex items-center justify-between gap-2 pb-1.5 border-b border-border/60">
            <div class="flex items-center gap-1.5 cursor-grab active:cursor-grabbing handle-drag" onmousedown="App.onCardMouseDown(event, '${c.id}')">
              <i data-lucide="grip-vertical" class="w-3.5 h-3.5 text-neutral-400"></i>
              <span class="text-[9px] font-mono px-1.5 py-0.5 rounded border ${badgeStyle} font-medium">${typeLabel}</span>
            </div>
            <div class="flex items-center gap-1">
              <button onclick="App.startConnecting('${c.id}')" class="text-neutral-400 hover:text-ink p-1 rounded hover:bg-muted text-[10px]" title="Connect to another card with an arrow">
                <i data-lucide="git-commit" class="w-3 h-3"></i>
              </button>
              <button onclick="App.deleteCanvasCard('${c.id}')" class="text-neutral-400 hover:text-rose-500 p-1 rounded hover:bg-muted transition" title="Delete Card">
                <i data-lucide="x" class="w-3 h-3"></i>
              </button>
            </div>
          </div>

          <!-- Card Title -->
          <div class="text-xs font-semibold text-ink tracking-tight">${this.escapeHtml(c.title || 'Untitled Card')}</div>

          <!-- Card Content Body -->
          <div class="text-xs text-ink leading-relaxed prose-ledger max-h-60 overflow-y-auto pr-1">
            ${parsedContent}
          </div>
        </div>
      `;
    }).join('');

    // Render SVG connector arrows
    this.renderCanvasConnections();

    // Render KaTeX in cards
    if (window.renderMathInElement) {
      renderMathInElement(container, {
        delimiters: [
          {left: '$$', right: '$$', display: true},
          {left: '$', right: '$', display: false}
        ],
        throwOnError: false
      });
    }

    if (window.lucide) window.lucide.createIcons();
  },

  renderCanvasConnections() {
    const svgLayer = document.getElementById('canvas-svg-layer');
    if (!svgLayer) return;

    const connections = this.currentTopicCanvas.connections || [];
    let svgHtml = `
      <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#a3a3a3"/>
        </marker>
      </defs>
    `;

    connections.forEach(conn => {
      const fromEl = document.getElementById(`card-el-${conn.from}`);
      const toEl = document.getElementById(`card-el-${conn.to}`);
      if (!fromEl || !toEl) return;

      const fromX = fromEl.offsetLeft + fromEl.offsetWidth / 2;
      const fromY = fromEl.offsetTop + fromEl.offsetHeight / 2;
      const toX = toEl.offsetLeft + toEl.offsetWidth / 2;
      const toY = toEl.offsetTop + toEl.offsetHeight / 2;

      const dx = (toX - fromX) * 0.4;
      const pathData = `M ${fromX} ${fromY} C ${fromX + dx} ${fromY}, ${toX - dx} ${toY}, ${toX} ${toY}`;

      svgHtml += `<path d="${pathData}" fill="none" stroke="#a3a3a3" stroke-width="1.75" stroke-dasharray="4,4" marker-end="url(#arrow)"/>`;
    });

    svgLayer.innerHTML = svgHtml;
  },

  onCardMouseDown(e, cardId) {
    if (e.target.closest('button') || e.target.closest('input')) return;
    this.draggingCardId = cardId;
    const cardEl = document.getElementById(`card-el-${cardId}`);
    if (cardEl) {
      cardEl.classList.add('dragging');
      this.dragOffset = {
        x: e.clientX - cardEl.offsetLeft,
        y: e.clientY - cardEl.offsetTop
      };
    }
  },

  onCanvasMouseMove(e) {
    if (!this.draggingCardId) return;
    const cardEl = document.getElementById(`card-el-${this.draggingCardId}`);
    if (!cardEl) return;

    const newX = Math.max(10, e.clientX - this.dragOffset.x);
    const newY = Math.max(10, e.clientY - this.dragOffset.y);

    cardEl.style.left = `${newX}px`;
    cardEl.style.top = `${newY}px`;

    const card = this.currentTopicCanvas.cards.find(c => c.id === this.draggingCardId);
    if (card) {
      card.x = newX;
      card.y = newY;
    }

    this.renderCanvasConnections();
  },

  onCanvasMouseUp(e) {
    if (this.draggingCardId) {
      const cardEl = document.getElementById(`card-el-${this.draggingCardId}`);
      if (cardEl) cardEl.classList.remove('dragging');
      this.saveTopicCanvas(this.selectedTopicId);
      this.draggingCardId = null;
    }
  },

  startConnecting(fromCardId) {
    const toCardId = prompt('Enter target card title or keyword to connect with an arrow:');
    if (!toCardId) return;
    const target = this.currentTopicCanvas.cards.find(c => c.id === toCardId || (c.title && c.title.toLowerCase().includes(toCardId.toLowerCase())));
    if (target && target.id !== fromCardId) {
      if (!this.currentTopicCanvas.connections) this.currentTopicCanvas.connections = [];
      this.currentTopicCanvas.connections.push({ from: fromCardId, to: target.id });
      this.saveTopicCanvas(this.selectedTopicId);
      this.renderCanvas();
    }
  },

  addCustomCanvasCard() {
    this.addCustomCanvasCardAt(60 + (this.currentTopicCanvas.cards.length % 3) * 320, 60 + Math.floor(this.currentTopicCanvas.cards.length / 3) * 220);
  },

  addCustomCanvasCardAt(x, y) {
    const title = prompt('Card Title (e.g. Core Formula, Exam Trap, Personal Note):');
    if (!title) return;
    const content = prompt('Card Content (Markdown & math $...$ supported):') || '';

    const newCard = {
      id: 'card-' + Date.now(),
      title: title.trim(),
      content: content.trim(),
      type: title.toLowerCase().includes('formula') ? 'formula' : 'note',
      x: Math.round(x),
      y: Math.round(y),
      width: 300
    };

    this.currentTopicCanvas.cards.push(newCard);
    this.saveTopicCanvas(this.selectedTopicId);
    this.renderCanvas();
  },

  pinHeadingToCanvas(btn) {
    const parentHeading = btn.closest('h1, h2, h3, h4');
    let title = 'Key Insight';
    let content = '';

    if (parentHeading) {
      title = parentHeading.innerText.replace('Pin to Canvas', '').replace('✓ Pinned', '').trim();
      let next = parentHeading.nextElementSibling;
      while (next && !['H1', 'H2', 'H3', 'H4'].includes(next.tagName) && content.length < 350) {
        content += next.innerText + '\n';
        next = next.nextElementSibling;
      }
    }

    const cardsCount = this.currentTopicCanvas.cards.length;
    const card = {
      id: 'card-' + Date.now(),
      title: title,
      content: content.trim() || title,
      type: title.toLowerCase().includes('formula') ? 'formula' : 'note',
      x: 50 + (cardsCount % 3) * 320,
      y: 50 + Math.floor(cardsCount / 3) * 220,
      width: 300
    };

    this.currentTopicCanvas.cards.push(card);
    this.saveTopicCanvas(this.selectedTopicId);
    
    // Auto open canvas pane if closed
    if (!this.paneState.canvas) {
      this.paneState.canvas = true;
      this.updateStudioLayout();
    } else {
      this.renderCanvas();
    }

    btn.innerText = '✓ Pinned';
    setTimeout(() => { 
      btn.innerHTML = '<i data-lucide="pin" class="w-3 h-3 inline mr-1"></i>Pin to Canvas'; 
      if (window.lucide) window.lucide.createIcons(); 
    }, 1500);
  },

  pinChatToCanvas(msgIndex) {
    const msg = this.copilotMessages[msgIndex];
    if (!msg) return;

    const cardsCount = this.currentTopicCanvas.cards.length;
    const card = {
      id: 'card-' + Date.now(),
      title: 'AI Copilot Explanation',
      content: msg.content,
      type: 'copilot',
      x: 50 + (cardsCount % 3) * 320,
      y: 50 + Math.floor(cardsCount / 3) * 220,
      width: 310
    };

    this.currentTopicCanvas.cards.push(card);
    this.saveTopicCanvas(this.selectedTopicId);

    // Auto open canvas pane if closed
    if (!this.paneState.canvas) {
      this.paneState.canvas = true;
      this.updateStudioLayout();
    } else {
      this.renderCanvas();
    }

    alert('📌 Copilot explanation clipped to your visual canvas!');
  },

  deleteCanvasCard(cardId) {
    this.currentTopicCanvas.cards = this.currentTopicCanvas.cards.filter(c => c.id !== cardId);
    if (this.currentTopicCanvas.connections) {
      this.currentTopicCanvas.connections = this.currentTopicCanvas.connections.filter(c => c.from !== cardId && c.to !== cardId);
    }
    this.saveTopicCanvas(this.selectedTopicId);
    this.renderCanvas();
  },

  clearCurrentCanvas() {
    if (confirm('Clear all canvas cards for this lecture?')) {
      this.currentTopicCanvas = { cards: [], connections: [] };
      this.saveTopicCanvas(this.selectedTopicId);
      this.renderCanvas();
    }
  },

  // -------------------------------------------------------------
  // Navigation / Views
  // -------------------------------------------------------------
  switchView(viewName) {
    const target = (viewName === 'syllabus' || viewName === 'dashboard') ? 'dashboard' : viewName;
    this.currentView = target;

    const views = {
      dashboard: document.getElementById('view-dashboard'),
      notes: document.getElementById('view-notes'),
      exam: document.getElementById('view-exam')
    };

    const tabs = {
      dashboard: document.getElementById('tab-dashboard'),
      notes: document.getElementById('tab-notes'),
      exam: document.getElementById('tab-exam')
    };

    Object.keys(views).forEach(k => {
      const el = views[k];
      const tab = tabs[k];
      const isActive = (k === target);

      if (el) {
        if (isActive) {
          el.classList.remove('hidden');
          el.style.display = (k === 'notes') ? 'flex' : 'block';
        } else {
          el.classList.add('hidden');
          el.style.display = 'none';
        }
      }

      if (tab) {
        if (isActive) {
          tab.className = 'px-3.5 py-1.5 rounded-full bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900 font-medium text-xs transition shadow-soft-sm';
        } else {
          tab.className = 'px-3.5 py-1.5 rounded-full text-neutral-500 hover:text-neutral-900 dark:hover:text-white font-medium text-xs transition';
        }
      }
    });

    if (target === 'dashboard') {
      this.renderDashboard();
    } else if (target === 'notes') {
      this.updateStudioLayout();
      if (!this.selectedTopicId) {
        if (this.lastStudiedTopicId) {
          this.loadTopicNotes(this.lastStudiedTopicId);
        } else {
          this.autoSelectFirstCompletedTopic();
        }
      }
    } else if (target === 'exam') {
      this.setupExamView();
    }

    if (window.lucide) window.lucide.createIcons();
  },

  // -------------------------------------------------------------
  // Courses & Modules Data API
  // -------------------------------------------------------------
  async loadCourses() {
    if (window.STUDY_DATA && window.STUDY_DATA.courses && window.STUDY_DATA.courses.length > 0) {
      this.courses = window.STUDY_DATA.courses;
      this.renderDashboard();
      this.renderNotesSidebar();
    }
    try {
      const res = await fetch('/api/courses');
      if (res.ok) {
        this.courses = await res.json();
        this.renderDashboard();
        this.renderNotesSidebar();
      }
    } catch (e) {
      // Static mode (GitHub Pages) uses window.STUDY_DATA
    }
  },

  renderSyllabusView() {
    this.renderDashboard();
  },

  // -------------------------------------------------------------
  // Create Course Modal
  // -------------------------------------------------------------
  openCreateCourseModal() {
    document.getElementById('modal-create-course').classList.remove('hidden');
  },

  closeCreateCourseModal() {
    document.getElementById('modal-create-course').classList.add('hidden');
  },

  async submitCreateCourse() {
    if (this.isStaticHost()) {
      this.notifyStaticViewer("add new subjects");
      return;
    }
    const name = document.getElementById('new-course-name').value.trim();
    const desc = document.getElementById('new-course-desc').value.trim();
    const moduleCount = parseInt(document.querySelector('input[name="module-count"]:checked').value, 10);

    if (!name) {
      alert('Please enter a subject name');
      return;
    }

    try {
      await fetch('/api/courses', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description: desc, module_count: moduleCount })
      });
      this.closeCreateCourseModal();
      document.getElementById('new-course-name').value = '';
      document.getElementById('new-course-desc').value = '';
      await this.loadCourses();
    } catch (e) {
      alert('Failed to create course: ' + e);
    }
  },

  async deleteCourse(courseId) {
    if (this.isStaticHost()) {
      this.notifyStaticViewer("delete subjects");
      return;
    }
    if (!confirm('Are you sure you want to delete this course and all its module notes?')) return;
    try {
      await fetch(`/api/courses/${courseId}`, { method: 'DELETE' });
      await this.loadCourses();
    } catch (e) {
      alert('Failed to delete course: ' + e);
    }
  },

  // -------------------------------------------------------------
  // Batch Video Ingestion Modal
  // -------------------------------------------------------------
  openIngestModal(courseId, moduleId, moduleTitle) {
    this.selectedCourseId = courseId;
    this.selectedModuleId = moduleId;
    document.getElementById('ingest-module-title').textContent = moduleTitle;
    document.getElementById('ingest-urls-textarea').value = '';
    document.getElementById('modal-ingest').classList.remove('hidden');
    this.renderModuleTopicsList(moduleId);
  },

  closeIngestModal() {
    document.getElementById('modal-ingest').classList.add('hidden');
  },

  async submitIngest() {
    const text = document.getElementById('ingest-urls-textarea').value.trim();
    const extractSlides = document.getElementById('ingest-extract-slides').checked;

    if (!text) {
      alert('Please paste at least one YouTube video URL or playlist link.');
      return;
    }

    const btn = document.getElementById('btn-start-curation');
    btn.disabled = true;
    btn.innerHTML = `<span class="animate-spin inline-block mr-1">↻</span> Starting Ingestion...`;

    try {
      if (window.location.hostname.includes('github.io')) {
        alert(
          "⚠️ Static Host Notice:\n\n" +
          "You are on the static GitHub Pages viewer (gupta-garv.github.io).\n\n" +
          "GitHub Pages only hosts static files and cannot run the Python video processor, Whisper AI, or FFmpeg OCR.\n\n" +
          "To curate new lecture videos, please open http://127.0.0.1:8000 on your Mac where your local Python engine is running. Once curated, the notes will sync here automatically!"
        );
        return;
      }

      const res = await fetch(`/api/modules/${this.selectedModuleId}/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ urls_text: text, extract_slides: extractSlides })
      });
      if (!res.ok) {
        const errText = await res.text();
        throw new Error(`Server returned HTTP ${res.status}: ${errText.slice(0, 150)}`);
      }
      const data = await res.json();
      document.getElementById('ingest-urls-textarea').value = '';
      alert(`Queued ${data.added_count} videos for processing! Curation will run on the spot in the background.`);
      await this.loadCourses();
      this.renderModuleTopicsList(this.selectedModuleId);
    } catch (e) {
      alert('Ingestion error: ' + e);
    } finally {
      btn.disabled = false;
      btn.innerHTML = 'Curate Notes & Questions On The Spot';
    }
  },

  renderModuleTopicsList(moduleId) {
    const listEl = document.getElementById('module-topics-status-list');
    if (!listEl) return;

    let topics = [];
    for (const c of this.courses) {
      for (const m of c.modules) {
        if (m.id === moduleId) {
          topics = m.topics;
          break;
        }
      }
    }

    if (topics.length === 0) {
      listEl.innerHTML = '<div class="text-xs text-neutral-400 py-3 text-center">No videos uploaded in this module yet.</div>';
      return;
    }

    listEl.innerHTML = topics.map(t => {
      let statusBadge = '';
      if (t.status === 'completed') {
        statusBadge = '<span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-400 font-semibold">Completed</span>';
      } else if (t.status === 'processing') {
        statusBadge = '<span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-400 animate-pulse font-semibold">Curating...</span>';
      } else if (t.status === 'error') {
        statusBadge = `<button onclick="App.retryTopic('${t.id}')" class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-rose-100 dark:bg-rose-950 text-rose-700 dark:text-rose-400 font-semibold hover:underline">Retry</button>`;
      } else {
        statusBadge = '<span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-500 font-semibold">Pending</span>';
      }

      return `
        <div class="flex items-center justify-between p-2.5 rounded-xl bg-card border border-neutral-200 dark:border-neutral-800 text-xs">
          <div class="flex items-center gap-2 truncate pr-2">
            <i data-lucide="video" class="w-3.5 h-3.5 text-neutral-400 shrink-0"></i>
            <span class="truncate font-medium">${t.title}</span>
          </div>
          ${statusBadge}
        </div>
      `;
    }).join('');

    if (window.lucide) window.lucide.createIcons();
  },

  async retryTopic(topicId) {
    if (this.isStaticHost()) {
      this.notifyStaticViewer("retry curation");
      return;
    }
    try {
      await fetch(`/api/topics/${topicId}/retry`, { method: 'POST' });
      await this.loadCourses();
      this.renderModuleTopicsList(this.selectedModuleId);
    } catch (e) {
      alert('Retry error: ' + e);
    }
  },

  async recurateModule() {
    if (this.isStaticHost()) {
      this.notifyStaticViewer("re-curate module notes");
      return;
    }
    if (!this.selectedModuleId) return;
    try {
      await fetch(`/api/modules/${this.selectedModuleId}/recurate`, { method: 'POST' });
      await this.loadCourses();
      this.renderModuleTopicsList(this.selectedModuleId);
    } catch (e) {
      alert('Re-curation error: ' + e);
    }
  },

  // Auto-polling for active background curation
  startPolling() {
    setInterval(async () => {
      let hasActive = false;
      for (const c of this.courses) {
        for (const m of c.modules) {
          if (m.topics.some(t => t.status === 'processing' || t.status === 'pending')) {
            hasActive = true;
            break;
          }
        }
      }
      if (hasActive) {
        await this.loadCourses();
        if (this.selectedModuleId) {
          this.renderModuleTopicsList(this.selectedModuleId);
        }
      }
    }, 4000);
  },

  // -------------------------------------------------------------
  // Study Hall / Notes Reader & Collapsible Accordion
  // -------------------------------------------------------------
  toggleModule(moduleId) {
    if (this.expandedModuleIds.has(moduleId)) {
      this.expandedModuleIds.delete(moduleId);
    } else {
      this.expandedModuleIds.add(moduleId);
    }
    this.renderNotesSidebar();
  },

  toggleAllModules() {
    const allModuleIds = [];
    for (const c of this.courses) {
      for (const m of c.modules) allModuleIds.push(m.id);
    }
    const allOpen = allModuleIds.length > 0 && allModuleIds.every(id => this.expandedModuleIds.has(id));
    if (allOpen) {
      this.expandedModuleIds.clear();
    } else {
      for (const id of allModuleIds) this.expandedModuleIds.add(id);
    }
    this.renderNotesSidebar();
  },

  // -------------------------------------------------------------
  // Resizable Panes & Sidebar / Copilot Toggles
  // -------------------------------------------------------------
  initResizers() {
    const sidebar = document.getElementById('notes-sidebar');
    const resizerSidebar = document.getElementById('resizer-sidebar');
    const copilot = document.getElementById('copilot-panel');
    const resizerCopilot = document.getElementById('resizer-copilot');
    const viewNotes = document.getElementById('view-notes');

    // 1. Restore saved pane widths
    const savedSidebarWidth = localStorage.getItem('study_engine_sidebar_width');
    if (savedSidebarWidth && sidebar) {
      sidebar.style.width = savedSidebarWidth;
    }
    const savedCopilotWidth = localStorage.getItem('study_engine_copilot_width');
    if (savedCopilotWidth && copilot) {
      copilot.style.width = savedCopilotWidth;
    }

    // 2. Restore collapse states
    if (localStorage.getItem('study_engine_sidebar_open') === 'false') {
      this.isSidebarOpen = false;
      if (sidebar) sidebar.classList.add('hidden');
      if (resizerSidebar) resizerSidebar.classList.add('hidden');
      const toggleText = document.getElementById('sidebar-toggle-text');
      if (toggleText) toggleText.textContent = 'Show Syllabus';
    }
    if (localStorage.getItem('study_engine_copilot_open') === 'false') {
      this.isCopilotOpen = false;
      if (copilot) copilot.classList.add('hidden');
      if (resizerCopilot) resizerCopilot.classList.add('hidden');
      const label = document.getElementById('copilot-toggle-label');
      if (label) label.textContent = 'Open Copilot';
    }

    // 3. Syllabus Sidebar Drag-to-Resize
    if (resizerSidebar && sidebar && viewNotes) {
      let isDragging = false;

      const onMouseDown = (e) => {
        isDragging = true;
        e.preventDefault();
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
        resizerSidebar.classList.add('resizer-active');
        sidebar.style.transition = 'none';
        window.addEventListener('mousemove', onMouseMove);
        window.addEventListener('mouseup', onMouseUp);
      };

      const onMouseMove = (e) => {
        if (!isDragging) return;
        const rect = viewNotes.getBoundingClientRect();
        let newWidth = e.clientX - rect.left;
        if (newWidth < 170) newWidth = 170;
        if (newWidth > 480) newWidth = 480;
        sidebar.style.width = `${newWidth}px`;
      };

      const onMouseUp = () => {
        if (!isDragging) return;
        isDragging = false;
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        resizerSidebar.classList.remove('resizer-active');
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);
        localStorage.setItem('study_engine_sidebar_width', sidebar.style.width);
      };

      resizerSidebar.addEventListener('mousedown', onMouseDown);
    }

    // 4. Lecture Copilot Drag-to-Resize
    if (resizerCopilot && copilot && viewNotes) {
      let isDragging = false;

      const onMouseDown = (e) => {
        isDragging = true;
        e.preventDefault();
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
        resizerCopilot.classList.add('resizer-active');
        copilot.style.transition = 'none';
        window.addEventListener('mousemove', onMouseMove);
        window.addEventListener('mouseup', onMouseUp);
      };

      const onMouseMove = (e) => {
        if (!isDragging) return;
        const rect = viewNotes.getBoundingClientRect();
        let newWidth = rect.right - e.clientX;
        if (newWidth < 260) newWidth = 260;
        if (newWidth > 600) newWidth = 600;
        copilot.style.width = `${newWidth}px`;
      };

      const onMouseUp = () => {
        if (!isDragging) return;
        isDragging = false;
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        resizerCopilot.classList.remove('resizer-active');
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);
        localStorage.setItem('study_engine_copilot_width', copilot.style.width);
      };

      resizerCopilot.addEventListener('mousedown', onMouseDown);
    }
  },

  toggleSidebar() {
    const sidebar = document.getElementById('notes-sidebar');
    const resizer = document.getElementById('resizer-sidebar');
    const toggleText = document.getElementById('sidebar-toggle-text');
    if (!sidebar) return;
    this.isSidebarOpen = !this.isSidebarOpen;
    if (this.isSidebarOpen) {
      sidebar.classList.remove('hidden');
      if (resizer) resizer.classList.remove('hidden');
      if (toggleText) toggleText.textContent = 'Syllabus';
    } else {
      sidebar.classList.add('hidden');
      if (resizer) resizer.classList.add('hidden');
      if (toggleText) toggleText.textContent = 'Show Syllabus';
    }
    localStorage.setItem('study_engine_sidebar_open', this.isSidebarOpen ? 'true' : 'false');
    if (window.lucide) window.lucide.createIcons();
  },

  toggleCopilot() {
    this.paneState.copilot = !this.paneState.copilot;
    this.updateStudioLayout();
    localStorage.setItem('study_engine_copilot_open', this.paneState.copilot ? 'true' : 'false');
  },

  renderNotesSidebar() {
    const tree = document.getElementById('notes-syllabus-tree');
    if (!tree) return;

    if (this.courses.length === 0) {
      tree.innerHTML = '<div class="text-xs text-neutral-400 p-4">Add courses in Syllabus first.</div>';
      return;
    }

    // Default expand the first module that has topics if none is expanded
    if (this.expandedModuleIds.size === 0) {
      for (const c of this.courses) {
        for (const m of c.modules) {
          if (m.topics && m.topics.length > 0) {
            this.expandedModuleIds.add(m.id);
            break;
          }
        }
        if (this.expandedModuleIds.size > 0) break;
      }
    }

    tree.innerHTML = this.courses.map(c => `
      <div class="space-y-2">
        <div class="flex items-center justify-between px-1">
          <span class="text-[11px] font-mono uppercase tracking-wider text-neutral-500 dark:text-neutral-400 font-semibold truncate">${c.name}</span>
          <span class="text-[10px] font-mono text-neutral-400">${c.modules.length} Mods</span>
        </div>
        <div class="space-y-1.5">
          ${c.modules.map(m => {
            const isExpanded = this.expandedModuleIds.has(m.id);
            const hasActiveTopic = m.topics.some(t => t.id === this.selectedTopicId);
            return `
              <div class="rounded-xl border ${hasActiveTopic ? 'border-neutral-900/40 dark:border-white/40' : 'border-border'} overflow-hidden bg-card transition shadow-soft-sm">
                <!-- Module Header Accordion Trigger -->
                <button onclick="App.toggleModule('${m.id}')" title="${m.name}" class="w-full px-3 py-2 flex items-center justify-between text-left hover:bg-muted/50 transition">
                  <div class="flex items-center gap-2 min-w-0">
                    <i data-lucide="${isExpanded ? 'chevron-down' : 'chevron-right'}" class="w-3.5 h-3.5 text-neutral-400 shrink-0"></i>
                    <span class="text-xs font-medium text-foreground truncate">${m.name}</span>
                  </div>
                  <span class="text-[10px] font-mono px-1.5 py-0.5 rounded-full bg-muted text-neutral-500 shrink-0">${m.topics.length}</span>
                </button>

                <!-- Collapsible Topic List -->
                ${isExpanded ? `
                  <div class="p-1.5 space-y-0.5 border-t border-border/60 bg-muted/20">
                    ${m.topics.length === 0 ? '<div class="text-[11px] text-neutral-400 px-2 py-1">No lectures uploaded</div>' : ''}
                    ${m.topics.map(t => {
                      const isSelected = t.id === this.selectedTopicId;
                      return `
                        <button onclick="App.loadTopicNotes('${t.id}')" title="${t.title}" class="w-full text-left text-xs px-2.5 py-1.5 rounded-lg flex items-center justify-between gap-2 transition ${
                          isSelected 
                            ? 'bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 font-medium shadow-soft-sm' 
                            : 'text-neutral-600 dark:text-neutral-400 hover:bg-muted'
                        }">
                          <span class="truncate">${t.title}</span>
                          <span class="w-1.5 h-1.5 rounded-full shrink-0 ${t.status === 'completed' ? (isSelected ? 'bg-emerald-400' : 'bg-emerald-500') : 'bg-neutral-300 dark:bg-neutral-700'}"></span>
                        </button>
                      `;
                    }).join('')}
                  </div>
                ` : ''}
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `).join('');

    if (window.lucide) window.lucide.createIcons();
  },

  autoSelectFirstCompletedTopic() {
    for (const c of this.courses) {
      for (const m of c.modules) {
        for (const t of m.topics) {
          if (t.status === 'completed') {
            this.loadTopicNotes(t.id);
            return;
          }
        }
      }
    }
  },

  async loadTopicNotes(topicId) {
    this.selectedTopicId = topicId;
    this.lastStudiedTopicId = topicId;
    localStorage.setItem('study_engine_last_studied_topic', topicId);
    this.studiedTopicIds.add(topicId);
    localStorage.setItem('study_engine_studied_topics', JSON.stringify([...this.studiedTopicIds]));

    // Auto-expand module containing this topic
    for (const c of this.courses) {
      for (const m of c.modules) {
        if (m.topics.some(t => t.id === topicId)) {
          this.expandedModuleIds.add(m.id);
          break;
        }
      }
    }

    this.renderNotesSidebar();
    this.loadTopicChat(topicId);
    this.loadTopicCanvas(topicId);

    const contentEl = document.getElementById('notes-content-body');
    contentEl.innerHTML = '<div class="text-center py-20 text-xs text-neutral-400">Loading synthesized notes...</div>';

    try {
      let data = null;
      if (window.STUDY_DATA && window.STUDY_DATA.topics && window.STUDY_DATA.topics[topicId]) {
        data = window.STUDY_DATA.topics[topicId];
      }
      try {
        const res = await fetch(`/api/topics/${topicId}`);
        if (res.ok) data = await res.json();
      } catch (err) {}

      if (!data) {
        contentEl.innerHTML = '<div class="p-8 text-center text-xs text-neutral-400">Lecture notes not found.</div>';
        return;
      }

      // Load Video Player in Studio
      this.loadTopicVideo(data);

      if (data.status !== 'completed') {
        contentEl.innerHTML = `
          <div class="p-8 text-center rounded-2xl bg-card border border-neutral-200 dark:border-neutral-800 shadow-soft space-y-2">
            <h3 class="font-medium text-sm">Notes are ${data.status}</h3>
            <p class="text-xs text-neutral-500">${data.error_message || 'This lecture is currently queued or being curated. Check back in a moment.'}</p>
          </div>
        `;
        return;
      }

      contentEl.innerHTML = marked.parse(data.notes_markdown || '# No notes synthesized.');

      // Inject pin-to-canvas buttons on headings
      contentEl.querySelectorAll('h2, h3').forEach(h => {
        h.classList.add('group', 'flex', 'items-center', 'justify-between', 'gap-2');
        const pinBtn = document.createElement('button');
        pinBtn.className = 'pin-note-btn text-[10px] font-mono px-2 py-0.5 rounded bg-muted hover:bg-ink hover:text-canvas text-neutral-400 transition shrink-0';
        pinBtn.innerHTML = '<i data-lucide="pin" class="w-3 h-3 inline mr-1"></i>Pin to Canvas';
        pinBtn.onclick = (e) => { e.stopPropagation(); App.pinHeadingToCanvas(pinBtn); };
        h.appendChild(pinBtn);
      });

      // Inject clickable timestamp jump buttons
      contentEl.querySelectorAll('p, li, td').forEach(el => {
        el.innerHTML = el.innerHTML.replace(/\b(\d{1,2}:\d{2})\b/g, (match, ts) => {
          const parts = ts.split(':');
          const secs = parseInt(parts[0], 10) * 60 + parseInt(parts[1], 10);
          return `<span class="timestamp-jump-btn" onclick="App.seekVideoToSeconds(${secs})" title="Jump video to ${ts}"><i data-lucide="play" class="w-2.5 h-2.5 fill-current"></i>${ts}</span>`;
        });
      });

      // KaTeX
      if (window.renderMathInElement) {
        renderMathInElement(contentEl, {
          delimiters: [
            {left: '$$', right: '$$', display: true},
            {left: '$', right: '$', display: false}
          ],
          throwOnError: false
        });
      }

      // Mermaid
      const mermaidBlocks = contentEl.querySelectorAll('.language-mermaid');
      mermaidBlocks.forEach(block => {
        const div = document.createElement('div');
        div.className = 'mermaid my-6 p-4 rounded-xl bg-card border border-neutral-200 dark:border-neutral-800 text-center overflow-x-auto';
        div.textContent = block.textContent;
        block.parentElement.replaceWith(div);
      });
      if (mermaidBlocks.length > 0 && window.mermaid) {
        mermaid.run();
      }

      // Render slide frames
      const slideGallery = document.getElementById('notes-slide-gallery');
      const slideThumbs = document.getElementById('slide-thumbs-container');
      if (data.slides && data.slides.length > 0) {
        slideGallery.classList.remove('hidden');
        slideThumbs.innerHTML = data.slides.map(s => `
          <div class="rounded-xl overflow-hidden border border-neutral-200 dark:border-neutral-800 bg-neutral-900 aspect-video">
            <img src="${s.url}" alt="${s.filename}" class="w-full h-full object-cover">
          </div>
        `).join('');
      } else {
        slideGallery.classList.add('hidden');
      }

    } catch (e) {
      contentEl.innerHTML = `<div class="text-rose-500 text-xs">Error loading notes: ${e}</div>`;
    }
  },

  // -------------------------------------------------------------
  // In-Context AI Lecture Copilot (Per-Video Persistent History)
  // -------------------------------------------------------------
  async loadTopicChat(topicId) {
    const topic = this.getTopicById(topicId);
    const activeLabel = document.getElementById('copilot-active-topic');
    if (activeLabel) {
      activeLabel.textContent = topic ? topic.title : 'No lecture selected';
    }

    const badge = document.getElementById('reader-topic-badge');
    if (badge) {
      badge.textContent = topic ? topic.title : 'Ready';
      badge.title = topic ? topic.title : '';
    }

    const container = document.getElementById('copilot-messages');
    if (!container) return;

    container.innerHTML = '<div class="text-center py-10 text-xs text-neutral-400">Loading saved doubts for this lecture...</div>';

    // 1. Fetch from SQLite database
    let messages = [];
    try {
      const res = await fetch(`/api/topics/${topicId}/chat`);
      if (res.ok) {
        messages = await res.json();
      }
    } catch (err) {}

    // 2. Fallback to STUDY_DATA bundle or localStorage (GitHub Pages / offline support)
    if ((!messages || messages.length === 0) && window.STUDY_DATA && window.STUDY_DATA.chats && window.STUDY_DATA.chats[topicId]) {
      messages = window.STUDY_DATA.chats[topicId];
    }
    if (!messages || messages.length === 0) {
      const saved = localStorage.getItem(`copilot_chat_${topicId}`);
      if (saved) {
        try { messages = JSON.parse(saved); } catch (e) {}
      }
    }

    this.copilotMessages = messages || [];
    this.renderCopilotMessages();
  },

  renderCopilotMessages() {
    const container = document.getElementById('copilot-messages');
    if (!container) return;

    const topic = this.getTopicById(this.selectedTopicId);
    const topicTitle = topic ? topic.title : 'this lecture';

    if (this.copilotMessages.length === 0) {
      container.innerHTML = `
        <div class="text-center py-12 text-neutral-400 space-y-2">
          <div class="w-8 h-8 rounded-full bg-muted mx-auto flex items-center justify-center text-neutral-400">
            <i data-lucide="sparkles" class="w-4 h-4"></i>
          </div>
          <p class="font-medium text-ink">Lecture AI Copilot</p>
          <p class="text-[11px] text-ink-secondary max-w-[220px] mx-auto">
            I am reading <strong>${topicTitle}</strong> with you. Ask any doubts about this video's concepts, formulas, or tricky exam traps!
          </p>
        </div>
      `;
      if (window.lucide) window.lucide.createIcons();
      return;
    }

    container.innerHTML = this.copilotMessages.map((m, idx) => {
      const isUser = m.role === 'user';
      let formattedContent = m.content;
      if (!isUser && window.marked) {
        try {
          formattedContent = window.marked.parse(m.content);
        } catch (e) {}
      }
      return `
        <div class="flex flex-col ${isUser ? 'items-end' : 'items-start'} space-y-1">
          <span class="text-[9px] font-mono text-ink-muted uppercase">${isUser ? 'You' : 'AI Copilot (GLM)'}</span>
          <div class="max-w-[90%] rounded-2xl px-3.5 py-2.5 text-xs shadow-soft-sm ${
            isUser 
              ? 'bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 rounded-br-sm' 
              : 'bg-card border border-border text-foreground rounded-bl-sm prose-ledger'
          }">
            ${formattedContent}
          </div>
          ${!isUser ? `
            <button onclick="App.pinChatToCanvas(${idx})" class="text-[10px] font-mono text-neutral-400 hover:text-ink flex items-center gap-1 transition px-1" title="Pin AI explanation to your personal canvas">
              <i data-lucide="pin" class="w-3 h-3"></i>
              <span>Pin to Canvas</span>
            </button>
          ` : ''}
        </div>
      `;
    }).join('');

    // Render KaTeX in Copilot responses
    if (window.renderMathInElement) {
      window.renderMathInElement(container, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "$", right: "$", display: false }
        ],
        throwOnError: false
      });
    }

    container.scrollTop = container.scrollHeight;
    if (window.lucide) window.lucide.createIcons();
  },

  async handleCopilotSubmit(e) {
    if (e) e.preventDefault();
    if (!this.selectedTopicId) {
      alert("Please select a lecture first to ask doubts in context.");
      return;
    }

    const input = document.getElementById('copilot-input');
    const question = input ? input.value.trim() : '';
    if (!question || this.isCopilotLoading) return;

    input.value = '';

    // Add user message to UI immediately
    const userMsg = { role: 'user', content: question, created_at: new Date().toISOString() };
    this.copilotMessages.push(userMsg);
    this.renderCopilotMessages();

    // Show typing indicator
    const container = document.getElementById('copilot-messages');
    const typingId = 'copilot-typing-indicator';
    container.insertAdjacentHTML('beforeend', `
      <div id="${typingId}" class="flex flex-col items-start space-y-1">
        <span class="text-[9px] font-mono text-ink-muted uppercase">AI Copilot</span>
        <div class="rounded-2xl px-3 py-2 text-xs bg-card border border-border text-ink-muted flex items-center gap-1.5 rounded-bl-sm">
          <span class="w-1.5 h-1.5 rounded-full bg-neutral-400 animate-pulse"></span>
          <span class="w-1.5 h-1.5 rounded-full bg-neutral-400 animate-pulse delay-75"></span>
          <span class="w-1.5 h-1.5 rounded-full bg-neutral-400 animate-pulse delay-150"></span>
          <span class="text-[11px] ml-1">Analyzing lecture context...</span>
        </div>
      </div>
    `);
    container.scrollTop = container.scrollHeight;

    this.isCopilotLoading = true;
    const sendBtn = document.getElementById('copilot-send-btn');
    if (sendBtn) sendBtn.disabled = true;

    try {
      let replyText = "";
      if (this.isStaticHost()) {
        replyText = "💡 Notice: You are viewing on GitHub Pages. For live AI answers with your GLM-5.3 Flash & Nemotron API, open http://127.0.0.1:8000 on your Mac where your local Python engine is running!";
      } else {
        const res = await fetch(`/api/topics/${this.selectedTopicId}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: question })
        });
        const data = await res.json();
        replyText = data.reply || "No response received.";
      }

      const typingEl = document.getElementById(typingId);
      if (typingEl) typingEl.remove();

      const assistantMsg = { role: 'assistant', content: replyText, created_at: new Date().toISOString() };
      this.copilotMessages.push(assistantMsg);

      // Save to localStorage for instant client persistence
      localStorage.setItem(`copilot_chat_${this.selectedTopicId}`, JSON.stringify(this.copilotMessages));

      this.renderCopilotMessages();
    } catch (err) {
      const typingEl = document.getElementById(typingId);
      if (typingEl) typingEl.remove();
      this.copilotMessages.push({ role: 'assistant', content: `Error: ${err.message}` });
      this.renderCopilotMessages();
    } finally {
      this.isCopilotLoading = false;
      if (sendBtn) sendBtn.disabled = false;
    }
  },

  askSuggestedQuestion(q) {
    const input = document.getElementById('copilot-input');
    if (input) {
      input.value = q;
      this.handleCopilotSubmit();
    }
  },

  clearTopicChat() {
    if (!this.selectedTopicId) return;
    if (confirm("Reset chat history for this specific lecture?")) {
      this.copilotMessages = [];
      localStorage.removeItem(`copilot_chat_${this.selectedTopicId}`);
      this.renderCopilotMessages();
    }
  },

  getTopicById(topicId) {
    for (const c of this.courses) {
      for (const m of c.modules) {
        for (const t of m.topics) {
          if (t.id === topicId) return t;
        }
      }
    }
    return null;
  },

  // -------------------------------------------------------------
  // Exam Arena
  // -------------------------------------------------------------
  setupExamView() {
    const select = document.getElementById('exam-module-select');
    if (!select) return;

    const options = [];
    this.courses.forEach(c => {
      c.modules.forEach(m => {
        options.push(`<option value="${m.id}">${c.name} - Module ${m.number}: ${m.name}</option>`);
      });
    });

    select.innerHTML = options.length ? options.join('') : '<option value="">No modules available</option>';
  },

  async startExam() {
    const moduleId = document.getElementById('exam-module-select').value;
    if (!moduleId) {
      alert('Please select a module.');
      return;
    }

    try {
      let examData = null;
      if (window.STUDY_DATA && window.STUDY_DATA.exams && window.STUDY_DATA.exams[moduleId]) {
        examData = window.STUDY_DATA.exams[moduleId];
      }
      try {
        const res = await fetch(`/api/modules/${moduleId}/exam`);
        if (res.ok) examData = await res.json();
      } catch (err) {}

      if (!examData || !examData.mcqs || examData.mcqs.length === 0) {
        alert('No MCQs available in this module yet. Add videos and curate notes first!');
        return;
      }

      this.examQuestions = examData.mcqs;
      this.subjectiveQuestions = examData.subjective_questions || [];
      this.currentQuestionIdx = 0;
      this.userAnswers = {};

      document.getElementById('exam-setup-box').classList.add('hidden');
      document.getElementById('exam-runner-box').classList.remove('hidden');
      this.loadExamQuestion(0);
    } catch (e) {
      alert('Failed to load exam: ' + e);
    }
  },

  loadExamQuestion(index) {
    this.currentQuestionIdx = index;
    const q = this.examQuestions[index];
    if (!q) return;

    document.getElementById('exam-q-counter').textContent = `Question ${index + 1} of ${this.examQuestions.length}`;
    document.getElementById('exam-q-text').textContent = q.question;

    const optContainer = document.getElementById('exam-q-options');
    optContainer.innerHTML = q.options.map((opt, optIdx) => `
      <button onclick="App.selectExamOption(${optIdx})" class="w-full text-left p-3.5 rounded-xl border text-xs sm:text-sm font-medium transition flex items-center justify-between gap-3 ${
        this.userAnswers[index] === optIdx ? 'border-neutral-900 bg-neutral-100 dark:border-white dark:bg-neutral-800 font-semibold' : 'border-neutral-200 dark:border-neutral-800 hover:bg-neutral-50 dark:hover:bg-neutral-900'
      }">
        <span>${opt}</span>
        <span class="w-4 h-4 rounded-full border ${this.userAnswers[index] === optIdx ? 'bg-neutral-900 dark:bg-white' : ''}"></span>
      </button>
    `).join('');
  },

  selectExamOption(optIdx) {
    this.userAnswers[this.currentQuestionIdx] = optIdx;
    this.loadExamQuestion(this.currentQuestionIdx);
  },

  nextExamQuestion() {
    if (this.currentQuestionIdx < this.examQuestions.length - 1) {
      this.loadExamQuestion(this.currentQuestionIdx + 1);
    }
  },

  prevExamQuestion() {
    if (this.currentQuestionIdx > 0) {
      this.loadExamQuestion(this.currentQuestionIdx - 1);
    }
  },

  finishExam() {
    let correct = 0;
    let wrong = 0;
    this.examQuestions.forEach((q, idx) => {
      const u = this.userAnswers[idx];
      if (u !== undefined) {
        if (u === q.correct_index) correct++;
        else wrong++;
      }
    });

    const score = Math.max(0, correct - (wrong * 0.25));
    alert(`Exam Finished!\nScore: ${score.toFixed(2)} / ${this.examQuestions.length}\nCorrect: ${correct}\nWrong: ${wrong}`);
    document.getElementById('exam-runner-box').classList.add('hidden');
    document.getElementById('exam-setup-box').classList.remove('hidden');
  },

  // -------------------------------------------------------------
  // Flashcards View
  // -------------------------------------------------------------
  setupFlashcardsView() {
    let allCards = [];
    this.courses.forEach(c => {
      c.modules.forEach(m => {
        m.topics.forEach(t => {
          // Can gather flashcards
        });
      });
    });
  },

  // -------------------------------------------------------------
  // Settings
  // -------------------------------------------------------------
};

window.App = App;

window.addEventListener('DOMContentLoaded', () => {
  App.init();
});

