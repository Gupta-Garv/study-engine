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
  paneState: { video: true, notes: true, canvas: true, copilot: false },
  activePreset: 'lecture',
  videoSpeed: 2,
  _lastPlayRateVerified: false,
  _lastSpeedEnforcedTime: 0,
  speedrunMode: false,
  currentKeyMoments: [],
  currentKeyMomentsMeta: null,
  activeKeyMomentIndex: -1,
  speedrunMonitoringInterval: null,
  speedrunToastTimeout: null,
  lastPlaybackSeconds: 0,
  voiceRate: 1,
  selectedVoiceKey: 'christopher',
  curatedVoices: [],
  notesAudioElement: null,
  currentAudioTopicId: null,
  currentAudioVoiceKey: null,
  voiceSentences: [],
  voiceSegments: [],
  voiceCurrentSentenceIdx: -1,
  isVoicePlaying: false,
  isVoicePaused: false,
  isVoiceSynthesizing: false,
  voiceTotalSeconds: 0,
  notepadTool: 'select',
  notepadColor: 'ink',
  notepadWidth: 2,
  isDrawing: false,
  isErasing: false,
  currentStroke: null,
  currentTopicCanvas: { drawings: [], text_notes: [], cards: [], images: [] },
  draggingNoteId: null,
  dragNoteOffset: { x: 0, y: 0 },
  draggingImageId: null,
  dragImageOffset: { x: 0, y: 0 },
  selectedImageId: null,
  selectedNoteId: null,
  resizingImageId: null,
  resizingCorner: null,
  resizeStartX: 0,
  resizeStartY: 0,
  resizeStartWidth: 0,
  resizeStartLeft: 0,
  resizeStartTop: 0,
  isPanningCanvas: false,
  panStartX: 0,
  panStartY: 0,
  panScrollLeft: 0,
  panScrollTop: 0,
  draggingNoteId: null,
  dragNoteOffset: { x: 0, y: 0 },
  saveNotepadDebounceTimer: null,

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
    this.initVideoSpeed();
    if (this.isStaticHost()) {
      const banner = document.getElementById('static-viewer-banner');
      if (banner) banner.classList.remove('hidden');
    }
    this.initResizers();
    this.initSearch();
    this.initDashboard();
    this.initCanvasListeners();
    this.initSpeedrunListener();
    this.initNotesVoice();
    this.initNavDrawer();
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
    if (this.redrawCanvas) this.redrawCanvas();
    if (window.FolioMotion) window.FolioMotion.updateThemeColors();
    if (window.lucide) window.lucide.createIcons();
  },

  // -------------------------------------------------------------
  // Persistent Video Speed Management (2x by default, auto-enforced)
  // -------------------------------------------------------------
  initVideoSpeed() {
    let savedSpeed = 2; // Default to 2x (user preferred speed)
    try {
      const stored = localStorage.getItem('study_engine_video_speed');
      if (stored) {
        const val = parseFloat(stored);
        if (!isNaN(val) && val > 0) savedSpeed = val;
      } else {
        localStorage.setItem('study_engine_video_speed', '2');
      }
    } catch (e) {}
    this.videoSpeed = savedSpeed;
    this.updateSpeedButtonsUI(this.videoSpeed);
  },

  // -------------------------------------------------------------
  // Universal Navigation Drawer & User Profile Controller
  // -------------------------------------------------------------
  userProfile: {
    name: 'Garv Gupta',
    email: 'garv@iimbx.ac.in',
    initials: 'GG',
    term: 'IIMBx MBA 2026 • Term 1'
  },

  initNavDrawer() {
    this.initUserProfile();

    // Hotkey: Cmd+M or Option+M or Ctrl+M to toggle Drawer
    window.addEventListener('keydown', (e) => {
      const tag = (e.target && e.target.tagName) || '';
      const isInput = tag === 'INPUT' || tag === 'TEXTAREA' || e.target.isContentEditable;
      if (!isInput && (e.metaKey || e.ctrlKey || e.altKey) && e.key.toLowerCase() === 'm') {
        e.preventDefault();
        this.toggleNavDrawer();
      }
      if (e.key === 'Escape') {
        this.closeNavDrawer();
        this.closeSearchModal();
        this.closeUserProfileModal();
      }
    });
  },

  openNavDrawer() {
    const drawer = document.getElementById('nav-drawer');
    const backdrop = document.getElementById('nav-drawer-backdrop');
    if (drawer && backdrop) {
      backdrop.classList.remove('hidden');
      drawer.classList.add('drawer-open');
    }
    this.updateDrawerSubjectList();
    this.updateUserProfileUI();
    if (window.lucide) window.lucide.createIcons();
  },

  closeNavDrawer() {
    const drawer = document.getElementById('nav-drawer');
    const backdrop = document.getElementById('nav-drawer-backdrop');
    if (drawer && backdrop) {
      drawer.classList.remove('drawer-open');
      setTimeout(() => {
        backdrop.classList.add('hidden');
      }, 200);
    }
  },

  toggleNavDrawer() {
    const drawer = document.getElementById('nav-drawer');
    if (drawer && drawer.classList.contains('drawer-open')) {
      this.closeNavDrawer();
    } else {
      this.openNavDrawer();
    }
  },

  switchViewAndCloseDrawer(viewName) {
    this.closeNavDrawer();
    this.switchView(viewName);
  },

  updateDrawerSubjectList() {
    const container = document.getElementById('drawer-subjects-list');
    if (!container || !this.courses) return;

    container.innerHTML = this.courses.map(c => {
      const totalLectures = (c.modules || []).reduce((acc, m) => acc + (m.topics ? m.topics.length : 0), 0);
      const firstTopicId = (c.modules && c.modules[0] && c.modules[0].topics && c.modules[0].topics[0]) ? c.modules[0].topics[0].id : null;

      return `
        <button onclick="App.jumpToSubjectFromDrawer('${c.id}', '${firstTopicId || ''}')" class="w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs text-neutral-500 hover:text-ink hover:bg-muted transition text-left group">
          <span class="truncate pr-2 font-medium">${this.escapeHtml(c.name)}</span>
          <span class="text-[10px] font-mono text-neutral-400 tabular-nums px-1.5 py-0.2 rounded bg-card-muted border border-border/60">${totalLectures}</span>
        </button>
      `;
    }).join('');
  },

  jumpToSubjectFromDrawer(courseId, topicId) {
    this.closeNavDrawer();
    this.switchView('notes');
    if (topicId) {
      this.loadTopicNotes(topicId);
    }
  },

  // -------------------------------------------------------------
  // Command Palette Global Search Modal Controller
  // -------------------------------------------------------------
  openSearchModal() {
    const modal = document.getElementById('global-search-modal');
    if (modal) {
      modal.classList.remove('hidden');
      modal.classList.add('modal-active');
      const input = document.getElementById('global-search-input');
      if (input) {
        input.focus();
        input.select();
      }
      this.onSearchFocus();
    }
  },

  closeSearchModal() {
    const modal = document.getElementById('global-search-modal');
    if (modal) {
      modal.classList.add('hidden');
      modal.classList.remove('modal-active');
    }
  },

  // -------------------------------------------------------------
  // User Profile & Account Settings (Multi-Student Isolation)
  // -------------------------------------------------------------
  initUserProfile() {
    try {
      const saved = localStorage.getItem('study_engine_user_profile');
      if (saved) {
        this.userProfile = { ...this.userProfile, ...JSON.parse(saved) };
      }
    } catch (e) {}
    this.updateUserProfileUI();
  },

  updateUserProfileUI() {
    const nameEls = document.querySelectorAll('.user-profile-name');
    nameEls.forEach(el => el.textContent = this.userProfile.name);

    const emailEls = document.querySelectorAll('.user-profile-email');
    emailEls.forEach(el => el.textContent = this.userProfile.email);

    const avatarEls = document.querySelectorAll('.user-avatar-initials');
    avatarEls.forEach(el => el.textContent = this.userProfile.initials || 'GG');

    const termEls = document.querySelectorAll('.user-profile-term');
    termEls.forEach(el => el.textContent = this.userProfile.term);
  },

  openUserProfileModal() {
    this.closeNavDrawer();
    const modal = document.getElementById('modal-user-profile');
    if (modal) {
      document.getElementById('profile-input-name').value = this.userProfile.name;
      document.getElementById('profile-input-email').value = this.userProfile.email;
      document.getElementById('profile-input-term').value = this.userProfile.term;
      modal.classList.remove('hidden');
    }
  },

  closeUserProfileModal() {
    const modal = document.getElementById('modal-user-profile');
    if (modal) modal.classList.add('hidden');
  },

  saveUserProfile() {
    const name = document.getElementById('profile-input-name').value.trim() || 'Garv Gupta';
    const email = document.getElementById('profile-input-email').value.trim() || 'garv@iimbx.ac.in';
    const term = document.getElementById('profile-input-term').value.trim() || 'IIMBx MBA 2026 • Term 1';

    const parts = name.split(/\s+/).filter(Boolean);
    let initials = 'GG';
    if (parts.length >= 2) {
      initials = (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    } else if (parts.length === 1 && parts[0].length >= 2) {
      initials = parts[0].substring(0, 2).toUpperCase();
    }

    this.userProfile = { name, email, initials, term };
    localStorage.setItem('study_engine_user_profile', JSON.stringify(this.userProfile));
    this.updateUserProfileUI();
    this.closeUserProfileModal();
  },

  // -------------------------------------------------------------
  // Global Search Controller (Cross-Subject & Multi-Occurrence)
  // -------------------------------------------------------------
  initSearch() {
    // Global hotkey: Cmd+K / Ctrl+K or '/'
    document.addEventListener('keydown', (e) => {
      const tag = (e.target && e.target.tagName) || '';
      const isInput = tag === 'INPUT' || tag === 'TEXTAREA' || e.target.isContentEditable;
      
      if (!isInput) {
        if (e.shiftKey && e.key.toLowerCase() === 's') {
          e.preventDefault();
          App.toggleSpeedrunMode();
          return;
        } else if ((e.shiftKey && e.key.toLowerCase() === 'n') || (e.altKey && e.key === 'ArrowRight')) {
          e.preventDefault();
          App.goToNextTopic();
          return;
        } else if ((e.shiftKey && e.key.toLowerCase() === 'p') || (e.altKey && e.key === 'ArrowLeft')) {
          e.preventDefault();
          App.goToPrevTopic();
          return;
        }
      }

      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        App.openSearchModal();
      } else if (e.key === '/' && !isInput) {
        e.preventDefault();
        App.openSearchModal();
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
    this.closeSearchModal();
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
    this.updateDynamicLectureCounts();
    this.renderRecentLectureBanner();
    this.renderSubjectMasteryCards();
    this.renderChecklist();
    this.updateDashboardTelemetry();
    if (window.FolioMotion) {
      if (!this._folioMotionInited) {
        this._folioMotionInited = true;
        window.FolioMotion.init();
      } else {
        window.FolioMotion.start3D();
        window.FolioMotion.bindTiltCards();
      }
    }
    if (window.lucide) window.lucide.createIcons();
  },

  updateDashboardTelemetry() {
    const all = this.getAllCurriculumTopics() || [];
    const totalLectures = all.length || 543;
    const studiedCount = this.studiedTopicIds ? this.studiedTopicIds.size : 0;

    const lecEl = document.getElementById('metric-lectures-studied');
    if (lecEl) lecEl.textContent = `${studiedCount} / ${totalLectures}`;

    try {
      const practiced = JSON.parse(localStorage.getItem('folio_practiced_uids') || '[]');
      const pEl = document.getElementById('metric-questions-practiced');
      if (pEl) pEl.textContent = `${Array.isArray(practiced) ? practiced.length : 0} / 587`;
    } catch (e) {}

    try {
      const mocks = JSON.parse(localStorage.getItem('folio_mock_history') || '[]');
      const mEl = document.getElementById('metric-mocks-completed');
      if (mEl) mEl.textContent = `${Array.isArray(mocks) ? mocks.length : 0}`;
    } catch (e) {}

    const doneTasks = (this.checklistItems || []).filter(i => i.done).length;
    const totalTasks = (this.checklistItems || []).length;
    const cEl = document.getElementById('metric-checklist-done');
    if (cEl) cEl.textContent = `${doneTasks} / ${totalTasks}`;
  },

  async openExamBankFor(slug) {
    this.switchView('exam');
    if (window.ExamHub) {
      await window.ExamHub.init();
      await window.ExamHub.selectCategory(slug, window.ExamHub.getSubjectCategories(slug)[0]?.key || 'mcq');
      window.ExamHub.setMode('bank');
    }
  },

  async openMockFor(slug) {
    this.switchView('exam');
    if (window.ExamHub) {
      await window.ExamHub.init();
      window.ExamHub.setMode('mock');
      await window.ExamHub.startMock(slug);
    }
  },

  updateDynamicLectureCounts() {
    const all = this.getAllCurriculumTopics();
    const total = all.length || 505;
    const coursesCount = (this.courses && this.courses.length) || 5;

    // 1. Search input placeholder
    const searchInput = document.getElementById('global-search-input');
    if (searchInput) {
      searchInput.placeholder = `Search all ${total} lectures, concepts, equations...`;
    }

    // 2. Static viewer banner
    const staticBanner = document.getElementById('static-viewer-banner');
    if (staticBanner) {
      const spans = staticBanner.querySelectorAll('span');
      if (spans.length >= 5) {
        spans[4].textContent = `IIMBx Degree Suite • ${coursesCount} Subjects • ${total} Curated Lectures`;
      }
    }

    // 3. Hero summary description
    const heroDesc = document.querySelector('#view-dashboard p.text-ink-secondary');
    if (heroDesc) {
      heroDesc.textContent = `All ${total} lectures, slides, and transcripts are indexed. Study notes with embedded video, pin key formulas to your visual canvas, solve doubts with AI Copilot, and track exam readiness.`;
    }

    // 4. Curriculum mastery header
    const masteryHeader = document.querySelector('#view-dashboard .text-xs.font-mono.uppercase span');
    if (masteryHeader && masteryHeader.textContent.includes('Curriculum Mastery')) {
      masteryHeader.textContent = `Degree Curriculum Mastery (${coursesCount} Subjects • ${total} Lectures)`;
    }
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
      const totalLectures = (this.getAllCurriculumTopics() || []).length || 505;
      banner.innerHTML = `
        <button onclick="App.switchView('notes')" class="pill-ink text-xs px-4 py-2 inline-flex items-center gap-2">
          <i data-lucide="sparkles" class="w-3.5 h-3.5"></i>
          <span>Launch Study Studio (${totalLectures} Lectures Ready)</span>
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
          <div class="grid grid-cols-3 gap-1.5 pt-2 border-t border-border/60">
            <button onclick="App.launchCourseStudy('${firstTopicId}')" class="pill-muted text-[11px] py-1.5 px-2 flex items-center justify-center gap-1 font-medium truncate">
              <i data-lucide="book-open" class="w-3 h-3"></i>
              <span>Studio</span>
            </button>
            <button onclick="App.launchOneShot('${c.id}')" class="px-2 py-1.5 rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 hover:bg-amber-500/20 text-[11px] flex items-center justify-center gap-1 font-medium transition truncate">
              <i data-lucide="zap" class="w-3 h-3"></i>
              <span>One-Shot</span>
            </button>
            <button onclick="App.launchCourseExam('${firstModuleId}')" class="px-2 py-1.5 rounded-full border border-border hover:bg-card-muted text-[11px] text-ink flex items-center justify-center gap-1 font-medium transition truncate">
              <i data-lucide="award" class="w-3 h-3"></i>
              <span>Quiz</span>
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
      this.paneState = { video: true, notes: true, canvas: true, copilot: false };
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
    const leftCol = document.getElementById('left-studio-column');
    const paneVideo = document.getElementById('pane-video');
    const resizerVideo = document.getElementById('resizer-video-canvas');
    const paneCanvas = document.getElementById('pane-canvas');
    const resizerNotes = document.getElementById('resizer-notes-column');
    const paneNotes = document.getElementById('pane-notes');
    const copilot = document.getElementById('copilot-panel');
    const resizerCopilot = document.getElementById('resizer-copilot');

    const showVideo = !!this.paneState.video;
    const showCanvas = !!this.paneState.canvas;
    const showNotes = !!this.paneState.notes;
    const showCopilot = !!this.paneState.copilot;

    // 1. Left Column (Video + Notepad) Visibility & Vertical Sizing
    if (!showVideo && !showCanvas) {
      if (leftCol) leftCol.classList.add('hidden');
      if (resizerNotes) resizerNotes.classList.add('hidden');
    } else {
      if (leftCol) {
        leftCol.classList.remove('hidden');
        if (!showNotes) {
          leftCol.style.width = '100%';
        } else {
          const savedW = localStorage.getItem('study_engine_left_col_width');
          leftCol.style.width = savedW || '48%';
        }
      }
      if (resizerNotes) resizerNotes.classList.toggle('hidden', !showNotes);

      if (showVideo && showCanvas) {
        if (paneVideo) {
          paneVideo.classList.remove('hidden');
          const savedH = localStorage.getItem('study_engine_video_pane_height');
          paneVideo.style.height = savedH || '48%';
        }
        if (resizerVideo) resizerVideo.classList.remove('hidden');
        if (paneCanvas) {
          paneCanvas.classList.remove('hidden');
          paneCanvas.style.height = '';
          paneCanvas.classList.add('flex-1');
        }
      } else if (showVideo && !showCanvas) {
        if (paneVideo) {
          paneVideo.classList.remove('hidden');
          paneVideo.style.height = '100%';
        }
        if (resizerVideo) resizerVideo.classList.add('hidden');
        if (paneCanvas) paneCanvas.classList.add('hidden');
      } else if (!showVideo && showCanvas) {
        if (paneVideo) paneVideo.classList.add('hidden');
        if (resizerVideo) resizerVideo.classList.add('hidden');
        if (paneCanvas) {
          paneCanvas.classList.remove('hidden');
          paneCanvas.style.height = '100%';
          paneCanvas.classList.remove('flex-1');
        }
      }
    }

    // 2. Right Column (Synthesized Notes)
    if (paneNotes) {
      paneNotes.classList.toggle('hidden', !showNotes);
      if (!showVideo && !showCanvas) {
        paneNotes.style.width = '100%';
      } else {
        paneNotes.style.width = '';
      }
    }

    // 3. Lecture Copilot Drawer
    if (copilot) copilot.classList.toggle('hidden', !showCopilot);
    if (resizerCopilot) resizerCopilot.classList.toggle('hidden', !showCopilot);
    this.isCopilotOpen = showCopilot;

    // 4. Update Header Toggle Buttons
    ['video', 'notes', 'canvas', 'copilot'].forEach(p => {
      const btn = document.getElementById(`toggle-${p}-btn`);
      if (btn) {
        if (this.paneState[p]) {
          btn.className = 'tool-toggle-pill px-2.5 py-1 rounded-lg border text-xs font-mono flex items-center gap-1.5 transition active font-semibold border-neutral-900 dark:border-white bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 shadow-soft-sm';
        } else {
          btn.className = 'tool-toggle-pill px-2.5 py-1 rounded-lg border text-xs font-mono flex items-center gap-1.5 transition border-border bg-card text-neutral-400 hover:text-ink';
        }
      }
    });

    // Keep speed buttons in sync
    this.updateSpeedButtonsUI(this.videoSpeed);

    // 5. Redraw canvas after layout change
    if (showCanvas) {
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
      const isNewSrc = (iframe.src !== embedUrl);
      if (isNewSrc) {
        this._lastPlayRateVerified = false;
        iframe.onload = () => {
          this.applyCurrentVideoSpeed();
          [200, 500, 900, 1600, 2800].forEach(delay => {
            setTimeout(() => this.applyCurrentVideoSpeed(), delay);
          });
        };
        iframe.src = embedUrl;
      }
      iframe.classList.remove('hidden');
      if (placeholder) placeholder.classList.add('hidden');
      if (extLink) {
        extLink.href = topic.youtube_url || `https://www.youtube.com/watch?v=${topic.video_id}`;
        extLink.classList.remove('pointer-events-none', 'opacity-50');
      }

      // Keep UI speed buttons visually in sync with persistent speed
      this.updateSpeedButtonsUI(this.videoSpeed);

      // Staggered speed auto-enforcements
      this.applyCurrentVideoSpeed();
      [250, 600, 1200, 2000, 3200].forEach(delay => {
        setTimeout(() => this.applyCurrentVideoSpeed(), delay);
      });
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
    this._lastPlayRateVerified = false;
    try {
      localStorage.setItem('study_engine_video_speed', String(speed));
    } catch (e) {}
    this.updateSpeedButtonsUI(speed);
    this.applyCurrentVideoSpeed();
  },

  updateSpeedButtonsUI(speed) {
    const targetSpeed = (typeof speed === 'number' && speed > 0) ? speed : (this.videoSpeed || 2);
    const speedBtns = document.querySelectorAll('.speed-btn');
    speedBtns.forEach(btn => {
      const s = parseFloat(btn.getAttribute('data-speed'));
      if (Math.abs(s - targetSpeed) < 0.01) {
        btn.className = 'speed-btn px-1.5 py-0.5 rounded bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 font-semibold';
      } else {
        btn.className = 'speed-btn px-1.5 py-0.5 rounded bg-card-muted hover:bg-muted text-ink-secondary';
      }
    });
  },

  applyCurrentVideoSpeed() {
    const speed = this.videoSpeed || 2;
    const iframe = document.getElementById('lecture-video-iframe');
    if (iframe && iframe.contentWindow && !iframe.classList.contains('hidden')) {
      try {
        iframe.contentWindow.postMessage(JSON.stringify({ event: 'listening' }), '*');
        iframe.contentWindow.postMessage(JSON.stringify({
          event: 'command',
          func: 'setPlaybackRate',
          args: [speed]
        }), '*');
      } catch (e) {}
    }
  },

  seekVideoToSeconds(seconds) {
    if (!this.paneState.video) {
      this.paneState.video = true;
      this.updateStudioLayout();
    }
    const iframe = document.getElementById('lecture-video-iframe');
    if (iframe && iframe.contentWindow) {
      this.applyCurrentVideoSpeed();
      iframe.contentWindow.postMessage(JSON.stringify({
        event: 'command',
        func: 'seekTo',
        args: [seconds, true]
      }), '*');
    }
  },

  playVideo() {
    const iframe = document.getElementById('lecture-video-iframe');
    if (iframe && iframe.contentWindow) {
      this.applyCurrentVideoSpeed();
      iframe.contentWindow.postMessage(JSON.stringify({
        event: 'command',
        func: 'playVideo',
        args: []
      }), '*');
      setTimeout(() => this.applyCurrentVideoSpeed(), 200);
    }
  },

  pauseVideo() {
    const iframe = document.getElementById('lecture-video-iframe');
    if (iframe && iframe.contentWindow) {
      iframe.contentWindow.postMessage(JSON.stringify({
        event: 'command',
        func: 'pauseVideo',
        args: []
      }), '*');
    }
  },

  // -------------------------------------------------------------
  // High-Yield Key Moments & Smart Speedrun Engine
  // -------------------------------------------------------------
  initSpeedrunListener() {
    // Listen for YouTube IFrame postMessages
    window.addEventListener('message', (event) => {
      try {
        let data = event.data;
        if (typeof data === 'string') {
          try { data = JSON.parse(data); } catch (e) { return; }
        }
        if (!data) return;

        // When YouTube player signals it is ready or initial delivery
        if (data.event === 'onReady' || data.event === 'initialDelivery') {
          this.applyCurrentVideoSpeed();
        }

        if (data.event === 'infoDelivery' && data.info) {
          const ct = data.info.currentTime;
          const ps = data.info.playerState;
          const rate = data.info.playbackRate;

          // Reactive auto-enforcement: if YouTube rate does not match user's persistent speed, re-apply!
          if (typeof rate === 'number' && Math.abs(rate - this.videoSpeed) > 0.01) {
            const now = Date.now();
            if (!this._lastSpeedEnforcedTime || (now - this._lastSpeedEnforcedTime > 250)) {
              this._lastSpeedEnforcedTime = now;
              this.applyCurrentVideoSpeed();
            }
          }

          // When video begins playing (1) or buffering (3), ensure speed matches
          if ((ps === 1 || ps === 3) && typeof rate === 'number' && Math.abs(rate - this.videoSpeed) > 0.01) {
            this.applyCurrentVideoSpeed();
          } else if (ps === 1 && !this._lastPlayRateVerified) {
            this._lastPlayRateVerified = true;
            this.applyCurrentVideoSpeed();
          }

          if (typeof ct === 'number') {
            this.onVideoTimeUpdate(ct, ps);
          }
        }
      } catch (e) {}
    });

    // Also poll iframe every 800ms while video pane is open to ensure continuous time synchronization
    if (!this.speedrunMonitoringInterval) {
      this.speedrunMonitoringInterval = setInterval(() => {
        const iframe = document.getElementById('lecture-video-iframe');
        if (iframe && iframe.contentWindow && !iframe.classList.contains('hidden')) {
          iframe.contentWindow.postMessage(JSON.stringify({ event: 'listening' }), '*');
        }
      }, 750);
    }
  },

  renderKeyMoments(topicData) {
    const panel = document.getElementById('video-key-moments-panel');
    const pillsList = document.getElementById('key-moments-pills-list');
    const statsEl = document.getElementById('speedrun-summary-stats');
    if (!panel || !pillsList) return;

    let kmData = topicData ? (topicData.key_moments || topicData.key_moments_json) : null;
    if (typeof kmData === 'string') {
      try { kmData = JSON.parse(kmData); } catch (e) { kmData = null; }
    }

    let moments = [];
    let meta = null;
    if (kmData) {
      if (Array.isArray(kmData)) {
        moments = kmData;
      } else if (typeof kmData === 'object' && Array.isArray(kmData.key_moments)) {
        moments = kmData.key_moments;
        meta = kmData;
      }
    }

    this.currentKeyMoments = moments;
    this.currentKeyMomentsMeta = meta;
    this.activeKeyMomentIndex = -1;

    if (!moments || moments.length === 0) {
      const dur = (topicData && topicData.duration_seconds > 0) ? topicData.duration_seconds : 720;
      moments = this.generateFallbackMoments(topicData, dur);
      meta = {
        total_video_duration_seconds: dur,
        high_yield_duration_seconds: Math.round(dur * 0.4),
        fluff_saved_percentage: 60,
        key_moments: moments
      };
      this.currentKeyMoments = moments;
      this.currentKeyMomentsMeta = meta;

      // Auto-synthesize deep context-aware moments in background
      if (topicData && topicData.id && !this.isStaticHost()) {
        this.autoSynthesizeKeyMomentsInBackground(topicData.id);
      }
    }

    panel.classList.remove('hidden');

    if (statsEl) {
      if (meta && meta.fluff_saved_percentage) {
        const hyMins = Math.floor((meta.high_yield_duration_seconds || 0) / 60);
        const hySecs = Math.floor((meta.high_yield_duration_seconds || 0) % 60);
        statsEl.textContent = `${moments.length} key moments • ${hyMins}m ${hySecs}s (${meta.fluff_saved_percentage}% fluff cut)`;
      } else {
        statsEl.textContent = `${moments.length} key concepts identified`;
      }
    }

    pillsList.innerHTML = moments.map((m, idx) => {
      const titleEscaped = (m.title || 'Key Concept').replace(/"/g, '&quot;');
      const whyEscaped = (m.why_essential || '').replace(/"/g, '&quot;');
      return `
        <button 
          id="km-pill-${idx}"
          onclick="App.jumpToKeyMoment(${idx}, ${m.start_seconds})" 
          class="key-moment-pill shrink-0 px-2.5 py-1 rounded-lg border border-border bg-card hover:bg-muted text-[11px] font-mono flex items-center gap-1.5 transition text-ink"
          title="${whyEscaped ? whyEscaped + '\nTakeaway: ' + (m.key_takeaway || '') : titleEscaped}"
          data-start="${m.start_seconds}"
          data-end="${m.end_seconds}"
        >
          <i data-lucide="play" class="w-2.5 h-2.5 text-amber-500 fill-amber-500"></i>
          <span class="text-neutral-400 font-semibold">${m.timestamp_display || App.formatSeconds(m.start_seconds)}</span>
          <span class="font-medium text-ink max-w-[170px] sm:max-w-[210px] truncate">${m.title}</span>
          ${m.yield_score ? `<span class="px-1 py-0.2 rounded bg-amber-500/15 text-amber-600 dark:text-amber-400 text-[9px] font-bold">★${m.yield_score}</span>` : ''}
        </button>
      `;
    }).join('');

    if (window.lucide) window.lucide.createIcons();
    this.updateSpeedrunToggleButtonUI();
  },

  jumpToKeyMoment(idx, startSeconds) {
    if (!this.currentKeyMoments || !this.currentKeyMoments[idx]) return;
    const moment = this.currentKeyMoments[idx];
    this.seekVideoToSeconds(startSeconds);
    this.playVideo();
    this.highlightActiveKeyMomentPill(idx);
    this.showSpeedrunToast(`⚡ Concept: ${moment.title}`);
  },

  generateFallbackMoments(topicData, dur) {
    const title = topicData ? (topicData.title || 'Core Lecture') : 'Core Lecture';
    const s1 = Math.round(dur * 0.1);
    const e1 = Math.round(dur * 0.35);
    const s2 = Math.round(dur * 0.45);
    const e2 = Math.round(dur * 0.7);
    const s3 = Math.round(dur * 0.75);
    const e3 = Math.round(dur * 0.95);

    return [
      {
        start_seconds: s1,
        end_seconds: e1,
        timestamp_display: `${this.formatSeconds(s1)} - ${this.formatSeconds(e1)}`,
        title: `${title}: Core Problem & Foundation`,
        yield_score: 9,
        why_essential: 'Essential mental model setup and foundational problem formulation.',
        key_takeaway: 'Core definitions and initial setup.'
      },
      {
        start_seconds: s2,
        end_seconds: e2,
        timestamp_display: `${this.formatSeconds(s2)} - ${this.formatSeconds(e2)}`,
        title: `${title}: Mechanics & Analytical Model`,
        yield_score: 10,
        why_essential: 'Core mechanics, governing frameworks, and parameter shifts.',
        key_takeaway: 'High-yield analytical mechanics tested in exams.'
      },
      {
        start_seconds: s3,
        end_seconds: e3,
        timestamp_display: `${this.formatSeconds(s3)} - ${this.formatSeconds(e3)}`,
        title: `${title}: Strategic Takeaways & Synthesis`,
        yield_score: 8,
        why_essential: 'Decision criteria, boundary conditions, and executive conclusions.',
        key_takeaway: 'Final strategic implications.'
      }
    ];
  },

  autoSynthesizeKeyMomentsInBackground(topicId) {
    if (this._synthesizingTopics && this._synthesizingTopics.has(topicId)) return;
    if (!this._synthesizingTopics) this._synthesizingTopics = new Set();
    this._synthesizingTopics.add(topicId);

    fetch(`/api/topics/${topicId}/key-moments`, { method: 'POST' })
      .then(res => res.json())
      .then(kmData => {
        if (kmData && kmData.key_moments && this.selectedTopicId === topicId) {
          this.renderKeyMoments({ id: topicId, key_moments: kmData });
        }
      })
      .catch(() => {})
      .finally(() => {
        if (this._synthesizingTopics) this._synthesizingTopics.delete(topicId);
      });
  },

  toggleSpeedrunMode() {
    this.speedrunMode = !this.speedrunMode;
    this.updateSpeedrunToggleButtonUI();

    if (this.speedrunMode) {
      this.showSpeedrunToast('⚡ Speedrun Mode ON • Auto-skipping recaps & filler', 2200);
      if (this.currentKeyMoments && this.currentKeyMoments.length > 0) {
        const firstM = this.currentKeyMoments[0];
        if (this.lastPlaybackSeconds < firstM.start_seconds - 2) {
          this.seekVideoToSeconds(firstM.start_seconds);
          this.playVideo();
          this.highlightActiveKeyMomentPill(0);
        }
      }
    } else {
      this.showSpeedrunToast('Speedrun Mode OFF • Full lecture playback active', 1800);
    }
  },

  updateSpeedrunToggleButtonUI() {
    const btn = document.getElementById('btn-toggle-speedrun');
    const dot = document.getElementById('speedrun-status-dot');
    const label = document.getElementById('speedrun-toggle-label');
    if (!btn || !dot || !label) return;

    if (this.speedrunMode) {
      btn.className = 'px-2.5 py-0.5 rounded-full border border-amber-500/50 bg-amber-500/15 text-amber-600 dark:text-amber-400 text-[11px] font-mono flex items-center gap-1.5 transition font-semibold shadow-soft-sm';
      dot.className = 'w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse';
      label.textContent = 'Auto-Skip: ON';
    } else {
      btn.className = 'px-2.5 py-0.5 rounded-full border border-border text-[11px] font-mono flex items-center gap-1.5 transition text-neutral-400 hover:text-ink hover:bg-card-muted';
      dot.className = 'w-1.5 h-1.5 rounded-full bg-neutral-400';
      label.textContent = 'Auto-Skip: OFF';
    }
  },

  onVideoTimeUpdate(currentTime, playerState) {
    this.lastPlaybackSeconds = currentTime;
    if (!this.currentKeyMoments || this.currentKeyMoments.length === 0) return;

    // 1. Identify which moment we are currently in
    let matchedIdx = -1;
    for (let i = 0; i < this.currentKeyMoments.length; i++) {
      const m = this.currentKeyMoments[i];
      if (currentTime >= (m.start_seconds - 0.5) && currentTime <= (m.end_seconds + 0.5)) {
        matchedIdx = i;
        break;
      }
    }

    if (matchedIdx !== this.activeKeyMomentIndex) {
      this.highlightActiveKeyMomentPill(matchedIdx);
    }

    // 2. Automated Fluff-Skipping when Speedrun Mode is ON
    if (this.speedrunMode && (playerState === 1 || playerState === undefined)) {
      if (this.activeKeyMomentIndex >= 0) {
        const curM = this.currentKeyMoments[this.activeKeyMomentIndex];
        if (currentTime >= curM.end_seconds) {
          const nextIdx = this.activeKeyMomentIndex + 1;
          if (nextIdx < this.currentKeyMoments.length) {
            const nextM = this.currentKeyMoments[nextIdx];
            const skippedSecs = Math.max(0, Math.round(nextM.start_seconds - currentTime));
            this.seekVideoToSeconds(nextM.start_seconds);
            this.highlightActiveKeyMomentPill(nextIdx);
            this.showSpeedrunToast(`⚡ Skipped ${skippedSecs}s fluff • Now: ${nextM.title}`, 2500);
          } else {
            this.showSpeedrunToast('⚡ Speedrun Complete! All key concepts mastered.', 3000);
          }
        }
      } else {
        for (let i = 0; i < this.currentKeyMoments.length; i++) {
          const m = this.currentKeyMoments[i];
          if (m.start_seconds > currentTime + 3.0) {
            const prevMomentEnd = i > 0 ? this.currentKeyMoments[i-1].end_seconds : 0;
            if (currentTime >= prevMomentEnd) {
              const skippedSecs = Math.max(0, Math.round(m.start_seconds - currentTime));
              this.seekVideoToSeconds(m.start_seconds);
              this.highlightActiveKeyMomentPill(i);
              this.showSpeedrunToast(`⚡ Skipped ${skippedSecs}s filler • Jumping to: ${m.title}`, 2500);
              break;
            }
          }
        }
      }
    }
  },

  highlightActiveKeyMomentPill(idx) {
    this.activeKeyMomentIndex = idx;
    const pills = document.querySelectorAll('.key-moment-pill');
    pills.forEach((p, i) => {
      if (i === idx) {
        p.classList.add('active');
        p.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' });
      } else {
        p.classList.remove('active');
      }
    });
  },

  showSpeedrunToast(text, durationMs = 2000) {
    const toast = document.getElementById('speedrun-skip-toast');
    const label = document.getElementById('speedrun-skip-toast-text');
    if (!toast || !label) return;

    label.textContent = text;
    toast.classList.remove('opacity-0', '-translate-y-2');
    toast.classList.add('opacity-100', 'translate-y-0');

    if (this.speedrunToastTimeout) clearTimeout(this.speedrunToastTimeout);
    this.speedrunToastTimeout = setTimeout(() => {
      toast.classList.remove('opacity-100', 'translate-y-0');
      toast.classList.add('opacity-0', '-translate-y-2');
    }, durationMs);
  },

  formatSeconds(secs) {
    if (!secs || isNaN(secs)) return '00:00';
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  },

  // -------------------------------------------------------------
  // Freeform Interactive Study Notepad / Scratchpad Engine
  // -------------------------------------------------------------
  initCanvasListeners() {
    const canvas = document.getElementById('notepad-drawing-canvas');
    if (canvas) {
      canvas.addEventListener('pointerdown', (e) => this.onNotepadPointerDown(e));
      canvas.addEventListener('pointermove', (e) => this.onNotepadPointerMove(e));
      canvas.addEventListener('pointerup', (e) => this.onNotepadPointerUp(e));
      canvas.addEventListener('pointercancel', (e) => this.onNotepadPointerUp(e));

      canvas.addEventListener('mousedown', (e) => {
        if (!window.PointerEvent) this.onNotepadPointerDown(e);
      });
      canvas.addEventListener('mousemove', (e) => {
        if (!window.PointerEvent) this.onNotepadPointerMove(e);
      });
      canvas.addEventListener('mouseup', (e) => {
        if (!window.PointerEvent) this.onNotepadPointerUp(e);
      });
    }

    const viewport = document.getElementById('notepad-viewport');
    if (viewport) {
      // Double click to place note anywhere
      viewport.addEventListener('dblclick', (e) => {
        if (e.target.closest && (e.target.closest('.notepad-text-note') || e.target.closest('.notepad-image-card'))) return;
        const coords = this.getNotepadCanvasCoords(e);
        this.addFloatingTextNoteAt(coords.x, coords.y);
      });

      // Background panning in Pointer mode (Mac Notes style)
      viewport.addEventListener('pointerdown', (e) => {
        if (this.notepadTool === 'select') {
          if (e.target.closest && (e.target.closest('.notepad-image-card') || e.target.closest('.notepad-text-note') || e.target.closest('button'))) return;
          this.isPanningCanvas = true;
          this.panStartX = e.clientX;
          this.panStartY = e.clientY;
          this.panScrollLeft = viewport.scrollLeft;
          this.panScrollTop = viewport.scrollTop;
          viewport.style.cursor = 'grabbing';
          this.deselectAllCards();
        }
      });

      // Drag and Drop Screenshot Images onto Notepad
      viewport.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        viewport.classList.add('notepad-drop-active');
      });

      viewport.addEventListener('dragleave', (e) => {
        e.preventDefault();
        viewport.classList.remove('notepad-drop-active');
      });

      viewport.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        viewport.classList.remove('notepad-drop-active');
        if (e.dataTransfer && e.dataTransfer.files) {
          for (let i = 0; i < e.dataTransfer.files.length; i++) {
            const file = e.dataTransfer.files[i];
            if (file.type && file.type.startsWith('image/')) {
              this.handleImageUploadFile(file, e.clientX, e.clientY);
            }
          }
        }
      });
    }

    // Global Clipboard Paste listener (Cmd+V / Ctrl+V) for instant screenshot pasting!
    window.addEventListener('paste', (e) => {
      const tag = (e.target && e.target.tagName) || '';
      if (tag === 'INPUT' || tag === 'TEXTAREA' || (e.target && e.target.isContentEditable)) return;
      if (!this.paneState || !this.paneState.canvas) return;

      if (e.clipboardData && e.clipboardData.items) {
        for (let i = 0; i < e.clipboardData.items.length; i++) {
          const item = e.clipboardData.items[i];
          if (item.type && item.type.indexOf('image') !== -1) {
            const file = item.getAsFile();
            if (file) {
              e.preventDefault();
              this.handleImageUploadFile(file);
              break;
            }
          }
        }
      }
    });

    // Global Pointer listeners for dragging notes & images smoothly
    window.addEventListener('pointermove', (e) => this.onNotepadGlobalPointerMove(e));
    window.addEventListener('pointerup', (e) => this.onNotepadGlobalPointerUp(e));
    window.addEventListener('mousemove', (e) => {
      if (!window.PointerEvent) this.onNotepadGlobalPointerMove(e);
    });
    window.addEventListener('mouseup', (e) => {
      if (!window.PointerEvent) this.onNotepadGlobalPointerUp(e);
    });

    // Keyboard Shortcuts: Tool switching (V, P, H, T, E), Delete selected, Cmd+Z for undo
    window.addEventListener('keydown', (e) => {
      const tag = (e.target && e.target.tagName) || '';
      const isInput = tag === 'INPUT' || tag === 'TEXTAREA' || (e.target && e.target.isContentEditable);
      
      if (!isInput) {
        // Delete selected image with Backspace / Delete
        if (e.key === 'Backspace' || e.key === 'Delete') {
          if (this.selectedImageId) {
            e.preventDefault();
            this.deleteNotepadImage(this.selectedImageId);
            this.selectedImageId = null;
            return;
          }
        }

        // Tool hotkeys when in Studio
        if (this.paneState && this.paneState.canvas) {
          const k = e.key.toLowerCase();
          if (k === 'v' || e.key === 'Escape' || k === '1') {
            this.setNotepadTool('select');
          } else if (k === 'p' || k === '2') {
            this.setNotepadTool('pen');
          } else if (k === 'h' || k === '3') {
            this.setNotepadTool('highlighter');
          } else if (k === 't' || k === '4') {
            this.setNotepadTool('text');
          } else if (k === 'e' || k === '5') {
            this.setNotepadTool('eraser');
          }
        }

        if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'z') {
          if (this.paneState && this.paneState.canvas) {
            e.preventDefault();
            this.undoNotepadStroke();
          }
        }
      }
    });
  },

  setNotepadTool(tool) {
    this.notepadTool = tool;

    // Update toolbar tool buttons
    const tools = ['select', 'pen', 'highlighter', 'text', 'eraser'];
    tools.forEach(t => {
      const btn = document.getElementById(`np-tool-${t}`);
      if (!btn) return;
      if (t === tool) {
        btn.className = 'notepad-tool-btn active px-2.5 py-1 rounded-md text-xs font-mono flex items-center gap-1 transition shadow-soft-sm font-semibold text-ink bg-card';
      } else {
        btn.className = 'notepad-tool-btn px-2.5 py-1 rounded-md text-xs font-mono flex items-center gap-1 transition text-neutral-400 hover:text-ink';
      }
    });

    const viewport = document.getElementById('notepad-viewport');
    const canvas = document.getElementById('notepad-drawing-canvas');

    // In 'select' or 'text' mode, drawing canvas has pointer-events: none so you can directly click & drag images and notes!
    // In 'pen', 'highlighter', or 'eraser' mode, drawing canvas has pointer-events: auto to draw/erase strokes.
    if (canvas) {
      if (tool === 'select' || tool === 'text') {
        canvas.style.pointerEvents = 'none';
        canvas.style.zIndex = '5';
      } else {
        canvas.style.pointerEvents = 'auto';
        canvas.style.zIndex = '50';
      }
    }

    // Update viewport cursor
    const cursor = (tool === 'select') ? 'default' :
                   (tool === 'pen' || tool === 'highlighter') ? 'crosshair' :
                   (tool === 'text') ? 'text' : 'cell';
    if (viewport) viewport.style.cursor = cursor;
    if (canvas && tool !== 'select' && tool !== 'text') canvas.style.cursor = cursor;

    // Update helpful status hint with keyboard shortcuts
    const hintEl = document.getElementById('notepad-tool-hint');
    if (hintEl) {
      if (tool === 'select') {
        hintEl.textContent = 'Pointer mode • Click & drag any screenshot or note to move • Drag background to pan board [V]';
      } else if (tool === 'pen') {
        hintEl.textContent = 'Pen mode • Drag to draw equations & arrows over notes and screenshots [P]';
      } else if (tool === 'highlighter') {
        hintEl.textContent = 'Highlighter mode • Drag to highlight diagrams & equations [H]';
      } else if (tool === 'text') {
        hintEl.textContent = 'Text mode • Click anywhere on notepad to drop a note [T]';
      } else if (tool === 'eraser') {
        hintEl.textContent = 'Eraser mode • Drag over strokes to erase [E]';
      }
    }
  },

  selectImageCard(imgId) {
    this.selectedImageId = imgId;
    document.querySelectorAll('.notepad-image-card').forEach(el => {
      const match = el.getAttribute('data-image-id') === imgId;
      el.classList.toggle('selected', match);
    });

    const img = (this.currentTopicCanvas.images || []).find(i => i.id === imgId);
    if (img) {
      this.maxNoteZIndex = (this.maxNoteZIndex || 30) + 1;
      img.zIndex = this.maxNoteZIndex;
      const el = document.querySelector(`.notepad-image-card[data-image-id="${imgId}"]`);
      if (el) el.style.zIndex = img.zIndex;
    }
  },

  deselectAllCards() {
    this.selectedImageId = null;
    document.querySelectorAll('.notepad-image-card').forEach(el => el.classList.remove('selected'));
  },

  setNotepadColor(color) {
    this.notepadColor = color;
    
    // Update color dots active state
    const dots = document.querySelectorAll('.notepad-color-dot');
    dots.forEach(dot => {
      if (dot.getAttribute('data-color') === color) {
        dot.classList.add('active', 'ring-2', 'ring-neutral-400', 'scale-110');
      } else {
        dot.classList.remove('active', 'ring-2', 'ring-neutral-400', 'scale-110');
      }
    });

    if (this.notepadTool === 'select' || this.notepadTool === 'eraser' || this.notepadTool === 'text') {
      this.setNotepadTool('pen');
    }
  },

  setNotepadWidth(width) {
    this.notepadWidth = Number(width) || 2;
    
    const sizeBtns = document.querySelectorAll('.np-size-btn');
    sizeBtns.forEach(btn => {
      if (Number(btn.getAttribute('data-width')) === this.notepadWidth) {
        btn.className = 'np-size-btn active px-1.5 py-0.5 rounded text-xs font-semibold text-ink bg-card shadow-soft-sm';
      } else {
        btn.className = 'np-size-btn px-1.5 py-0.5 rounded text-xs text-neutral-400 hover:text-ink';
      }
    });

    if (this.notepadTool === 'select' || this.notepadTool === 'eraser' || this.notepadTool === 'text') {
      this.setNotepadTool('pen');
    }
  },

  getNotepadCanvasCoords(e) {
    const canvas = document.getElementById('notepad-drawing-canvas');
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    if (!rect.width || !rect.height) return { x: 0, y: 0 };
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    return {
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top) * scaleY
    };
  },

  onNotepadPointerDown(e) {
    if (e.button !== undefined && e.button !== 0 && e.button !== -1) return;
    
    // In select mode, clicking on drawing canvas should not draw!
    if (this.notepadTool === 'select') {
      this.deselectAllCards();
      return;
    }

    e.preventDefault();
    const canvas = document.getElementById('notepad-drawing-canvas');
    if (canvas && e.pointerId !== undefined) {
      try { canvas.setPointerCapture(e.pointerId); } catch (_) {}
    }

    const coords = this.getNotepadCanvasCoords(e);

    // If text tool is active, place a note at click position then return to select
    if (this.notepadTool === 'text') {
      this.addFloatingTextNoteAt(coords.x, coords.y);
      this.setNotepadTool('select');
      return;
    }

    if (this.notepadTool === 'eraser') {
      this.isDrawing = true;
      this.eraseStrokesNear(coords.x, coords.y);
      return;
    }

    this.isDrawing = true;
    const isHighlighter = this.notepadTool === 'highlighter';
    const strokeWidth = isHighlighter ? Math.max(16, this.notepadWidth * 4) : this.notepadWidth;
    const strokeOpacity = isHighlighter ? 0.35 : 1.0;

    this.currentStroke = {
      tool: this.notepadTool,
      color: this.notepadColor,
      width: strokeWidth,
      opacity: strokeOpacity,
      points: [{ x: Math.round(coords.x), y: Math.round(coords.y) }]
    };

    this.drawSinglePoint(coords.x, coords.y, this.currentStroke);
  },

  onNotepadPointerMove(e) {
    if (!this.isDrawing) return;
    e.preventDefault();
    
    const coords = this.getNotepadCanvasCoords(e);

    if (this.notepadTool === 'eraser') {
      this.eraseStrokesNear(coords.x, coords.y);
      return;
    }

    if (this.currentStroke && this.currentStroke.points.length > 0) {
      const pts = this.currentStroke.points;
      const lastPt = pts[pts.length - 1];
      const distSq = (coords.x - lastPt.x) ** 2 + (coords.y - lastPt.y) ** 2;
      
      if (distSq >= 2) {
        const newPt = { x: Math.round(coords.x), y: Math.round(coords.y) };
        pts.push(newPt);
        this.drawLineSegment(lastPt, newPt, this.currentStroke);
      }
    }
  },

  onNotepadPointerUp(e) {
    if (!this.isDrawing) return;
    this.isDrawing = false;

    const canvas = document.getElementById('notepad-drawing-canvas');
    if (canvas && e && e.pointerId !== undefined) {
      try { canvas.releasePointerCapture(e.pointerId); } catch (_) {}
    }

    if (this.currentStroke && this.currentStroke.points.length > 0) {
      if (!this.currentTopicCanvas.drawings) {
        this.currentTopicCanvas.drawings = [];
      }
      this.currentTopicCanvas.drawings.push(this.currentStroke);
      this.currentStroke = null;
      this.scheduleSaveCanvas();
    }
  },

  drawSinglePoint(x, y, stroke) {
    const canvas = document.getElementById('notepad-drawing-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const isDark = document.documentElement.classList.contains('dark');
    const strokeColor = stroke.color === 'ink' ? (isDark ? '#EDEDED' : '#171717') : (stroke.color || (isDark ? '#EDEDED' : '#171717'));

    ctx.save();
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.globalAlpha = stroke.opacity || 1.0;
    ctx.fillStyle = strokeColor;
    ctx.beginPath();
    ctx.arc(x, y, Math.max(1, (stroke.width || 2) / 2), 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  },

  drawLineSegment(p1, p2, stroke) {
    const canvas = document.getElementById('notepad-drawing-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const isDark = document.documentElement.classList.contains('dark');
    const strokeColor = stroke.color === 'ink' ? (isDark ? '#EDEDED' : '#171717') : (stroke.color || (isDark ? '#EDEDED' : '#171717'));

    ctx.save();
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.globalAlpha = stroke.opacity || 1.0;
    ctx.strokeStyle = strokeColor;
    ctx.lineWidth = stroke.width || 2;
    ctx.beginPath();
    ctx.moveTo(p1.x, p1.y);
    ctx.lineTo(p2.x, p2.y);
    ctx.stroke();
    ctx.restore();
  },

  eraseStrokesNear(x, y) {
    const drawings = this.currentTopicCanvas.drawings || [];
    if (drawings.length === 0) return;

    const eraseRadius = 26;
    const eraseRadiusSq = eraseRadius * eraseRadius;
    const origLen = drawings.length;

    this.currentTopicCanvas.drawings = drawings.filter(stroke => {
      if (!stroke.points) return false;
      for (let i = 0; i < stroke.points.length; i++) {
        const pt = stroke.points[i];
        const distSq = (pt.x - x) ** 2 + (pt.y - y) ** 2;
        if (distSq <= eraseRadiusSq) {
          return false;
        }
      }
      return true;
    });

    if (this.currentTopicCanvas.drawings.length !== origLen) {
      this.redrawCanvas();
      this.scheduleSaveCanvas();
    }
  },

  undoNotepadStroke() {
    if (this.currentTopicCanvas.drawings && this.currentTopicCanvas.drawings.length > 0) {
      this.currentTopicCanvas.drawings.pop();
      this.redrawCanvas();
      this.scheduleSaveCanvas();
    }
  },

  redrawCanvas() {
    const canvas = document.getElementById('notepad-drawing-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const isDark = document.documentElement.classList.contains('dark');
    const drawings = this.currentTopicCanvas.drawings || [];

    drawings.forEach(stroke => {
      if (!stroke.points || stroke.points.length === 0) return;
      const strokeColor = stroke.color === 'ink' ? (isDark ? '#EDEDED' : '#171717') : (stroke.color || (isDark ? '#EDEDED' : '#171717'));

      ctx.save();
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.globalAlpha = stroke.opacity || 1.0;
      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = stroke.width || 2;

      if (stroke.points.length === 1) {
        ctx.fillStyle = strokeColor;
        ctx.beginPath();
        ctx.arc(stroke.points[0].x, stroke.points[0].y, Math.max(1, (stroke.width || 2) / 2), 0, Math.PI * 2);
        ctx.fill();
      } else {
        ctx.beginPath();
        ctx.moveTo(stroke.points[0].x, stroke.points[0].y);
        for (let i = 1; i < stroke.points.length; i++) {
          ctx.lineTo(stroke.points[i].x, stroke.points[i].y);
        }
        ctx.stroke();
      }
      ctx.restore();
    });
  },

  // -------------------------------------------------------------
  // Movable Floating Text Notes Engine
  // -------------------------------------------------------------
  renderNotepadNotes() {
    const container = document.getElementById('notepad-notes-layer');
    if (!container) return;
    container.innerHTML = '';

    const notes = this.currentTopicCanvas.text_notes || [];
    notes.forEach(note => {
      const el = this.createNoteElement(note);
      container.appendChild(el);
    });

    if (window.lucide) window.lucide.createIcons();
  },

  createNoteElement(note) {
    const el = document.createElement('div');
    el.className = 'notepad-text-note absolute bg-card border border-border rounded-xl shadow-soft flex flex-col pointer-events-auto transition-shadow';
    el.style.left = `${note.x}px`;
    el.style.top = `${note.y}px`;
    el.style.width = `${note.width || 280}px`;
    el.style.zIndex = note.zIndex || 20;
    el.setAttribute('data-note-id', note.id);

    // Header / Drag Handle
    const header = document.createElement('div');
    header.className = 'notepad-text-note-handle flex items-center justify-between px-2.5 py-1.5 border-b border-border/70 bg-card-muted/50 rounded-t-xl select-none';
    header.innerHTML = `
      <div class="flex items-center gap-1.5 text-neutral-400">
        <i data-lucide="grip-horizontal" class="w-3.5 h-3.5"></i>
        <span class="text-[10px] font-mono uppercase tracking-wider text-neutral-400">Note</span>
      </div>
      <button onclick="App.deleteNotepadNote('${note.id}')" class="text-neutral-400 hover:text-rose-500 transition p-0.5 rounded" title="Delete note">
        <i data-lucide="x" class="w-3 h-3"></i>
      </button>
    `;

    header.addEventListener('pointerdown', (e) => {
      this.onNoteHandlePointerDown(e, note.id);
    });
    header.addEventListener('mousedown', (e) => {
      if (!window.PointerEvent) this.onNoteHandlePointerDown(e, note.id);
    });

    // Note Body
    const body = document.createElement('div');
    body.className = 'p-2 flex-1 flex flex-col';

    const textarea = document.createElement('textarea');
    textarea.className = 'notepad-note-textarea w-full bg-transparent resize-none outline-none font-sans text-xs text-ink placeholder:text-neutral-400 leading-relaxed';
    textarea.placeholder = 'Type note, formula, or exam trap...';
    textarea.value = note.text || '';
    textarea.rows = 2;

    const stopProp = (e) => e.stopPropagation();
    textarea.addEventListener('pointerdown', stopProp);
    textarea.addEventListener('mousedown', stopProp);
    textarea.addEventListener('click', stopProp);
    textarea.addEventListener('touchstart', stopProp);

    textarea.addEventListener('input', (e) => this.onNoteTextInput(e, note.id));
    textarea.addEventListener('focus', () => {
      this.maxNoteZIndex = (this.maxNoteZIndex || 30) + 1;
      note.zIndex = this.maxNoteZIndex;
      el.style.zIndex = note.zIndex;
    });

    body.appendChild(textarea);
    el.appendChild(header);
    el.appendChild(body);

    setTimeout(() => {
      textarea.style.height = 'auto';
      textarea.style.height = Math.max(52, textarea.scrollHeight) + 'px';
    }, 0);

    return el;
  },

  addFloatingTextNote() {
    const vp = document.getElementById('notepad-viewport');
    const x = vp ? (vp.scrollLeft + 60 + Math.floor(Math.random() * 30)) : 100;
    const y = vp ? (vp.scrollTop + 60 + Math.floor(Math.random() * 30)) : 100;
    this.addFloatingTextNoteAt(x, y, '');
  },

  addFloatingTextNoteAt(x, y, initialText = '') {
    if (!this.currentTopicCanvas.text_notes) {
      this.currentTopicCanvas.text_notes = [];
    }

    const noteId = 'note_' + Date.now() + '_' + Math.random().toString(36).substr(2, 4);
    this.maxNoteZIndex = (this.maxNoteZIndex || 30) + 1;

    const note = {
      id: noteId,
      x: Math.max(10, Math.round(x)),
      y: Math.max(10, Math.round(y)),
      text: initialText,
      width: 280,
      zIndex: this.maxNoteZIndex
    };

    this.currentTopicCanvas.text_notes.push(note);

    const container = document.getElementById('notepad-notes-layer');
    if (container) {
      const el = this.createNoteElement(note);
      container.appendChild(el);
      if (window.lucide) window.lucide.createIcons();
      const ta = el.querySelector('textarea');
      if (ta) ta.focus();
    }

    this.scheduleSaveCanvas();
  },

  onNoteTextInput(e, noteId) {
    const note = (this.currentTopicCanvas.text_notes || []).find(n => n.id === noteId);
    if (!note) return;
    note.text = e.target.value;
    e.target.style.height = 'auto';
    e.target.style.height = Math.max(52, e.target.scrollHeight) + 'px';
    this.scheduleSaveCanvas();
  },

  onNoteHandlePointerDown(e, noteId) {
    if (e.target.closest('button')) return;
    e.preventDefault();
    this.draggingNoteId = noteId;

    const note = (this.currentTopicCanvas.text_notes || []).find(n => n.id === noteId);
    if (!note) return;

    this.maxNoteZIndex = (this.maxNoteZIndex || 30) + 1;
    note.zIndex = this.maxNoteZIndex;
    const el = document.querySelector(`.notepad-text-note[data-note-id="${noteId}"]`);
    if (el) {
      el.style.zIndex = note.zIndex;
      el.classList.add('shadow-soft-md');
    }

    this.dragNoteOffset = {
      x: e.clientX - note.x,
      y: e.clientY - note.y
    };
  },

  // -------------------------------------------------------------
  // Screenshot & Image Upload Engine
  // -------------------------------------------------------------
  triggerNotepadImageUpload() {
    const fileInput = document.getElementById('notepad-image-file-input');
    if (fileInput) fileInput.click();
  },

  onNotepadImageFileSelected(e) {
    const file = e.target.files && e.target.files[0];
    if (file) {
      this.handleImageUploadFile(file);
    }
    e.target.value = '';
  },

  handleImageUploadFile(file, clientX = null, clientY = null) {
    if (!file || !file.type.startsWith('image/')) return;

    const reader = new FileReader();
    reader.onload = (loadEvt) => {
      const rawDataUrl = loadEvt.target.result;
      const img = new Image();
      img.onload = () => {
        // Optimize high-res screenshots to max 1200px to maintain crispness without SQLite bloat
        let targetW = img.naturalWidth || img.width;
        let targetH = img.naturalHeight || img.height;
        const maxDim = 1200;
        if (targetW > maxDim || targetH > maxDim) {
          if (targetW > targetH) {
            targetH = Math.round((targetH * maxDim) / targetW);
            targetW = maxDim;
          } else {
            targetW = Math.round((targetW * maxDim) / targetH);
            targetH = maxDim;
          }
        }

        const offCanvas = document.createElement('canvas');
        offCanvas.width = targetW;
        offCanvas.height = targetH;
        const ctx = offCanvas.getContext('2d');
        ctx.drawImage(img, 0, 0, targetW, targetH);
        const optimizedSrc = offCanvas.toDataURL('image/jpeg', 0.88);

        // Determine drop or viewport coordinates
        let x = 80;
        let y = 80;
        if (clientX !== null && clientY !== null) {
          const coords = this.getNotepadCanvasCoords({ clientX, clientY });
          x = coords.x - 100;
          y = coords.y - 40;
        } else {
          const vp = document.getElementById('notepad-viewport');
          if (vp) {
            x = vp.scrollLeft + 60 + Math.floor(Math.random() * 40);
            y = vp.scrollTop + 60 + Math.floor(Math.random() * 40);
          }
        }

        if (!this.currentTopicCanvas.images) {
          this.currentTopicCanvas.images = [];
        }

        const imgWidth = Math.min(Math.max(260, targetW), 440);
        const imageRecord = {
          id: 'img_' + Date.now() + '_' + Math.random().toString(36).substr(2, 4),
          src: optimizedSrc,
          title: file.name ? file.name.substring(0, 32) : 'Screenshot',
          x: Math.max(10, Math.round(x)),
          y: Math.max(10, Math.round(y)),
          width: imgWidth,
          zIndex: 12
        };

        this.currentTopicCanvas.images.push(imageRecord);
        this.renderNotepadImages();
        this.scheduleSaveCanvas();

        const hintEl = document.getElementById('notepad-tool-hint');
        if (hintEl) {
          hintEl.textContent = 'Screenshot added • Drag header to move • Draw on it with Pen or annotate';
        }
      };
      img.src = rawDataUrl;
    };
    reader.readAsDataURL(file);
  },

  renderNotepadImages() {
    const container = document.getElementById('notepad-images-layer');
    if (!container) return;
    container.innerHTML = '';

    const images = this.currentTopicCanvas.images || [];
    images.forEach(img => {
      const el = this.createImageCardElement(img);
      container.appendChild(el);
    });

    if (window.lucide) window.lucide.createIcons();
  },

  createImageCardElement(img) {
    const el = document.createElement('div');
    el.className = 'notepad-image-card absolute bg-card border border-border rounded-xl shadow-soft flex flex-col pointer-events-auto select-none overflow-visible transition-shadow';
    if (this.selectedImageId === img.id) {
      el.classList.add('selected');
    }
    el.style.left = `${img.x}px`;
    el.style.top = `${img.y}px`;
    el.style.width = `${img.width || 380}px`;
    el.style.zIndex = img.zIndex || 12;
    el.setAttribute('data-image-id', img.id);

    // 4 Corner Resize Handles (Mac Notes style)
    const corners = ['nw', 'ne', 'sw', 'se'];
    corners.forEach(c => {
      const h = document.createElement('div');
      h.className = `notepad-resize-handle notepad-resize-handle-${c}`;
      h.setAttribute('data-corner', c);
      h.title = 'Drag to resize';
      h.addEventListener('pointerdown', (e) => this.onImageCornerResizePointerDown(e, img.id, c));
      h.addEventListener('mousedown', (e) => this.onImageCornerResizePointerDown(e, img.id, c));
      el.appendChild(h);
    });

    // Header / Drag Handle
    const header = document.createElement('div');
    header.className = 'notepad-image-handle flex items-center justify-between px-2.5 py-1.5 border-b border-border/70 bg-card-muted/80 text-ink cursor-grab select-none rounded-t-xl';
    header.innerHTML = `
      <div class="flex items-center gap-1.5 text-neutral-400 min-w-0 pointer-events-none">
        <i data-lucide="image" class="w-3.5 h-3.5 text-neutral-400 shrink-0"></i>
        <span class="text-[10px] font-mono uppercase tracking-wider text-neutral-400 truncate max-w-[140px]">${img.title || 'Screenshot'}</span>
      </div>
      <div class="flex items-center gap-1 shrink-0">
        <button onclick="App.resizeNotepadImage('${img.id}', -50)" class="text-neutral-400 hover:text-ink p-0.5 rounded transition" title="Smaller (-50px)">
          <i data-lucide="zoom-out" class="w-3 h-3"></i>
        </button>
        <button onclick="App.resizeNotepadImage('${img.id}', 50)" class="text-neutral-400 hover:text-ink p-0.5 rounded transition" title="Larger (+50px)">
          <i data-lucide="zoom-in" class="w-3 h-3"></i>
        </button>
        <button onclick="App.deleteNotepadImage('${img.id}')" class="text-neutral-400 hover:text-rose-500 transition p-0.5 rounded ml-1" title="Delete screenshot (or press Backspace)">
          <i data-lucide="trash-2" class="w-3 h-3"></i>
        </button>
      </div>
    `;

    // Image Body
    const body = document.createElement('div');
    body.className = 'image-wrapper relative w-full bg-neutral-900/10 dark:bg-black/20 flex items-center justify-center p-1 cursor-grab rounded-b-xl overflow-hidden';
    
    const imgEl = document.createElement('img');
    imgEl.src = img.src;
    imgEl.alt = img.title || 'Lecture Screenshot';
    imgEl.className = 'w-full h-auto object-contain rounded-lg pointer-events-none block';
    imgEl.draggable = false;
    body.appendChild(imgEl);

    // Clicking / Dragging anywhere on the card starts moving it!
    const onStartDrag = (e) => {
      if (e.target.closest('button') || e.target.closest('.notepad-resize-handle')) return;
      e.preventDefault();
      e.stopPropagation();

      // If user is currently in a drawing tool, clicking on an image switches smoothly to Pointer
      if (this.notepadTool !== 'select') {
        this.setNotepadTool('select');
      }

      this.selectImageCard(img.id);

      this.draggingImageId = img.id;
      this.dragImageOffset = {
        x: e.clientX - img.x,
        y: e.clientY - img.y
      };

      el.classList.add('dragging');
    };

    el.addEventListener('pointerdown', onStartDrag);
    el.addEventListener('mousedown', onStartDrag);
    el.addEventListener('click', (e) => {
      e.stopPropagation();
      this.selectImageCard(img.id);
    });

    el.appendChild(header);
    el.appendChild(body);

    return el;
  },

  onImageCornerResizePointerDown(e, imgId, corner) {
    e.preventDefault();
    e.stopPropagation();
    const img = (this.currentTopicCanvas.images || []).find(i => i.id === imgId);
    if (!img) return;

    this.selectImageCard(imgId);
    this.resizingImageId = imgId;
    this.resizingCorner = corner;
    this.resizeStartX = e.clientX;
    this.resizeStartY = e.clientY;
    this.resizeStartWidth = img.width || 380;
    this.resizeStartLeft = img.x;
    this.resizeStartTop = img.y;
  },

  resizeNotepadImage(imgId, deltaWidth) {
    const img = (this.currentTopicCanvas.images || []).find(i => i.id === imgId);
    if (!img) return;

    img.width = Math.max(160, Math.min(1200, (img.width || 380) + deltaWidth));
    const el = document.querySelector(`.notepad-image-card[data-image-id="${imgId}"]`);
    if (el) {
      el.style.width = `${img.width}px`;
    }
    this.scheduleSaveCanvas();
  },

  deleteNotepadImage(imgId) {
    this.currentTopicCanvas.images = (this.currentTopicCanvas.images || []).filter(i => i.id !== imgId);
    const el = document.querySelector(`.notepad-image-card[data-image-id="${imgId}"]`);
    if (el) el.remove();
    if (this.selectedImageId === imgId) this.selectedImageId = null;
    this.scheduleSaveCanvas();
  },

  // Unified Pointer Drag for Notes and Images
  // -------------------------------------------------------------
  onNotepadGlobalPointerMove(e) {
    // 0. Board panning in Pointer mode
    if (this.isPanningCanvas) {
      const viewport = document.getElementById('notepad-viewport');
      if (viewport) {
        const dx = e.clientX - this.panStartX;
        const dy = e.clientY - this.panStartY;
        viewport.scrollLeft = this.panScrollLeft - dx;
        viewport.scrollTop = this.panScrollTop - dy;
      }
      return;
    }

    // 1. Dragging Text Note
    if (this.draggingNoteId) {
      const note = (this.currentTopicCanvas.text_notes || []).find(n => n.id === this.draggingNoteId);
      if (note) {
        const newX = Math.max(10, Math.min(2100, e.clientX - this.dragNoteOffset.x));
        const newY = Math.max(10, Math.min(1600, e.clientY - this.dragNoteOffset.y));
        note.x = Math.round(newX);
        note.y = Math.round(newY);

        const el = document.querySelector(`.notepad-text-note[data-note-id="${this.draggingNoteId}"]`);
        if (el) {
          el.style.left = `${note.x}px`;
          el.style.top = `${note.y}px`;
        }
      }
    }

    // 2. Dragging Screenshot Image Card anywhere on canvas
    if (this.draggingImageId) {
      const img = (this.currentTopicCanvas.images || []).find(i => i.id === this.draggingImageId);
      if (img) {
        const newX = Math.max(10, Math.min(2100, e.clientX - this.dragImageOffset.x));
        const newY = Math.max(10, Math.min(1600, e.clientY - this.dragImageOffset.y));
        img.x = Math.round(newX);
        img.y = Math.round(newY);

        const el = document.querySelector(`.notepad-image-card[data-image-id="${this.draggingImageId}"]`);
        if (el) {
          el.style.left = `${img.x}px`;
          el.style.top = `${img.y}px`;
        }
      }
    }

    // 3. Resizing Screenshot Image Card via corner handles (aspect ratio preserved)
    if (this.resizingImageId) {
      const img = (this.currentTopicCanvas.images || []).find(i => i.id === this.resizingImageId);
      if (img) {
        const dx = e.clientX - this.resizeStartX;
        let newWidth = this.resizeStartWidth;
        if (this.resizingCorner === 'se' || this.resizingCorner === 'ne') {
          newWidth = Math.max(160, Math.min(1200, this.resizeStartWidth + dx));
        } else {
          newWidth = Math.max(160, Math.min(1200, this.resizeStartWidth - dx));
          img.x = Math.max(10, Math.round(this.resizeStartLeft + (this.resizeStartWidth - newWidth)));
        }
        img.width = Math.round(newWidth);

        const el = document.querySelector(`.notepad-image-card[data-image-id="${this.resizingImageId}"]`);
        if (el) {
          el.style.width = `${img.width}px`;
          el.style.left = `${img.x}px`;
        }
      }
    }
  },

  onNotepadGlobalPointerUp(e) {
    let shouldSave = false;

    if (this.isPanningCanvas) {
      this.isPanningCanvas = false;
      const viewport = document.getElementById('notepad-viewport');
      if (viewport && this.notepadTool === 'select') {
        viewport.style.cursor = 'default';
      }
    }

    if (this.draggingNoteId) {
      const el = document.querySelector(`.notepad-text-note[data-note-id="${this.draggingNoteId}"]`);
      if (el) el.classList.remove('dragging', 'shadow-soft-md');
      this.draggingNoteId = null;
      shouldSave = true;
    }

    if (this.draggingImageId) {
      const el = document.querySelector(`.notepad-image-card[data-image-id="${this.draggingImageId}"]`);
      if (el) el.classList.remove('dragging');
      this.draggingImageId = null;
      shouldSave = true;
    }

    if (this.resizingImageId) {
      this.resizingImageId = null;
      this.resizingCorner = null;
      shouldSave = true;
    }

    if (shouldSave) {
      this.scheduleSaveCanvas();
    }
  },

  deleteNotepadNote(noteId) {
    this.currentTopicCanvas.text_notes = (this.currentTopicCanvas.text_notes || []).filter(n => n.id !== noteId);
    const el = document.querySelector(`.notepad-text-note[data-note-id="${noteId}"]`);
    if (el) el.remove();
    this.scheduleSaveCanvas();
  },

  // Bridge & Pin Integration
  // -------------------------------------------------------------
  renderCanvas() {
    this.redrawCanvas();
    this.renderNotepadNotes();
    this.renderNotepadImages();
    if (window.lucide) window.lucide.createIcons();
  },

  pinHeadingToCanvas(btn) {
    const headingEl = btn.closest('h1, h2, h3, h4, h5, h6, .notes-section, div');
    const title = headingEl ? headingEl.innerText.replace('📌', '').trim() : 'Pinned Concept';

    // Ensure Canvas pane is visible in Studio
    if (!this.paneState.canvas) {
      this.paneState.canvas = true;
      this.updateStudioLayout();
    }

    const vp = document.getElementById('notepad-viewport');
    const x = (vp ? vp.scrollLeft : 0) + 70 + Math.floor(Math.random() * 40);
    const y = (vp ? vp.scrollTop : 0) + 70 + Math.floor(Math.random() * 40);

    this.addFloatingTextNoteAt(x, y, `📌 ${title}`);
    alert(`📌 Pinned "${title.substring(0, 40)}..." to your lecture notepad!`);
  },

  pinChatToCanvas(msgIndex) {
    const msg = this.chatMessages[msgIndex];
    if (!msg) return;

    if (!this.paneState.canvas) {
      this.paneState.canvas = true;
      this.updateStudioLayout();
    }

    const vp = document.getElementById('notepad-viewport');
    const x = (vp ? vp.scrollLeft : 0) + 80 + Math.floor(Math.random() * 40);
    const y = (vp ? vp.scrollTop : 0) + 80 + Math.floor(Math.random() * 40);

    const snippet = msg.text.length > 300 ? msg.text.substring(0, 300) + '...' : msg.text;
    this.addFloatingTextNoteAt(x, y, `💡 Copilot AI Insight:\n${snippet}`);
    alert('📌 Copilot explanation clipped to your movable notepad!');
  },

  // Legacy aliases
  addCustomCanvasCard() {
    this.addFloatingTextNote();
  },

  addCustomCanvasCardAt(x, y) {
    this.addFloatingTextNoteAt(x, y, '');
  },

  deleteCanvasCard(id) {
    this.deleteNotepadNote(id);
  },

  clearCurrentCanvas() {
    if (confirm('Clear all drawings, screenshots and notes for this lecture notepad?')) {
      this.currentTopicCanvas = { drawings: [], text_notes: [], cards: [], images: [] };
      this.saveTopicCanvas(this.selectedTopicId);
      this.renderCanvas();
    }
  },

  // -------------------------------------------------------------
  // Canvas Persistence (SQLite + LocalStorage)
  // -------------------------------------------------------------
  scheduleSaveCanvas() {
    const indicator = document.getElementById('notepad-status-indicator');
    if (indicator) {
      indicator.textContent = 'Saving...';
      indicator.className = 'text-amber-500';
    }

    if (this.saveNotepadDebounceTimer) {
      clearTimeout(this.saveNotepadDebounceTimer);
    }

    this.saveNotepadDebounceTimer = setTimeout(() => {
      this.saveTopicCanvas(this.selectedTopicId);
    }, 400);
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
    if (!canvasData && !this.isStaticHost()) {
      try {
        const res = await fetch(`/api/topics/${topicId}/canvas`);
        if (res.ok) {
          canvasData = await res.json();
        }
      } catch (err) {
        console.warn('Could not load canvas from API, fallback to default', err);
      }
    }

    if (!canvasData) {
      canvasData = { drawings: [], text_notes: [], cards: [] };
    }

    if (!canvasData.drawings) canvasData.drawings = [];
    if (!canvasData.text_notes) canvasData.text_notes = [];
    if (!canvasData.images) canvasData.images = [];

    // Backward compatibility: Convert legacy card format to floating text notes if present
    if (canvasData.text_notes.length === 0 && canvasData.cards && canvasData.cards.length > 0) {
      canvasData.text_notes = canvasData.cards.map((c, i) => ({
        id: c.id || ('legacy_' + i),
        x: c.x || (60 + (i % 3) * 300),
        y: c.y || (60 + Math.floor(i / 3) * 180),
        text: (c.title ? `### ${c.title}\n` : '') + (c.content || ''),
        width: 280,
        zIndex: 20
      }));
    }

    this.currentTopicCanvas = canvasData;
    this.renderCanvas();

    const indicator = document.getElementById('notepad-status-indicator');
    if (indicator) {
      indicator.textContent = 'Auto-saved';
      indicator.className = 'text-emerald-500';
    }
  },

  async saveTopicCanvas(topicId) {
    if (!topicId) return;

    // Always persist to localStorage for instant recovery
    try {
      localStorage.setItem(`canvas_${topicId}`, JSON.stringify(this.currentTopicCanvas));
    } catch (e) {
      console.warn('LocalStorage save failed:', e);
    }

    // Persist to SQLite backend if not static
    if (!this.isStaticHost()) {
      try {
        await fetch(`/api/topics/${topicId}/canvas`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.currentTopicCanvas)
        });
      } catch (err) {
        console.warn('Failed to sync canvas to backend:', err);
      }
    }

    const indicator = document.getElementById('notepad-status-indicator');
    if (indicator) {
      indicator.textContent = 'Auto-saved';
      indicator.className = 'text-emerald-500';
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
      exam: document.getElementById('view-exam'),
      oneshot: document.getElementById('view-oneshot')
    };

    const tabs = {
      dashboard: document.getElementById('tab-dashboard'),
      notes: document.getElementById('tab-notes'),
      exam: document.getElementById('tab-exam'),
      oneshot: document.getElementById('tab-oneshot')
    };

    Object.keys(views).forEach(k => {
      const el = views[k];
      const tab = tabs[k];
      const isActive = (k === target);

      if (el) {
        if (isActive) {
          el.classList.remove('hidden');
          el.removeAttribute('style');
        } else {
          el.classList.add('hidden');
          el.removeAttribute('style');
        }
      }

      if (tab) {
        if (isActive) {
          tab.className = 'px-3 py-1 rounded-full bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900 font-medium text-xs transition shadow-soft-sm whitespace-nowrap';
        } else {
          tab.className = 'px-3 py-1 rounded-full text-neutral-500 hover:text-neutral-900 dark:hover:text-white font-medium text-xs transition whitespace-nowrap';
        }
      }
    });

    // Keep the unified global header visible across all views so navigation never disappears
    const globalHeader = document.getElementById('app-global-header');
    if (globalHeader) globalHeader.classList.remove('hidden');

    // 2. Update Drawer navigation active pills
    ['dashboard', 'notes', 'exam', 'oneshot'].forEach(k => {
      const drawerItem = document.getElementById(`drawer-nav-${k}`);
      if (drawerItem) {
        if (k === target) {
          drawerItem.className = 'w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold transition bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 shadow-soft-sm';
        } else {
          drawerItem.className = 'w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition text-ink hover:bg-muted';
        }
      }
    });

    if (target === 'dashboard') {
      this.renderDashboard();
    } else {
      if (window.FolioMotion) window.FolioMotion.stop3D();
      if (target === 'notes') {
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
      } else if (target === 'oneshot') {
        this.initOneShotView();
      }
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
    const workspace = document.getElementById('studio-workspace');
    const leftCol = document.getElementById('left-studio-column');
    const resizerNotesCol = document.getElementById('resizer-notes-column');
    const paneVideo = document.getElementById('pane-video');
    const resizerVideoCanvas = document.getElementById('resizer-video-canvas');

    // 1. Restore saved pane sizes
    const savedSidebarWidth = localStorage.getItem('study_engine_sidebar_width');
    if (savedSidebarWidth && sidebar) {
      sidebar.style.width = savedSidebarWidth;
    }
    const savedCopilotWidth = localStorage.getItem('study_engine_copilot_width');
    if (savedCopilotWidth && copilot) {
      copilot.style.width = savedCopilotWidth;
    }
    const savedLeftColWidth = localStorage.getItem('study_engine_left_col_width');
    if (savedLeftColWidth && leftCol) {
      leftCol.style.width = savedLeftColWidth;
    }
    const savedVideoHeight = localStorage.getItem('study_engine_video_pane_height');
    if (savedVideoHeight && paneVideo) {
      paneVideo.style.height = savedVideoHeight;
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

    // 5. Horizontal Resizer: Left Column (Video + Notepad) vs Right Column (Notes Reader)
    if (resizerNotesCol && leftCol && workspace) {
      let isDragging = false;
      const onMouseDown = (e) => {
        isDragging = true;
        e.preventDefault();
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
        resizerNotesCol.classList.add('resizer-active');
        leftCol.style.transition = 'none';
        window.addEventListener('mousemove', onMouseMove);
        window.addEventListener('mouseup', onMouseUp);
        window.addEventListener('pointermove', onMouseMove);
        window.addEventListener('pointerup', onMouseUp);
      };
      const onMouseMove = (e) => {
        if (!isDragging) return;
        const rect = workspace.getBoundingClientRect();
        let newWidth = e.clientX - rect.left;
        if (newWidth < 280) newWidth = 280;
        if (newWidth > rect.width - 280) newWidth = rect.width - 280;
        leftCol.style.width = `${newWidth}px`;
        if (this.redrawCanvas) this.redrawCanvas();
      };
      const onMouseUp = () => {
        if (!isDragging) return;
        isDragging = false;
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        resizerNotesCol.classList.remove('resizer-active');
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);
        window.removeEventListener('pointermove', onMouseMove);
        window.removeEventListener('pointerup', onMouseUp);
        localStorage.setItem('study_engine_left_col_width', leftCol.style.width);
        if (this.redrawCanvas) this.redrawCanvas();
      };
      resizerNotesCol.addEventListener('mousedown', onMouseDown);
      resizerNotesCol.addEventListener('pointerdown', onMouseDown);
    }

    // 6. Vertical Resizer: Top Video Pane vs Bottom-Left Canvas / Notepad
    if (resizerVideoCanvas && paneVideo && leftCol) {
      let isDragging = false;
      const onMouseDown = (e) => {
        isDragging = true;
        e.preventDefault();
        document.body.style.cursor = 'row-resize';
        document.body.style.userSelect = 'none';
        resizerVideoCanvas.classList.add('resizer-active');
        paneVideo.style.transition = 'none';
        window.addEventListener('mousemove', onMouseMove);
        window.addEventListener('mouseup', onMouseUp);
        window.addEventListener('pointermove', onMouseMove);
        window.addEventListener('pointerup', onMouseUp);
      };
      const onMouseMove = (e) => {
        if (!isDragging) return;
        const rect = leftCol.getBoundingClientRect();
        let newHeight = e.clientY - rect.top;
        if (newHeight < 160) newHeight = 160;
        if (newHeight > rect.height - 160) newHeight = rect.height - 160;
        paneVideo.style.height = `${newHeight}px`;
        if (this.redrawCanvas) this.redrawCanvas();
      };
      const onMouseUp = () => {
        if (!isDragging) return;
        isDragging = false;
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        resizerVideoCanvas.classList.remove('resizer-active');
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);
        window.removeEventListener('pointermove', onMouseMove);
        window.removeEventListener('pointerup', onMouseUp);
        localStorage.setItem('study_engine_video_pane_height', paneVideo.style.height);
        if (this.redrawCanvas) this.redrawCanvas();
      };
      resizerVideoCanvas.addEventListener('mousedown', onMouseDown);
      resizerVideoCanvas.addEventListener('pointerdown', onMouseDown);
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
    this.stopNotesVoice(true);
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

      // Render Context-Aware Key Moments & Speedrun Controls
      this.renderKeyMoments(data);

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
      if (slideGallery) {
        if (data.slides && data.slides.length > 0 && slideThumbs) {
          slideGallery.classList.remove('hidden');
          slideThumbs.innerHTML = data.slides.map(s => `
            <div class="rounded-xl overflow-hidden border border-neutral-200 dark:border-neutral-800 bg-neutral-900 aspect-video">
              <img src="${s.url}" alt="${s.filename}" class="w-full h-full object-cover">
            </div>
          `).join('');
        } else {
          slideGallery.classList.add('hidden');
        }
      }

    } catch (e) {
      contentEl.innerHTML = `<div class="text-rose-500 text-xs">Error loading notes: ${e}</div>`;
    }
    this.updateLectureNavButtons();
    this.prepareNotesVoiceSegments();
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


  getAllCurriculumTopics() {
    const list = [];
    if (!this.courses) return list;
    for (const c of this.courses) {
      for (const m of (c.modules || [])) {
        for (const t of (m.topics || [])) {
          list.push({
            id: t.id,
            title: t.title,
            duration: t.duration,
            video_id: t.video_id,
            youtube_url: t.youtube_url,
            courseId: c.id,
            courseName: c.name,
            moduleId: m.id,
            moduleName: m.name
          });
        }
      }
    }
    return list;
  },

  getAdjacentTopics(topicId = this.selectedTopicId) {
    const all = this.getAllCurriculumTopics();
    const idx = all.findIndex(t => t.id === topicId);
    if (idx === -1) {
      return { prev: null, next: null, current: null, index: -1, total: all.length };
    }
    return {
      prev: idx > 0 ? all[idx - 1] : null,
      next: idx < all.length - 1 ? all[idx + 1] : null,
      current: all[idx],
      index: idx,
      total: all.length
    };
  },

  goToNextTopic() {
    const { next } = this.getAdjacentTopics();
    if (next) {
      this.loadTopicNotes(next.id);
    }
  },

  goToPrevTopic() {
    const { prev } = this.getAdjacentTopics();
    if (prev) {
      this.loadTopicNotes(prev.id);
    }
  },

  updateLectureNavButtons() {
    const { prev, next, current, index, total } = this.getAdjacentTopics();

    // 1. Subheader navigation buttons
    const btnPrev = document.getElementById('btn-prev-lecture');
    const btnNext = document.getElementById('btn-next-lecture');
    const counterBadge = document.getElementById('lecture-index-counter');

    if (btnPrev) {
      btnPrev.disabled = !prev;
      btnPrev.title = prev ? `Previous: ${prev.title} (Shift+P)` : 'First lecture in curriculum';
      btnPrev.classList.toggle('opacity-30', !prev);
      btnPrev.classList.toggle('pointer-events-none', !prev);
    }

    if (btnNext) {
      btnNext.disabled = !next;
      btnNext.title = next ? `Next: ${next.title} (Shift+N)` : 'Final lecture in curriculum';
      btnNext.classList.toggle('opacity-30', !next);
      btnNext.classList.toggle('pointer-events-none', !next);
    }

    if (counterBadge && index >= 0) {
      counterBadge.textContent = `${index + 1}/${total}`;
      counterBadge.classList.remove('hidden');
    }

    // 2. Notes footer next lecture card
    const notesFooter = document.getElementById('notes-next-lecture-footer');
    if (notesFooter) {
      if (next) {
        notesFooter.classList.remove('hidden');
        const nextTitleEl = document.getElementById('notes-next-lecture-title');
        const nextModuleEl = document.getElementById('notes-next-lecture-module');
        if (nextTitleEl) nextTitleEl.textContent = next.title;
        if (nextModuleEl) nextModuleEl.textContent = `${next.courseName || ''} • ${next.moduleName || ''}`;
      } else {
        notesFooter.classList.add('hidden');
      }
    }

    if (window.lucide) window.lucide.createIcons();
  },
  // -------------------------------------------------------------
  // Exam Arena (Conceptual 2-Set Simulator)
  // -------------------------------------------------------------
  selectedExamSet: 1,

  setupExamView() {
    if (window.ExamHub) window.ExamHub.init();
    const select = document.getElementById('exam-module-select');
    if (!select) return;

    const options = [];
    this.courses.forEach(c => {
      c.modules.forEach(m => {
        options.push(`<option value="${m.id}">${c.name} - Module ${m.number}: ${m.name}</option>`);
      });
    });

    select.innerHTML = options.length ? options.join('') : '<option value="">No modules available</option>';
    this.onExamModuleChange();
  },

  selectExamSet(setNum) {
    this.selectedExamSet = setNum;
    const card1 = document.getElementById('exam-set-card-1');
    const card2 = document.getElementById('exam-set-card-2');
    if (card1 && card2) {
      if (setNum === 1) {
        card1.className = 'cursor-pointer p-4 rounded-2xl border-2 border-neutral-900 dark:border-white bg-card-muted transition relative';
        card2.className = 'cursor-pointer p-4 rounded-2xl border border-border hover:border-neutral-400 dark:hover:border-neutral-600 bg-card transition relative';
      } else {
        card2.className = 'cursor-pointer p-4 rounded-2xl border-2 border-neutral-900 dark:border-white bg-card-muted transition relative';
        card1.className = 'cursor-pointer p-4 rounded-2xl border border-border hover:border-neutral-400 dark:hover:border-neutral-600 bg-card transition relative';
      }
    }
  },

  async onExamModuleChange() {
    const select = document.getElementById('exam-module-select');
    if (!select) return;
    const moduleId = select.value;
    if (!moduleId) return;

    // Check for tests in static bundle or via API
    let tests = null;
    if (window.STUDY_DATA && window.STUDY_DATA.module_tests && window.STUDY_DATA.module_tests[moduleId]) {
      tests = window.STUDY_DATA.module_tests[moduleId];
    }

    try {
      const res = await fetch(`/api/modules/${moduleId}/tests`);
      if (res.ok) {
        const data = await res.json();
        if (data.tests && data.tests.length) tests = data.tests;
      }
    } catch (e) {}

    const count1El = document.getElementById('exam-set-1-count');
    const count2El = document.getElementById('exam-set-2-count');
    const title1El = document.getElementById('exam-set-1-title');
    const title2El = document.getElementById('exam-set-2-title');

    if (tests && tests.length >= 2) {
      const s1 = tests.find(t => t.set_number === 1) || tests[0];
      const s2 = tests.find(t => t.set_number === 2) || tests[1];
      if (count1El) count1El.textContent = `${s1.total_questions || (s1.questions && s1.questions.length) || 12} Questions`;
      if (count2El) count2El.textContent = `${s2.total_questions || (s2.questions && s2.questions.length) || 12} Questions`;
      if (title1El && s1.title) title1El.textContent = s1.title;
      if (title2El && s2.title) title2El.textContent = s2.title;
    } else {
      if (count1El) count1El.textContent = '~12 Questions';
      if (count2El) count2El.textContent = '~12 Questions';
    }
  },

  async generateModuleTestsForCurrent() {
    const select = document.getElementById('exam-module-select');
    if (!select || !select.value) return;
    const moduleId = select.value;

    const btn = document.getElementById('exam-generate-btn');
    const origHtml = btn ? btn.innerHTML : '';
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<i data-lucide="loader-2" class="w-3 h-3 animate-spin text-amber-500"></i> AI Synthesizing Tests...`;
    }

    try {
      const res = await fetch(`/api/modules/${moduleId}/generate-tests?force=true`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        alert('Successfully synthesized 2 conceptual test sets for this module!');
        await this.onExamModuleChange();
      } else {
        const err = await res.text();
        alert('Generation failed: ' + err);
      }
    } catch (e) {
      alert('Error connecting to backend: ' + e);
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = origHtml;
        if (window.lucide) window.lucide.createIcons();
      }
    }
  },

  async startExam() {
    const moduleId = document.getElementById('exam-module-select').value;
    if (!moduleId) {
      alert('Please select a module.');
      return;
    }

    try {
      let questions = [];
      let testMeta = null;

      // 1. Try static bundle module_tests
      if (window.STUDY_DATA && window.STUDY_DATA.module_tests && window.STUDY_DATA.module_tests[moduleId]) {
        const setObj = window.STUDY_DATA.module_tests[moduleId].find(t => t.set_number === this.selectedExamSet);
        if (setObj && setObj.questions && setObj.questions.length > 0) {
          questions = setObj.questions;
          testMeta = setObj;
        }
      }

      // 2. Try API endpoint for specific test set
      try {
        const res = await fetch(`/api/modules/${moduleId}/tests/${this.selectedExamSet}`);
        if (res.ok) {
          const data = await res.json();
          if (data && data.questions && data.questions.length > 0) {
            questions = data.questions;
            testMeta = data;
          }
        }
      } catch (err) {}

      // 3. Fallback to /exam?set_number=
      if (questions.length === 0) {
        try {
          const res = await fetch(`/api/modules/${moduleId}/exam?set_number=${this.selectedExamSet}`);
          if (res.ok) {
            const data = await res.json();
            if (data && data.mcqs && data.mcqs.length > 0) {
              questions = data.mcqs;
              testMeta = data;
            }
          }
        } catch (err) {}
      }

      // 4. Final fallback to static exams
      if (questions.length === 0 && window.STUDY_DATA && window.STUDY_DATA.exams && window.STUDY_DATA.exams[moduleId]) {
        questions = window.STUDY_DATA.exams[moduleId].mcqs || [];
      }

      if (!questions || questions.length === 0) {
        if (confirm('No conceptual tests synthesized for this module yet. Would you like AI to synthesize Set 1 & Set 2 now?')) {
          await this.generateModuleTestsForCurrent();
          return;
        }
        return;
      }

      this.examQuestions = questions;
      this.currentTestMeta = testMeta || { title: `Set ${this.selectedExamSet} Test` };
      this.currentQuestionIdx = 0;
      this.userAnswers = {};

      document.getElementById('exam-setup-box').classList.add('hidden');
      document.getElementById('exam-results-box').classList.add('hidden');
      document.getElementById('exam-runner-box').classList.remove('hidden');

      this.renderExamPalette();
      this.loadExamQuestion(0);
      if (window.lucide) window.lucide.createIcons();
    } catch (e) {
      alert('Failed to load exam: ' + e);
    }
  },

  renderExamPalette() {
    const palette = document.getElementById('exam-palette');
    if (!palette) return;

    palette.innerHTML = this.examQuestions.map((q, idx) => {
      const isAnswered = this.userAnswers[idx] && this.userAnswers[idx].length > 0;
      const isCurrent = this.currentQuestionIdx === idx;
      let btnClasses = 'w-7 h-7 rounded-lg text-xs font-mono font-medium transition flex items-center justify-center ';

      if (isCurrent) {
        btnClasses += 'ring-2 ring-neutral-900 dark:ring-white bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 font-bold';
      } else if (isAnswered) {
        btnClasses += 'bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30';
      } else {
        btnClasses += 'bg-card border border-border text-ink-secondary hover:text-ink hover:bg-muted';
      }

      return `<button onclick="App.loadExamQuestion(${idx})" class="${btnClasses}">${idx + 1}</button>`;
    }).join('');
  },

  loadExamQuestion(index) {
    this.currentQuestionIdx = index;
    const q = this.examQuestions[index];
    if (!q) return;

    const isMulti = q.type === 'multiple_choice' || (q.correct_indices && q.correct_indices.length > 1);

    document.getElementById('exam-q-counter').textContent = `Question ${index + 1} of ${this.examQuestions.length}`;
    
    const badgeEl = document.getElementById('exam-q-type-badge');
    if (badgeEl) {
      if (isMulti) {
        badgeEl.textContent = 'Multiple Correct (Select all that apply)';
        badgeEl.className = 'text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 font-semibold';
      } else {
        badgeEl.textContent = 'Single Choice';
        badgeEl.className = 'text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 font-semibold';
      }
    }

    const conceptEl = document.getElementById('exam-q-concept-badge');
    if (conceptEl) {
      conceptEl.textContent = q.key_concept ? `Concept: ${q.key_concept}` : '';
    }

    document.getElementById('exam-q-text').textContent = q.question;

    const optContainer = document.getElementById('exam-q-options');
    const selectedList = this.userAnswers[index] || [];

    optContainer.innerHTML = q.options.map((opt, optIdx) => {
      const isSelected = selectedList.includes(optIdx);
      const indicatorShape = isMulti ? 'rounded-md' : 'rounded-full';

      return `
        <button onclick="App.selectExamOption(${optIdx}, ${isMulti})" class="w-full text-left p-3.5 rounded-xl border text-xs sm:text-sm font-medium transition flex items-center justify-between gap-3 ${
          isSelected 
            ? 'border-neutral-900 bg-neutral-100 dark:border-white dark:bg-neutral-800/80 font-semibold text-ink shadow-sm' 
            : 'border-neutral-200 dark:border-neutral-800 hover:bg-neutral-50 dark:hover:bg-neutral-900/60 text-ink-secondary'
        }">
          <span class="leading-relaxed">${opt}</span>
          <span class="w-4 h-4 shrink-0 ${indicatorShape} border flex items-center justify-center ${
            isSelected 
              ? 'bg-neutral-900 dark:bg-white border-neutral-900 dark:border-white text-white dark:text-neutral-900' 
              : 'border-neutral-300 dark:border-neutral-700'
          }">
            ${isSelected ? (isMulti ? '<span class="text-[9px] font-bold">✓</span>' : '') : ''}
          </span>
        </button>
      `;
    }).join('');

    this.renderExamPalette();
  },

  selectExamOption(optIdx, isMulti) {
    if (!this.userAnswers[this.currentQuestionIdx]) {
      this.userAnswers[this.currentQuestionIdx] = [];
    }

    if (isMulti) {
      let current = this.userAnswers[this.currentQuestionIdx];
      if (current.includes(optIdx)) {
        this.userAnswers[this.currentQuestionIdx] = current.filter(x => x !== optIdx);
      } else {
        this.userAnswers[this.currentQuestionIdx].push(optIdx);
      }
    } else {
      this.userAnswers[this.currentQuestionIdx] = [optIdx];
    }

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
    let correctCount = 0;
    let wrongCount = 0;
    let unansweredCount = 0;
    let rawScore = 0.0;

    const totalQuestions = this.examQuestions.length;

    this.examQuestions.forEach((q, idx) => {
      const userSelected = this.userAnswers[idx] || [];
      const isMulti = q.type === 'multiple_choice' || (q.correct_indices && q.correct_indices.length > 1);

      let targetCorrect = [];
      if (Array.isArray(q.correct_indices)) {
        targetCorrect = q.correct_indices;
      } else if (Array.isArray(q.correct_index)) {
        targetCorrect = q.correct_index;
      } else if (typeof q.correct_index === 'number') {
        targetCorrect = [q.correct_index];
      }

      if (userSelected.length === 0) {
        unansweredCount++;
        return;
      }

      if (!isMulti) {
        const u = userSelected[0];
        if (targetCorrect.includes(u)) {
          correctCount++;
          rawScore += 1.0;
        } else {
          wrongCount++;
          rawScore -= 0.25;
        }
      } else {
        const uSet = new Set(userSelected);
        const cSet = new Set(targetCorrect);
        
        let hasWrongSelection = false;
        userSelected.forEach(opt => {
          if (!cSet.has(opt)) hasWrongSelection = true;
        });

        if (uSet.size === cSet.size && !hasWrongSelection) {
          correctCount++;
          rawScore += 1.0;
        } else if (!hasWrongSelection && uSet.size > 0) {
          const partial = (uSet.size / cSet.size) * 0.75;
          rawScore += partial;
          correctCount++;
        } else {
          wrongCount++;
          rawScore -= 0.25;
        }
      }
    });

    const finalScore = Math.max(0, rawScore);
    const accuracy = totalQuestions > 0 ? Math.round((correctCount / totalQuestions) * 100) : 0;

    document.getElementById('exam-score-display').textContent = finalScore.toFixed(2);
    document.getElementById('exam-max-score-display').textContent = `/ ${totalQuestions}.00`;
    document.getElementById('exam-stat-accuracy').textContent = `${accuracy}%`;
    document.getElementById('exam-stat-correct').textContent = correctCount;
    document.getElementById('exam-stat-wrong').textContent = wrongCount;
    document.getElementById('exam-stat-unanswered').textContent = unansweredCount;

    const titleEl = document.getElementById('exam-results-title');
    if (titleEl) {
      titleEl.textContent = this.currentTestMeta ? this.currentTestMeta.title : 'Diagnostic Results';
    }

    const switchBtn = document.getElementById('exam-switch-set-btn');
    if (switchBtn) {
      const nextSet = this.selectedExamSet === 1 ? 2 : 1;
      switchBtn.textContent = `Take Set ${nextSet}`;
    }

    const reviewContainer = document.getElementById('exam-review-container');
    if (reviewContainer) {
      reviewContainer.innerHTML = this.examQuestions.map((q, idx) => {
        const userSelected = this.userAnswers[idx] || [];
        const isMulti = q.type === 'multiple_choice' || (q.correct_indices && q.correct_indices.length > 1);

        let targetCorrect = [];
        if (Array.isArray(q.correct_indices)) targetCorrect = q.correct_indices;
        else if (Array.isArray(q.correct_index)) targetCorrect = q.correct_index;
        else if (typeof q.correct_index === 'number') targetCorrect = [q.correct_index];

        const uSet = new Set(userSelected);
        const cSet = new Set(targetCorrect);

        let statusText = 'Skipped';
        let statusBadgeClass = 'bg-neutral-500/10 text-neutral-500 border-neutral-500/20';

        if (userSelected.length > 0) {
          let hasWrong = userSelected.some(o => !cSet.has(o));
          if (uSet.size === cSet.size && !hasWrong) {
            statusText = 'Correct (+1.00)';
            statusBadgeClass = 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20';
          } else if (!hasWrong) {
            statusText = 'Partially Correct';
            statusBadgeClass = 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20';
          } else {
            statusText = 'Incorrect (-0.25)';
            statusBadgeClass = 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20';
          }
        }

        const optionsHtml = q.options.map((opt, optIdx) => {
          const isUserPicked = uSet.has(optIdx);
          const isCorrect = cSet.has(optIdx);

          let optBorder = 'border-border bg-card';
          let markIcon = '';

          if (isCorrect) {
            optBorder = 'border-emerald-500 bg-emerald-500/10 text-emerald-800 dark:text-emerald-200 font-medium';
            markIcon = '<span class="text-xs font-bold text-emerald-600 dark:text-emerald-400">✓ Correct</span>';
          } else if (isUserPicked && !isCorrect) {
            optBorder = 'border-rose-500 bg-rose-500/10 text-rose-800 dark:text-rose-200 font-medium';
            markIcon = '<span class="text-xs font-bold text-rose-600 dark:text-rose-400">✕ Your Choice</span>';
          }

          return `
            <div class="p-3 rounded-xl border text-xs flex items-center justify-between gap-3 ${optBorder}">
              <span>${opt}</span>
              ${markIcon}
            </div>
          `;
        }).join('');

        return `
          <div class="rounded-2xl border border-border bg-card p-5 space-y-4 shadow-soft">
            <div class="flex items-center justify-between border-b border-border pb-3">
              <span class="text-xs font-mono font-bold text-ink">Q${idx + 1}. ${q.key_concept || 'Conceptual Principle'}</span>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded-full border ${statusBadgeClass} font-semibold">${statusText}</span>
            </div>

            <p class="text-sm font-medium leading-relaxed text-ink">${q.question}</p>

            <div class="space-y-2">
              ${optionsHtml}
            </div>

            <div class="mt-3 p-4 rounded-xl bg-muted/60 border border-border/80 space-y-2">
              <div class="text-[11px] font-mono uppercase tracking-wider text-ink font-semibold flex items-center gap-1.5">
                <i data-lucide="book-open" class="w-3.5 h-3.5 text-accent"></i> Core Conceptual Explanation
              </div>
              <p class="text-xs text-ink-secondary leading-relaxed">${q.explanation || 'Refer to lecture notes for complete derivation.'}</p>

              ${q.trap_warning ? `
                <div class="mt-2 pt-2 border-t border-border/60">
                  <div class="text-[11px] font-mono uppercase tracking-wider text-rose-600 dark:text-rose-400 font-semibold flex items-center gap-1.5">
                    <i data-lucide="alert-triangle" class="w-3.5 h-3.5"></i> Examiner Gotcha Radar
                  </div>
                  <p class="text-xs text-rose-600/90 dark:text-rose-400/90 mt-0.5 leading-relaxed">${q.trap_warning}</p>
                </div>
              ` : ''}
            </div>
          </div>
        `;
      }).join('');
    }

    document.getElementById('exam-runner-box').classList.add('hidden');
    document.getElementById('exam-results-box').classList.remove('hidden');
    if (window.lucide) window.lucide.createIcons();
  },

  retakeExam() {
    this.startExam();
  },

  switchExamSetFromResults() {
    const nextSet = this.selectedExamSet === 1 ? 2 : 1;
    this.selectExamSet(nextSet);
    this.startExam();
  },

  returnToExamSetup() {
    document.getElementById('exam-runner-box').classList.add('hidden');
    document.getElementById('exam-results-box').classList.add('hidden');
    document.getElementById('exam-setup-box').classList.remove('hidden');
    this.onExamModuleChange();
  },

  // -------------------------------------------------------------
  // Studio Neural Audio Narrator (Edge-TTS Broadcast-Grade Voices)
  // -------------------------------------------------------------
  async initNotesVoice() {
    if (!this.notesAudioElement) {
      this.notesAudioElement = new Audio();
      this.notesAudioElement.preload = 'auto';

      this.notesAudioElement.addEventListener('timeupdate', () => this.onAudioTimeUpdate());
      this.notesAudioElement.addEventListener('ended', () => this.onVoiceFinished());
      this.notesAudioElement.addEventListener('play', () => {
        this.isVoicePlaying = true;
        this.isVoicePaused = false;
        this.updateVoicePlayButtonUI(true);
      });
      this.notesAudioElement.addEventListener('pause', () => {
        if (!this.notesAudioElement.ended && !this.isVoiceSynthesizing) {
          this.isVoicePlaying = false;
          this.isVoicePaused = true;
          this.updateVoicePlayButtonUI(false);
          const statusEl = document.getElementById('voice-status-text');
          if (statusEl) statusEl.textContent = 'Paused';
        }
      });
      this.notesAudioElement.addEventListener('error', (e) => {
        console.warn('Audio playback error:', e);
        this.isVoicePlaying = false;
        this.isVoiceSynthesizing = false;
        this.updateVoicePlayButtonUI(false);
        const statusEl = document.getElementById('voice-status-text');
        if (statusEl) statusEl.textContent = 'Audio error';
      });
    }

    const savedVoice = localStorage.getItem('study_engine_neural_voice');
    if (savedVoice) this.selectedVoiceKey = savedVoice;

    await this.loadCuratedVoices();
  },

  async loadCuratedVoices() {
    try {
      const res = await fetch('/api/voices');
      if (res.ok) {
        const data = await res.json();
        this.curatedVoices = data.voices || [];
        if (!this.selectedVoiceKey && data.default) {
          this.selectedVoiceKey = data.default;
        }
      }
    } catch (e) {
      this.curatedVoices = [
        { key: 'christopher', label: 'Christopher (Warm Narrator)' },
        { key: 'jenny', label: 'Jenny (Soothing Studio)' },
        { key: 'ryan', label: 'Ryan (BBC British Male)' },
        { key: 'sonia', label: 'Sonia (Soft British Female)' },
        { key: 'neerja', label: 'Neerja (Natural Indian English)' },
        { key: 'guy', label: 'Guy (Conversational US)' }
      ];
    }

    const dropdown = document.getElementById('voice-select-dropdown');
    if (dropdown && this.curatedVoices.length > 0) {
      dropdown.innerHTML = this.curatedVoices.map(v => 
        `<option value="${v.key}" ${v.key === this.selectedVoiceKey ? 'selected' : ''}>${v.label || v.name}</option>`
      ).join('');
      dropdown.value = this.selectedVoiceKey;
    }
  },

  prepareNotesVoiceSegments() {
    this.stopNotesVoice(true);

    const contentEl = document.getElementById('notes-content-body');
    if (!contentEl) return;

    const nodes = contentEl.querySelectorAll('p, h1, h2, h3, h4, li, blockquote');
    const segments = [];
    let segIdx = 0;
    let totalWordCount = 0;

    nodes.forEach(node => {
      const clone = node.cloneNode(true);
      clone.querySelectorAll('.pin-note-btn, .timestamp-jump-btn, button, script, style').forEach(el => el.remove());

      const rawText = clone.textContent.trim();
      if (!rawText || rawText.length < 3) return;

      const words = rawText.split(/\s+/).filter(Boolean);
      totalWordCount += words.length;

      node.classList.add('voice-readable-segment');
      node.setAttribute('data-voice-idx', segIdx);
      node.onclick = (e) => {
        if (e.target.closest('.pin-note-btn') || e.target.closest('.timestamp-jump-btn')) return;
        App.jumpToVoiceSegment(segIdx, true);
      };

      segments.push({
        idx: segIdx,
        element: node,
        text: rawText.toLowerCase(),
        wordCount: words.length
      });

      segIdx++;
    });

    this.voiceSegments = segments;
    this.voiceCurrentSentenceIdx = -1;
    this.currentAudioTopicId = null;
    this.voiceSentences = [];

    this.voiceTotalSeconds = Math.max(10, Math.round((totalWordCount / 140) * 60));

    const totalTimeEl = document.getElementById('voice-time-total');
    if (totalTimeEl) {
      totalTimeEl.textContent = `~${this.formatVoiceSeconds(this.voiceTotalSeconds)}`;
    }
    const elapsedEl = document.getElementById('voice-time-elapsed');
    if (elapsedEl) elapsedEl.textContent = '0:00';
    const pctEl = document.getElementById('voice-progress-pct');
    if (pctEl) pctEl.textContent = '0%';
    const slider = document.getElementById('voice-progress-slider');
    if (slider) slider.value = 0;

    const statusEl = document.getElementById('voice-status-text');
    if (statusEl) {
      statusEl.textContent = 'Ready (Studio Neural Voice)';
    }
  },

  formatVoiceSeconds(sec) {
    if (!sec || isNaN(sec)) return '0:00';
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  },

  async toggleNotesVoice() {
    if (this.isVoicePlaying) {
      this.pauseNotesVoice();
    } else {
      await this.playNotesVoice();
    }
  },

  async playNotesVoice() {
    if (!this.selectedTopicId) return;

    const needFetch = !this.notesAudioElement.src || 
                      this.currentAudioTopicId !== this.selectedTopicId || 
                      this.currentAudioVoiceKey !== this.selectedVoiceKey;

    if (needFetch) {
      await this.loadTopicNeuralAudio(this.selectedTopicId, this.selectedVoiceKey);
    }

    if (this.notesAudioElement && this.notesAudioElement.src) {
      try {
        this.notesAudioElement.playbackRate = this.voiceRate || 1.0;
        await this.notesAudioElement.play();
        this.isVoicePlaying = true;
        this.isVoicePaused = false;
        this.updateVoicePlayButtonUI(true);
      } catch (err) {
        console.warn('Playback play failed:', err);
      }
    }
  },

  async loadTopicNeuralAudio(topicId, voiceKey) {
    const statusEl = document.getElementById('voice-status-text');
    const playBtn = document.getElementById('voice-play-btn');

    this.isVoiceSynthesizing = true;
    if (statusEl) statusEl.textContent = 'Synthesizing Studio Audio...';
    if (playBtn) playBtn.disabled = true;

    try {
      const res = await fetch(`/api/topics/${topicId}/audio?voice=${encodeURIComponent(voiceKey)}`);
      if (!res.ok) throw new Error('Failed to load audio from server');

      const data = await res.json();
      this.notesAudioElement.src = data.audio_url;
      this.currentAudioTopicId = topicId;
      this.currentAudioVoiceKey = voiceKey;
      this.voiceSentences = data.sentences || [];
      this.voiceTotalSeconds = Math.round(data.total_duration || 0);

      const totalTimeEl = document.getElementById('voice-time-total');
      if (totalTimeEl && this.voiceTotalSeconds > 0) {
        totalTimeEl.textContent = this.formatVoiceSeconds(this.voiceTotalSeconds);
      }
    } catch (e) {
      console.error('Error loading neural audio:', e);
      if (statusEl) statusEl.textContent = 'Failed to load audio';
    } finally {
      this.isVoiceSynthesizing = false;
      if (playBtn) playBtn.disabled = false;
    }
  },

  pauseNotesVoice() {
    if (this.notesAudioElement) {
      this.notesAudioElement.pause();
    }
    this.isVoicePlaying = false;
    this.isVoicePaused = true;
    this.updateVoicePlayButtonUI(false);
    this.markCurrentPausedSegment();

    const statusEl = document.getElementById('voice-status-text');
    if (statusEl) statusEl.textContent = 'Paused';
  },

  stopNotesVoice(silent = false) {
    if (this.notesAudioElement) {
      this.notesAudioElement.pause();
      this.notesAudioElement.currentTime = 0;
    }
    this.isVoicePlaying = false;
    this.isVoicePaused = false;
    this.voiceCurrentSentenceIdx = -1;
    this.clearVoiceHighlights();
    this.updateVoicePlayButtonUI(false);

    const elapsedEl = document.getElementById('voice-time-elapsed');
    if (elapsedEl) elapsedEl.textContent = '0:00';
    const pctEl = document.getElementById('voice-progress-pct');
    if (pctEl) pctEl.textContent = '0%';
    const slider = document.getElementById('voice-progress-slider');
    if (slider) slider.value = 0;

    const statusEl = document.getElementById('voice-status-text');
    if (statusEl && !silent) {
      statusEl.textContent = 'Ready (Studio Neural Voice)';
    }
  },

  skipNotesVoice(direction) {
    if (!this.notesAudioElement) return;
    const skipAmount = direction * 15;
    const dur = this.notesAudioElement.duration || this.voiceTotalSeconds || 1;
    const target = Math.max(0, Math.min(dur - 0.5, this.notesAudioElement.currentTime + skipAmount));
    this.notesAudioElement.currentTime = target;
    if (!this.isVoicePlaying) {
      this.playNotesVoice();
    }
  },

  onVoiceScrub(pctVal) {
    if (!this.notesAudioElement) return;
    const dur = this.notesAudioElement.duration || this.voiceTotalSeconds;
    if (!dur) return;
    const targetTime = (parseFloat(pctVal) / 100) * dur;
    this.notesAudioElement.currentTime = targetTime;
  },

  async jumpToVoiceSegment(segIdx, autoPlay = true) {
    if (!this.voiceSegments || !this.voiceSegments[segIdx]) return;
    const seg = this.voiceSegments[segIdx];

    if (!this.notesAudioElement.src || this.currentAudioTopicId !== this.selectedTopicId || this.currentAudioVoiceKey !== this.selectedVoiceKey) {
      await this.loadTopicNeuralAudio(this.selectedTopicId, this.selectedVoiceKey);
    }

    let targetTime = 0;
    if (this.voiceSentences && this.voiceSentences.length > 0) {
      const segTextClean = seg.text.replace(/[^a-z0-9]/g, '');
      const match = this.voiceSentences.find(s => {
        const sClean = s.text.toLowerCase().replace(/[^a-z0-9]/g, '');
        return segTextClean.includes(sClean) || sClean.includes(segTextClean);
      });
      if (match) {
        targetTime = match.start;
      } else {
        const ratio = segIdx / Math.max(1, this.voiceSegments.length - 1);
        targetTime = ratio * (this.notesAudioElement.duration || this.voiceTotalSeconds);
      }
    } else {
      const ratio = segIdx / Math.max(1, this.voiceSegments.length - 1);
      targetTime = ratio * (this.notesAudioElement.duration || this.voiceTotalSeconds);
    }

    this.notesAudioElement.currentTime = Math.max(0, targetTime);

    if (autoPlay) {
      await this.playNotesVoice();
    } else {
      this.highlightSegmentByIndex(segIdx, 'paused');
    }
  },

  async setNotesVoice(voiceKey) {
    if (this.selectedVoiceKey === voiceKey) return;
    this.selectedVoiceKey = voiceKey;
    localStorage.setItem('study_engine_neural_voice', voiceKey);

    const wasPlaying = this.isVoicePlaying;
    const savedTime = this.notesAudioElement ? this.notesAudioElement.currentTime : 0;

    if (this.notesAudioElement) {
      this.notesAudioElement.pause();
    }

    if (this.selectedTopicId) {
      await this.loadTopicNeuralAudio(this.selectedTopicId, this.selectedVoiceKey);
      if (this.notesAudioElement) {
        this.notesAudioElement.currentTime = savedTime;
        if (wasPlaying) {
          await this.playNotesVoice();
        }
      }
    }
  },

  setVoiceRate(rate) {
    this.voiceRate = parseFloat(rate);
    if (this.notesAudioElement) {
      this.notesAudioElement.playbackRate = this.voiceRate;
    }

    document.querySelectorAll('.voice-rate-btn').forEach(btn => {
      const bRate = parseFloat(btn.getAttribute('data-rate'));
      if (bRate === this.voiceRate) {
        btn.className = 'voice-rate-btn px-1.5 py-0.5 rounded font-semibold bg-neutral-900 text-white dark:bg-white dark:text-neutral-900';
      } else {
        btn.className = 'voice-rate-btn px-1.5 py-0.5 rounded text-neutral-400 hover:text-ink';
      }
    });
  },

  onAudioTimeUpdate() {
    if (!this.notesAudioElement) return;

    const cur = this.notesAudioElement.currentTime;
    const dur = this.notesAudioElement.duration || this.voiceTotalSeconds || 1;

    const pct = Math.min(100, Math.round((cur / dur) * 100));
    const slider = document.getElementById('voice-progress-slider');
    if (slider && !slider.matches(':active')) slider.value = pct;

    const pctEl = document.getElementById('voice-progress-pct');
    if (pctEl) pctEl.textContent = `${pct}%`;

    const elapsedEl = document.getElementById('voice-time-elapsed');
    if (elapsedEl) elapsedEl.textContent = this.formatVoiceSeconds(cur);

    if (this.voiceSentences && this.voiceSentences.length > 0 && this.voiceSegments && this.voiceSegments.length > 0) {
      const activeSent = this.voiceSentences.find(s => cur >= s.start && cur <= s.end);
      if (activeSent) {
        const sClean = activeSent.text.toLowerCase().replace(/[^a-z0-9]/g, '');
        const matchingSeg = this.voiceSegments.find(seg => {
          const segClean = seg.text.replace(/[^a-z0-9]/g, '');
          return segClean.includes(sClean) || sClean.includes(segClean);
        });

        if (matchingSeg && matchingSeg.idx !== this.voiceCurrentSentenceIdx) {
          this.voiceCurrentSentenceIdx = matchingSeg.idx;
          this.highlightSegmentByIndex(matchingSeg.idx, 'active');
        }
      }
    }
  },

  markCurrentPausedSegment() {
    if (this.voiceCurrentSentenceIdx >= 0) {
      this.highlightSegmentByIndex(this.voiceCurrentSentenceIdx, 'paused');
    }
  },

  highlightSegmentByIndex(idx, mode = 'active') {
    this.clearVoiceHighlights();
    if (!this.voiceSegments || idx < 0 || idx >= this.voiceSegments.length) return;

    const seg = this.voiceSegments[idx];
    if (seg && seg.element) {
      const cls = mode === 'active' ? 'voice-reading-active' : 'voice-reading-paused';
      seg.element.classList.add(cls);

      const pane = document.getElementById('pane-notes');
      if (pane) {
        const segRect = seg.element.getBoundingClientRect();
        const paneRect = pane.getBoundingClientRect();
        if (segRect.top < paneRect.top + 80 || segRect.bottom > paneRect.bottom - 80) {
          seg.element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }
    }
  },

  clearVoiceHighlights() {
    if (this.voiceSegments) {
      this.voiceSegments.forEach(s => {
        if (s.element) {
          s.element.classList.remove('voice-reading-active', 'voice-reading-paused');
        }
      });
    }
  },

  updateVoicePlayButtonUI(isPlaying) {
    const playBtn = document.getElementById('voice-play-btn');
    const playIcon = document.getElementById('voice-play-icon');
    const waveEl = document.getElementById('voice-audio-wave');
    const statusEl = document.getElementById('voice-status-text');

    if (playIcon) {
      playIcon.setAttribute('data-lucide', isPlaying ? 'pause' : 'play');
      if (isPlaying) {
        playIcon.classList.remove('ml-0.5');
      } else {
        playIcon.classList.add('ml-0.5');
      }
    }
    if (waveEl) {
      if (isPlaying) {
        waveEl.classList.remove('hidden');
        waveEl.classList.add('flex');
      } else {
        waveEl.classList.add('hidden');
        waveEl.classList.remove('flex');
      }
    }
    if (statusEl) {
      if (isPlaying) {
        const voiceObj = this.curatedVoices.find(v => v.key === this.selectedVoiceKey);
        const name = voiceObj ? (voiceObj.label || voiceObj.name) : 'Studio Neural Voice';
        statusEl.textContent = `Playing: ${name}`;
      } else if (this.isVoicePaused) {
        statusEl.textContent = 'Paused';
      }
    }

    if (window.lucide) window.lucide.createIcons();
  },

  onVoiceFinished() {
    this.stopNotesVoice(true);
    const statusEl = document.getElementById('voice-status-text');
    if (statusEl) statusEl.textContent = 'Finished Reading Notes';
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
  // One-Shot Revision & Master Formula View Controller
  // -------------------------------------------------------------
  currentOneShotCourseId: '2989cdfe',
  currentOneShotCFMode: 'formulas',

  launchOneShot(courseId) {
    if (courseId) this.currentOneShotCourseId = courseId;
    this.switchView('oneshot');
  },

  async initOneShotView() {
    this.renderOneShotCoursePills();
    await this.renderOneShotContent();
  },

  renderOneShotCoursePills() {
    const container = document.getElementById('oneshot-course-pills');
    if (!container || !this.courses) return;

    container.innerHTML = this.courses.map(c => {
      const isSelected = c.id === this.currentOneShotCourseId;
      const activeCls = isSelected 
        ? 'bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 font-semibold shadow-soft-sm'
        : 'bg-card border border-border text-neutral-500 hover:text-ink hover:bg-muted font-medium';
      
      const badgeIcon = c.id === '2989cdfe' ? '📐 ' : '📖 ';
      return `
        <button onclick="App.selectOneShotCourse('${c.id}')" 
          class="px-3 py-1 rounded-full text-xs transition shrink-0 flex items-center gap-1.5 ${activeCls}">
          <span>${badgeIcon}${this.escapeHtml(c.name)}</span>
        </button>
      `;
    }).join('');

    const cfModeContainer = document.getElementById('oneshot-cf-mode-container');
    if (cfModeContainer) {
      if (this.currentOneShotCourseId === '2989cdfe') {
        cfModeContainer.classList.remove('hidden');
        this.updateOneShotCFModeButtons();
      } else {
        cfModeContainer.classList.add('hidden');
      }
    }
  },

  updateOneShotCFModeButtons() {
    const btnFormulas = document.getElementById('btn-oneshot-cf-formulas');
    const btnNotes = document.getElementById('btn-oneshot-cf-notes');
    if (!btnFormulas || !btnNotes) return;

    if (this.currentOneShotCFMode === 'formulas') {
      btnFormulas.className = 'px-3 py-1 rounded-full font-medium transition text-xs flex items-center gap-1.5 bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 shadow-soft-sm';
      btnNotes.className = 'px-3 py-1 rounded-full font-medium transition text-xs flex items-center gap-1.5 text-neutral-500 hover:text-ink';
    } else {
      btnNotes.className = 'px-3 py-1 rounded-full font-medium transition text-xs flex items-center gap-1.5 bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 shadow-soft-sm';
      btnFormulas.className = 'px-3 py-1 rounded-full font-medium transition text-xs flex items-center gap-1.5 text-neutral-500 hover:text-ink';
    }
  },

  selectOneShotCourse(courseId) {
    this.currentOneShotCourseId = courseId;
    this.renderOneShotCoursePills();
    this.renderOneShotContent();
  },

  setOneShotCFMode(mode) {
    this.currentOneShotCFMode = mode;
    this.updateOneShotCFModeButtons();
    this.renderOneShotContent();
  },

  async renderOneShotContent() {
    const bodyEl = document.getElementById('oneshot-content-body');
    if (window.VisualCram) {
      await window.VisualCram.loadForCourse(this.currentOneShotCourseId);
    }
    const tocListEl = document.getElementById('oneshot-toc-list');
    const tocCounterEl = document.getElementById('oneshot-toc-counter');
    const readTimeEl = document.getElementById('oneshot-read-time');
    if (!bodyEl) return;

    bodyEl.innerHTML = '<div class="p-8 text-center text-xs text-neutral-400 font-mono">Loading revision notes...</div>';

    let data = null;
    if (window.STUDY_DATA && window.STUDY_DATA.one_shots && window.STUDY_DATA.one_shots[this.currentOneShotCourseId]) {
      data = window.STUDY_DATA.one_shots[this.currentOneShotCourseId];
    }

    if (!data) {
      try {
        const res = await fetch(`/api/courses/${this.currentOneShotCourseId}/one-shot`);
        if (res.ok) {
          data = await res.json();
        }
      } catch (e) {
        console.warn('Failed to fetch one-shot from backend:', e);
      }
    }

    if (!data) {
      bodyEl.innerHTML = '<div class="p-8 text-center text-xs text-neutral-400">No one-shot revision notes available for this subject.</div>';
      return;
    }

    let markdown = '';
    const isCF = this.currentOneShotCourseId === '2989cdfe';
    if (isCF && this.currentOneShotCFMode === 'formulas') {
      markdown = data.formula_sheet_markdown || data.one_shot_markdown || '';
    } else {
      markdown = data.one_shot_markdown || '';
    }

    if (!markdown.trim()) {
      bodyEl.innerHTML = '<div class="p-8 text-center text-xs text-neutral-400">Notes are being compiled.</div>';
      return;
    }

    // Render markdown
    bodyEl.innerHTML = window.marked ? window.marked.parse(markdown) : markdown;

    // Render KaTeX Math
    if (window.renderMathInElement) {
      window.renderMathInElement(bodyEl, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '$', right: '$', display: false }
        ],
        throwOnError: false
      });
    }

    // Update reading time estimate
    const words = markdown.trim().split(/\s+/).length;
    const minutes = Math.max(5, Math.ceil(words / 200));
    if (readTimeEl) {
      readTimeEl.textContent = `⚡ ~${minutes} min cram`;
    }

    // Generate Floating Table of Contents
    if (tocListEl) {
      const allH2 = Array.from(bodyEl.querySelectorAll('h2'));
      const headings = allH2.filter(h => {
        const t = h.textContent.trim().toLowerCase();
        return t.startsWith('module ') || t.includes('formula') || t.includes('variable') || t.includes('legend') || t.includes('navigation');
      });
      let tocHtml = '';
      headings.forEach((h, idx) => {
        const text = h.textContent.replace(/^[#\s]+/, '').trim();
        const anchorId = h.id || `oneshot-sec-${idx}`;
        h.id = anchorId;
        tocHtml += `
          <a href="#${anchorId}" onclick="App.scrollToOneShotHeading(event, '${anchorId}')"
            class="block px-2.5 py-1.5 rounded-lg text-neutral-500 hover:text-ink hover:bg-muted transition truncate text-[11px]">
            ${this.escapeHtml(text)}
          </a>
        `;
      });
      tocListEl.innerHTML = tocHtml || '<div class="text-[11px] text-neutral-400 p-2">Index populated</div>';
      if (tocCounterEl) {
        tocCounterEl.textContent = `${headings.length} Modules`;
      }
    }

    if (window.lucide) window.lucide.createIcons();

    // Scroll to top of content container
    const container = document.getElementById('oneshot-content-container');
    if (container) container.scrollTop = 0;
  },

  scrollToOneShotHeading(e, anchorId) {
    if (e) e.preventDefault();
    const target = document.getElementById(anchorId);
    const container = document.getElementById('oneshot-content-container');
    if (target && container) {
      const cRect = container.getBoundingClientRect();
      const tRect = target.getBoundingClientRect();
      const targetTop = container.scrollTop + (tRect.top - cRect.top) - 24;
      container.scrollTo({ top: Math.max(0, targetTop), behavior: 'smooth' });

      // Highlight active link in TOC
      const links = document.querySelectorAll('#oneshot-toc-list a');
      links.forEach(a => {
        if (a.getAttribute('href') === `#${anchorId}`) {
          a.classList.add('bg-muted', 'font-medium', 'text-ink');
          a.classList.remove('text-neutral-500');
        } else {
          a.classList.remove('bg-muted', 'font-medium', 'text-ink');
          a.classList.add('text-neutral-500');
        }
      });
    }
  },

  printOneShot() {
    window.print();
  },

  // -------------------------------------------------------------
  // Settings
  // -------------------------------------------------------------
};

window.App = App;

window.addEventListener('DOMContentLoaded', () => {
  App.init();
});

