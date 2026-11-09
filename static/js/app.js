/**
 * StudyEngine Frontend Application Controller
 * Handles Subjects, Modules, Batch Ingestion, Live Curation, Notes Reader, and Exam Arena.
 */

const App = {
  currentView: 'syllabus',
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
    await this.loadCourses();
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
  // Navigation / Views
  // -------------------------------------------------------------
  switchView(viewName) {
    this.currentView = viewName;
    ['syllabus', 'notes', 'exam', 'flashcards'].forEach(v => {
      const el = document.getElementById(`view-${v}`);
      const tab = document.getElementById(`tab-${v}`);
      if (el) el.classList.toggle('hidden', v !== viewName);
      if (tab) {
        if (v === viewName) {
          tab.className = 'px-3 py-1.5 rounded-full bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900 font-medium text-xs transition';
        } else {
          tab.className = 'px-3 py-1.5 rounded-full text-neutral-500 hover:text-neutral-900 dark:hover:text-white font-medium text-xs transition';
        }
      }
    });

    if (viewName === 'notes' && !this.selectedTopicId) {
      this.autoSelectFirstCompletedTopic();
    }
    if (viewName === 'exam') {
      this.setupExamView();
    }
    if (viewName === 'flashcards') {
      this.setupFlashcardsView();
    }
    if (window.lucide) window.lucide.createIcons();
  },

  // -------------------------------------------------------------
  // Courses & Modules Data API
  // -------------------------------------------------------------
  async loadCourses() {
    if (window.STUDY_DATA && window.STUDY_DATA.courses && window.STUDY_DATA.courses.length > 0) {
      this.courses = window.STUDY_DATA.courses;
      this.renderSyllabusView();
      this.renderNotesSidebar();
    }
    try {
      const res = await fetch('/api/courses');
      if (res.ok) {
        this.courses = await res.json();
        this.renderSyllabusView();
        this.renderNotesSidebar();
      }
    } catch (e) {
      // Static mode (GitHub Pages) uses window.STUDY_DATA
    }
  },

  renderSyllabusView() {
    const container = document.getElementById('courses-list');
    if (!container) return;

    if (this.courses.length === 0) {
      container.innerHTML = `
        <div class="p-12 text-center rounded-[1.5rem] bg-card border border-neutral-200 dark:border-neutral-800 shadow-soft space-y-4 max-w-xl mx-auto my-8">
          <div class="w-12 h-12 rounded-2xl bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center mx-auto text-neutral-500">
            <i data-lucide="book-plus" class="w-6 h-6"></i>
          </div>
          <div>
            <h3 class="text-lg font-medium tracking-tight">No courses added yet</h3>
            <p class="text-xs text-neutral-500 dark:text-neutral-400 mt-1 max-w-sm mx-auto">
              Create your real semester subjects below to begin batch-ingesting YouTube lecture videos.
            </p>
          </div>
          <button onclick="App.openCreateCourseModal()" class="pill-ink text-xs inline-flex items-center gap-1.5">
            <i data-lucide="plus" class="w-3.5 h-3.5"></i> Add First Subject
          </button>
        </div>
      `;
      if (window.lucide) window.lucide.createIcons();
      return;
    }

    container.innerHTML = this.courses.map(c => `
      <div class="rounded-[1.5rem] bg-card border border-neutral-200 dark:border-neutral-800 shadow-soft p-6 space-y-4">
        <div class="flex items-start justify-between">
          <div>
            <div class="flex items-center gap-2">
              <span class="text-xs font-mono text-neutral-400 font-medium">${c.modules.length} Modules in Syllabus</span>
            </div>
            <h3 class="text-lg font-medium tracking-tight mt-0.5">${c.name}</h3>
            ${c.description ? `<p class="text-xs text-neutral-500 dark:text-neutral-400 mt-0.5">${c.description}</p>` : ''}
          </div>
          <button onclick="App.deleteCourse('${c.id}')" class="text-neutral-400 hover:text-rose-500 p-1.5 transition" title="Delete Course">
            <i data-lucide="trash-2" class="w-4 h-4"></i>
          </button>
        </div>

        <!-- Modules Grid -->
        <div class="space-y-2 pt-2 border-t border-neutral-100 dark:border-neutral-800/80">
          <div class="text-[11px] font-mono uppercase tracking-wider text-neutral-400">Modules in Syllabus</div>
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2.5">
            ${c.modules.map(m => {
              const completedCount = m.topics.filter(t => t.status === 'completed').length;
              const totalCount = m.topics.length;
              return `
                <div class="p-3 rounded-xl bg-card-muted border border-neutral-200/60 dark:border-neutral-800/60 flex flex-col justify-between space-y-2">
                  <div>
                    <div class="flex items-center justify-between text-[11px] font-mono text-neutral-400">
                      <span>Module ${m.number}</span>
                      <span>${completedCount}/${totalCount}</span>
                    </div>
                    <div class="text-xs font-medium truncate mt-0.5">${m.name}</div>
                  </div>
                  <button onclick="App.openIngestModal('${c.id}', '${m.id}', 'Module ${m.number}')" class="w-full py-1.5 px-2 rounded-lg bg-card hover:bg-neutral-200 dark:hover:bg-neutral-700 text-xs font-medium transition flex items-center justify-center gap-1 shadow-soft-sm">
                    <i data-lucide="upload" class="w-3 h-3"></i> Add Videos
                  </button>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      </div>
    `).join('');

    if (window.lucide) window.lucide.createIcons();
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
    const panel = document.getElementById('copilot-panel');
    const resizer = document.getElementById('resizer-copilot');
    const label = document.getElementById('copilot-toggle-label');
    if (!panel) return;
    this.isCopilotOpen = !this.isCopilotOpen;
    if (this.isCopilotOpen) {
      panel.classList.remove('hidden');
      if (resizer) resizer.classList.remove('hidden');
      if (label) label.textContent = 'AI Copilot';
    } else {
      panel.classList.add('hidden');
      if (resizer) resizer.classList.add('hidden');
      if (label) label.textContent = 'Open Copilot';
    }
    localStorage.setItem('study_engine_copilot_open', this.isCopilotOpen ? 'true' : 'false');
    if (window.lucide) window.lucide.createIcons();
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

    container.innerHTML = this.copilotMessages.map(m => {
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

