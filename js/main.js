// Portfolio interactions: theme toggle, mobile nav, project filters,
// scroll reveal, active nav link and a lightweight animated "airflow" hero.
(function () {
  'use strict';

  var root = document.documentElement;

  // ---------- Theme ----------
  var themeBtn = document.querySelector('.theme-toggle');
  function currentTheme() {
    var t = root.getAttribute('data-theme');
    if (t) return t;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  root.setAttribute('data-theme', currentTheme());
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var next = currentTheme() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
    });
  }

  // ---------- Mobile nav ----------
  var toggle = document.querySelector('.nav-toggle');
  var links = document.getElementById('nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', function () {
      var open = links.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
    });
    links.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        links.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // ---------- Header border on scroll ----------
  var header = document.querySelector('.site-header');
  function onScroll() {
    if (header) header.classList.toggle('scrolled', window.scrollY > 8);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // ---------- Project filters ----------
  var filters = document.querySelectorAll('.filter');
  var cards = document.querySelectorAll('.card[data-category]');
  filters.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var f = btn.getAttribute('data-filter');
      filters.forEach(function (b) { b.classList.toggle('active', b === btn); });
      cards.forEach(function (c) {
        c.classList.toggle('hidden', f !== 'all' && c.getAttribute('data-category') !== f);
      });
    });
  });

  // ---------- Reveal on scroll + active nav ----------
  if ('IntersectionObserver' in window) {
    var revealEls = document.querySelectorAll('.section-title, .card, .timeline-item, .edu-card, .skill-group, .interest, .about-grid > *');
    revealEls.forEach(function (el) { el.classList.add('reveal'); });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('visible'); io.unobserve(en.target); }
      });
    }, { threshold: 0.12 });
    revealEls.forEach(function (el) { io.observe(el); });

    var navMap = {};
    document.querySelectorAll('.nav-links a[href^="#"]').forEach(function (a) {
      navMap[a.getAttribute('href').slice(1)] = a;
    });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var a = navMap[en.target.id];
        if (a && en.isIntersecting) {
          Object.keys(navMap).forEach(function (k) { navMap[k].classList.remove('active'); });
          a.classList.add('active');
        }
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    document.querySelectorAll('main section[id]').forEach(function (s) { spy.observe(s); });
  }

  // ---------- Footer year ----------
  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  // ---------- Hero airflow canvas ----------
  // Streamlines bending around an aerofoil-ish obstacle. Pure 2D canvas, no libraries.
  var canvas = document.getElementById('flow-canvas');
  if (!canvas || !canvas.getContext) return;
  var ctx = canvas.getContext('2d');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var W, H, dpr, particles = [];

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = canvas.clientWidth; H = canvas.clientHeight;
    canvas.width = W * dpr; canvas.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var n = Math.round(Math.min(160, W / 8));
    particles = [];
    for (var i = 0; i < n; i++) particles.push(spawn(true));
  }

  function spawn(anywhere) {
    return { x: anywhere ? Math.random() * W : -10, y: Math.random() * H, life: 0 };
  }

  // Potential flow around a cylinder, placed right of centre.
  function velocity(x, y) {
    var cx = W * 0.75, cy = H * 0.5, R = Math.min(W, H) * 0.16;
    var dx = (x - cx) / R, dy = (y - cy) / R;
    var r2 = dx * dx + dy * dy;
    if (r2 < 1) r2 = 1;
    var r4 = r2 * r2;
    var u = 1 - (dx * dx - dy * dy) / r4;
    var v = -(2 * dx * dy) / r4;
    return [u, v];
  }

  function strokeColor() {
    return currentTheme() === 'dark' ? 'rgba(91,157,255,0.35)' : 'rgba(31,111,235,0.28)';
  }

  function step() {
    ctx.fillStyle = currentTheme() === 'dark' ? 'rgba(11,16,23,0.12)' : 'rgba(247,248,250,0.14)';
    ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = strokeColor();
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    for (var i = 0; i < particles.length; i++) {
      var p = particles[i];
      var vel = velocity(p.x, p.y);
      var speed = 1.6;
      var nx = p.x + vel[0] * speed, ny = p.y + vel[1] * speed;
      ctx.moveTo(p.x, p.y); ctx.lineTo(nx, ny);
      p.x = nx; p.y = ny; p.life++;
      if (p.x > W + 10 || p.y < -10 || p.y > H + 10 || p.life > 900) particles[i] = spawn(false);
    }
    ctx.stroke();
    if (!reduce) requestAnimationFrame(step);
  }

  resize();
  window.addEventListener('resize', resize);
  if (reduce) { for (var k = 0; k < 200; k++) step(); } else { requestAnimationFrame(step); }
})();
