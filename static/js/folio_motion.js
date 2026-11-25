/**
 * Folio Motion & 3D Architectural Backdrop
 * - Interactive Three.js Folded-Folio Wireframe & Faceted Prism (pauses automatically off-Dashboard)
 * - GSAP + ScrollTrigger entrance & scroll-linked timeline
 * - Tactile mouse-tilt on subject cards
 */
window.FolioMotion = {
  renderer: null,
  scene: null,
  camera: null,
  group: null,
  rafId: null,
  isRunning: false,
  mouseX: 0,
  mouseY: 0,
  scrollProgress: 0,

  init() {
    this.initHero3D();
    this.initScrollAnimations();
    this.bindTiltCards();
  },

  prefersReducedMotion() {
    return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  },

  initHero3D() {
    const canvas = document.getElementById('folio-hero-canvas');
    if (!canvas || !window.THREE || this.prefersReducedMotion()) return;

    // Clean up prior instance if re-initialized
    if (this.renderer) {
      this.stop3D();
      this.renderer.dispose();
    }

    const parent = canvas.parentElement;
    const w = parent ? parent.clientWidth : 420;
    const h = parent ? parent.clientHeight : 320;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(40, w / Math.max(1, h), 0.1, 100);
    camera.position.set(0, 0, 5.2);

    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: false, powerPreference: 'low-power' });
    renderer.setPixelRatio(1);
    renderer.setSize(w, h, false);

    const group = new THREE.Group();

    // Inner faceted architectural crystal
    const geo = new THREE.IcosahedronGeometry(1.35, 0);
    const isDark = document.documentElement.classList.contains('dark');
    const accentHex = isDark ? 0xd4a359 : 0xb07d32;
    const inkHex = isDark ? 0xf2f1ee : 0x181715;

    const solidMat = new THREE.MeshStandardMaterial({
      color: accentHex,
      roughness: 0.35,
      metalness: 0.65,
      transparent: true,
      opacity: isDark ? 0.14 : 0.10,
      flatShading: true
    });
    const coreMesh = new THREE.Mesh(geo, solidMat);
    group.add(coreMesh);

    const wireGeo = new THREE.EdgesGeometry(geo);
    const wireMat = new THREE.LineBasicMaterial({
      color: accentHex,
      transparent: true,
      opacity: isDark ? 0.55 : 0.45
    });
    const wireMesh = new THREE.LineSegments(wireGeo, wireMat);
    group.add(wireMesh);

    // Outer precision orbital ring
    const ringGeo = new THREE.TorusGeometry(2.05, 0.008, 8, 96);
    const ringMat = new THREE.MeshBasicMaterial({
      color: inkHex,
      transparent: true,
      opacity: isDark ? 0.18 : 0.14
    });
    const ring1 = new THREE.Mesh(ringGeo, ringMat);
    ring1.rotation.x = Math.PI * 0.35;
    ring1.rotation.y = Math.PI * 0.15;
    group.add(ring1);

    const ring2 = new THREE.Mesh(ringGeo, ringMat);
    ring2.scale.set(0.82, 0.82, 0.82);
    ring2.rotation.x = -Math.PI * 0.28;
    ring2.rotation.z = Math.PI * 0.4;
    group.add(ring2);

    // Subtle ambient + directional key light
    scene.add(new THREE.AmbientLight(0xffffff, 0.9));
    const dirLight = new THREE.DirectionalLight(accentHex, 1.4);
    dirLight.position.set(4, 5, 4);
    scene.add(dirLight);

    scene.add(group);

    this.renderer = renderer;
    this.scene = scene;
    this.camera = camera;
    this.group = group;
    this._coreMat = solidMat;
    this._wireMat = wireMat;
    this._ringMat = ringMat;

    if (!this._eventsBound) {
      this._eventsBound = true;
      window.addEventListener('mousemove', (e) => {
        this.mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
        this.mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
        this._lastActivity = Date.now();
      }, { passive: true });

      document.addEventListener('visibilitychange', () => {
        if (document.hidden) this.stop3D();
        else if (window.App && window.App.currentView === 'dashboard') this.start3D();
      });

      window.addEventListener('resize', () => this.resize3D(), { passive: true });

      const dashEl = document.getElementById('view-dashboard');
      if (dashEl) {
        dashEl.addEventListener('scroll', () => {
          const maxScroll = Math.max(1, dashEl.scrollHeight - dashEl.clientHeight);
          this.scrollProgress = dashEl.scrollTop / maxScroll;
        }, { passive: true });
      }
    }

    this.start3D();
  },

  updateThemeColors() {
    if (!this._coreMat) return;
    const isDark = document.documentElement.classList.contains('dark');
    const accentHex = isDark ? 0xd4a359 : 0xb07d32;
    const inkHex = isDark ? 0xf2f1ee : 0x181715;
    this._coreMat.color.setHex(accentHex);
    this._coreMat.opacity = isDark ? 0.14 : 0.10;
    this._wireMat.color.setHex(accentHex);
    this._wireMat.opacity = isDark ? 0.55 : 0.45;
    this._ringMat.color.setHex(inkHex);
  },

  resize3D() {
    const canvas = document.getElementById('folio-hero-canvas');
    if (!canvas || !this.renderer || !this.camera) return;
    const parent = canvas.parentElement;
    if (!parent) return;
    const w = parent.clientWidth;
    const h = parent.clientHeight;
    if (w < 10 || h < 10) return;
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h, false);
  },

  start3D() {
    if (this.isRunning || !this.renderer || this.prefersReducedMotion() || document.hidden) return;
    this.isRunning = true;
    let lastFrame = 0;
    const tick = (now) => {
      if (!this.isRunning) return;
      this.rafId = requestAnimationFrame(tick);
      // Cap at ~24 FPS to save battery & prevent Mac thermal throttling
      if (now - lastFrame < 42) return;
      lastFrame = now;
      if (this.group) {
        this.group.rotation.y += 0.004;
        this.group.rotation.x += (this.mouseY * 0.25 + this.scrollProgress * 0.6 - this.group.rotation.x) * 0.06;
        this.group.rotation.z += (this.mouseX * 0.20 - this.group.rotation.z) * 0.06;
      }
      this.renderer.render(this.scene, this.camera);
    };
    this.rafId = requestAnimationFrame(tick);
  },

  stop3D() {
    this.isRunning = false;
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
  },

  initScrollAnimations() {
    if (!window.gsap || this.prefersReducedMotion()) return;
    if (window.ScrollTrigger) gsap.registerPlugin(ScrollTrigger);

    // Crisp hero stagger once
    const heroEls = document.querySelectorAll('.folio-hero-stagger');
    if (heroEls.length) {
      gsap.fromTo(heroEls,
        { y: 14, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.55, stagger: 0.07, ease: 'power3.out', clearProps: 'transform' }
      );
    }

    // Scroll-scrubbed progress bar inside Dashboard exam timeline
    const timelineFill = document.getElementById('folio-timeline-progress');
    const dashEl = document.getElementById('view-dashboard');
    if (timelineFill && dashEl && window.ScrollTrigger) {
      gsap.to(timelineFill, {
        scaleX: 1,
        ease: 'none',
        scrollTrigger: {
          trigger: '#folio-exam-timeline',
          scroller: '#view-dashboard',
          start: 'top 85%',
          end: 'bottom 55%',
          scrub: true
        }
      });
    }
  },

  bindTiltCards() {
    if (this.prefersReducedMotion()) return;
    document.querySelectorAll('.folio-tilt-card').forEach(card => {
      if (card.dataset.tiltBound) return;
      card.dataset.tiltBound = '1';
      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width - 0.5;
        const y = (e.clientY - rect.top) / rect.height - 0.5;
        card.style.transform = `perspective(900px) rotateX(${(-y * 4).toFixed(2)}deg) rotateY(${(x * 4).toFixed(2)}deg) translateY(-2px)`;
      });
      card.addEventListener('mouseleave', () => {
        card.style.transform = '';
      });
    });
  }
};
