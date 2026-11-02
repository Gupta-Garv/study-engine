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

  async init() {
    this.initTheme();
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
      const res = await fetch(`/api/modules/${this.selectedModuleId}/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ urls_text: text, extract_slides: extractSlides })
      });
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
    try {
      await fetch(`/api/topics/${topicId}/retry`, { method: 'POST' });
      await this.loadCourses();
      this.renderModuleTopicsList(this.selectedModuleId);
    } catch (e) {
      alert('Retry error: ' + e);
    }
  },

  async recurateModule() {
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
  // Study Hall / Notes Reader
  // -------------------------------------------------------------
  renderNotesSidebar() {
    const tree = document.getElementById('notes-syllabus-tree');
    if (!tree) return;

    if (this.courses.length === 0) {
      tree.innerHTML = '<div class="text-xs text-neutral-400 p-4">Add courses in Syllabus first.</div>';
      return;
    }

    tree.innerHTML = this.courses.map(c => `
      <div class="space-y-1">
        <div class="text-[11px] font-mono uppercase tracking-wider text-neutral-400 px-2 py-1 font-semibold">${c.name}</div>
        <div class="space-y-2 pl-2">
          ${c.modules.map(m => `
            <div class="space-y-0.5">
              <div class="text-xs font-medium text-neutral-500 px-2">Mod ${m.number}: ${m.name}</div>
              <div class="space-y-0.5 pl-2 border-l border-neutral-200 dark:border-neutral-800">
                ${m.topics.map(t => `
                  <button onclick="App.loadTopicNotes('${t.id}')" class="w-full text-left text-xs px-2.5 py-1.5 rounded-lg flex items-center justify-between gap-2 transition ${
                    t.id === this.selectedTopicId ? 'bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900 font-medium' : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800'
                  }">
                    <span class="truncate">${t.title}</span>
                    <span class="w-2 h-2 rounded-full ${t.status === 'completed' ? 'bg-emerald-500' : 'bg-neutral-300 dark:bg-neutral-700'}"></span>
                  </button>
                `).join('')}
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `).join('');
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
    this.renderNotesSidebar();

    const contentEl = document.getElementById('notes-content-body');
    contentEl.innerHTML = '<div class="text-center py-20 text-xs text-neutral-400">Loading synthesized notes...</div>';

    let data = null;
    if (window.STUDY_DATA && window.STUDY_DATA.topics && window.STUDY_DATA.topics[topicId]) {
      data = window.STUDY_DATA.topics[topicId];
    }
    try {
      const res = await fetch(`/api/topics/${topicId}`);
      if (res.ok) data = await res.json();
    } catch (e) {}

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

    let examData = null;
    if (window.STUDY_DATA && window.STUDY_DATA.exams && window.STUDY_DATA.exams[moduleId]) {
      examData = window.STUDY_DATA.exams[moduleId];
    }
    try {
      const res = await fetch(`/api/modules/${moduleId}/exam`);
      if (res.ok) examData = await res.json();
    } catch (e) {}

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

window.addEventListener('DOMContentLoaded', () => {
  App.init();
});

