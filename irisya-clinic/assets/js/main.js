/* İrisya Clinic · page behaviour */

// Clinic WhatsApp number: country code + number, digits only.
const WHATSAPP_NUMBER = '905000000000';
const WHATSAPP_DEFAULT_MSG = "Hi İrisya Clinic, I'd like a free shade plan and a quote for eye colour change.";

(() => {
  'use strict';
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const canHover = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  const waLink = (msg) => `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(msg)}`;
  const openWhatsApp = (msg) => window.open(waLink(msg), '_blank', 'noopener');
  const inView = (el, cb, threshold = 0.25) => new IntersectionObserver((en) => cb(en[0].isIntersecting), { threshold }).observe(el);

  /* ---------- Missing photos ----------
     Every photo points at assets/img/content/<file>. If a file is missing, the slot
     shows a labelled frame with the file name, so it's obvious what goes there. */
  const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const placeholder = (label, file, w, h) => {
    const big = w >= 220 && h >= 140;
    const fs = Math.round(Math.max(13, Math.min(w / 24, h / 9, 30)));
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" preserveAspectRatio="xMidYMid slice">
<rect width="${w}" height="${h}" fill="#0B2F6B"/>
<rect x="8" y="8" width="${w - 16}" height="${h - 16}" rx="10" fill="none" stroke="#A8C7E3" stroke-opacity=".5" stroke-width="1.5" stroke-dasharray="7 6"/>
${big ? `<g font-family="Figtree, Arial, sans-serif" text-anchor="middle"><text x="${w / 2}" y="${h / 2}" font-size="${fs}" font-weight="700" fill="#fff">${esc(label)}</text>
<text x="${w / 2}" y="${h / 2 + fs * 1.4}" font-size="${Math.round(fs * 0.7)}" fill="#A8C7E3">content/${esc(file)}</text></g>` : ''}</svg>`;
  };
  const watchPhoto = (img) => {
    const fail = () => {
      if (img.classList.contains('is-ph')) return;
      const file = img.getAttribute('src').split('/').pop();
      const w = img.clientWidth || +img.getAttribute('width') || 800;
      const h = img.clientHeight || +img.getAttribute('height') || 500;
      const pic = img.closest('picture');
      if (pic) $$('source', pic).forEach((s) => s.remove());
      img.classList.add('is-ph');
      img.title = `${img.dataset.ph}: assets/img/content/${file}`;
      img.src = `data:image/svg+xml,${encodeURIComponent(placeholder(img.dataset.ph, file, Math.round(w), Math.round(h)))}`;
    };
    if (img.complete) { if (!img.naturalWidth) fail(); } else img.addEventListener('error', fail, { once: true });
  };
  const watchPhotos = (root = document) => $$('img[data-ph]', root).forEach(watchPhoto);
  watchPhotos();

  /* ---------- Toast ---------- */
  const toastEl = $('#toast');
  let toastTimer;
  const toast = (msg, ms = 3600) => {
    toastEl.textContent = msg;
    toastEl.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove('show'), ms);
  };

  /* ---------- WhatsApp links (data-whatsapp="custom message" overrides the default) ---------- */
  $$('[data-whatsapp]').forEach((a) => {
    a.href = waLink(a.dataset.whatsapp || WHATSAPP_DEFAULT_MSG);
    a.target = '_blank';
    a.rel = 'noopener';
  });

  /* ---------- Announcement bar ---------- */
  const announce = $('#announce');
  let closed = false;
  try { closed = sessionStorage.getItem('irisya-announce') === 'closed'; } catch (e) { /* storage blocked */ }
  if (closed) announce.hidden = true;
  $('#announceClose').addEventListener('click', () => {
    announce.hidden = true;
    try { sessionStorage.setItem('irisya-announce', 'closed'); } catch (e) { /* storage blocked */ }
  });

  /* ---------- Nav: navy after 40px, mobile menu ---------- */
  const nav = $('#nav');
  const menuBtn = $('#menuBtn');
  const waFloat = $('.wa-float');
  const onScroll = () => {
    const y = window.scrollY;
    nav.classList.toggle('scrolled', y > 40);
    waFloat.classList.toggle('show', y > 700);
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });
  const setMenu = (open) => {
    nav.classList.toggle('open', open);
    menuBtn.setAttribute('aria-expanded', String(open));
    menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    $('use', menuBtn).setAttribute('href', open ? '#i-x' : '#i-menu');
  };
  menuBtn.addEventListener('click', () => setMenu(!nav.classList.contains('open')));
  $$('#mobileMenu a').forEach((a) => a.addEventListener('click', () => setMenu(false)));
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && nav.classList.contains('open')) { setMenu(false); menuBtn.focus(); } });
  window.addEventListener('resize', () => { if (window.innerWidth > 1023) setMenu(false); });

  /* ---------- Hero film ----------
     The poster paints first. The film loads once the hero is on screen, but not with
     reduced motion or data saver on; then the round button can still start it. */
  const hero = $('.hero');
  const film = $('#heroVideo');
  if (hero && film) {
    // chapter cuts of the edit in seconds (CUES in hero-film/irisya/build.py)
    const CUES = [
      [0, 'Laser eye colour change'],
      [1.75, 'Istanbul'],
      [4.75, 'Airport pickup'],
      [7.375, 'Eye exam first'],
      [9.625, 'Your shade, planned'],
      [13, 'Laser eye colour change'],
    ];
    const START_AT = 1; // hero.webp is this frame, so poster and film line up
    const toggle = $('#heroToggle');
    const reelN = $('#reelN');
    const reelLabel = $('#reelLabel');
    const reelBar = $('#reelBar');
    const saveData = !!(navigator.connection && navigator.connection.saveData);
    let wanted = !reduceMotion && !saveData;
    let visible = true;
    let available = true;
    let started = false;

    const load = () => {
      if (film.querySelector('source')) return;
      const portrait = window.matchMedia('(max-aspect-ratio: 4/5) and (max-width: 700px)').matches;
      const need = Math.max(window.innerWidth, window.innerHeight * 16 / 9) * Math.min(window.devicePixelRatio || 1, 2);
      const base = portrait ? film.dataset.portrait : need > 1500 ? film.dataset.hd : film.dataset.sd;
      // Safari decodes VP9 in software on many devices, so it gets H.264 straight away
      const safari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
      const exts = safari ? ['mp4'] : ['webm', 'mp4'];
      exts.forEach((ext, i) => {
        const s = document.createElement('source');
        s.src = `${base}.${ext}${film.dataset.v ? `?v=${film.dataset.v}` : ''}`;
        s.type = ext === 'webm' ? 'video/webm; codecs="vp9"' : 'video/mp4';
        // no file at all: keep the poster and drop the button
        if (i === exts.length - 1) s.addEventListener('error', () => { available = false; toggle.hidden = true; });
        film.appendChild(s);
      });
      film.addEventListener('loadedmetadata', () => { if (!started) film.currentTime = START_AT; }, { once: true });
      film.load();
    };
    const sync = () => {
      if (!available) return;
      if (wanted && visible && !document.hidden) {
        load();
        const p = film.play();
        // autoplay refused (iOS low power mode, for one): stay on the poster and offer play
        if (p && p.catch) p.catch((e) => { if (e && e.name === 'NotAllowedError') setWanted(false); });
      } else if (!film.paused) film.pause();
    };
    function setWanted(v) {
      wanted = v;
      hero.classList.toggle('film-paused', !v);
      toggle.setAttribute('aria-label', v ? 'Pause background video' : 'Play background video');
      toggle.hidden = false;
      sync();
    }
    toggle.addEventListener('click', () => setWanted(!wanted));
    film.addEventListener('playing', () => {
      toggle.hidden = false;
      if (!started) { started = true; hero.classList.add('film-on'); }
    });
    if (!wanted) setWanted(false);
    new IntersectionObserver((en) => { visible = en[0].isIntersecting; sync(); }, { threshold: 0.02 }).observe(hero);
    document.addEventListener('visibilitychange', sync);

    // the caption follows the cuts
    const chapter = {};
    CUES.forEach(([, label]) => { if (!(label in chapter)) chapter[label] = Object.keys(chapter).length + 1; });
    const onFrame = () => {
      const t = film.currentTime;
      let i = CUES.length - 1;
      while (i > 0 && CUES[i][0] > t) i--;
      const label = CUES[i][1];
      if (reelLabel.textContent !== label) {
        reelLabel.textContent = label;
        reelN.textContent = String(chapter[label]).padStart(2, '0');
        reelLabel.classList.remove('swap');
        void reelLabel.offsetWidth; // restart the animation
        reelLabel.classList.add('swap');
      }
      if (film.duration) reelBar.style.transform = `scaleX(${t / film.duration})`;
    };
    let ticking = false;
    const tick = () => { ticking = false; onFrame(); schedule(); };
    function schedule() {
      if (ticking || film.paused) return;
      ticking = true;
      if (film.requestVideoFrameCallback) film.requestVideoFrameCallback(tick);
      else requestAnimationFrame(tick);
    }
    film.addEventListener('play', schedule);
    sync();
  }

  /* ---------- Hero form → WhatsApp ---------- */
  const plan = $('#plan');
  // a <select> is as wide as its longest option; size each one to the option it shows
  const picks = $$('.pick select', plan);
  const sizer = document.createElement('span');
  sizer.setAttribute('aria-hidden', 'true');
  sizer.style.cssText = 'position:absolute;left:-9999px;top:0;visibility:hidden;white-space:pre';
  document.body.appendChild(sizer);
  const fitPick = (sel) => {
    const cs = getComputedStyle(sel);
    sizer.style.font = cs.font;
    sizer.style.letterSpacing = cs.letterSpacing;
    sizer.textContent = sel.options[sel.selectedIndex].text;
    sel.style.width = `${Math.ceil(sizer.getBoundingClientRect().width + parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight)) + 2}px`;
  };
  const fitPicks = () => picks.forEach(fitPick);
  picks.forEach((sel) => sel.addEventListener('change', () => fitPick(sel)));
  fitPicks();
  if (document.fonts) document.fonts.ready.then(fitPicks);
  window.addEventListener('resize', fitPicks);
  const photos = $('#planPhotos');
  const filesChip = $('#planFiles');
  photos.addEventListener('change', () => {
    const n = photos.files ? photos.files.length : 0;
    filesChip.hidden = !n;
    if (n) $('span', filesChip).textContent = n === 1 ? photos.files[0].name : `${n} photos added`;
  });
  $('button', filesChip).addEventListener('click', () => { photos.value = ''; filesChip.hidden = true; });
  plan.addEventListener('submit', (e) => {
    e.preventDefault();
    const now = $('#pNow').value;
    const want = $('#pWant').value;
    const from = $('#pFrom').value;
    const lines = [
      'Hi İrisya Clinic,',
      `my eyes are ${now} and ${want ? `I'd like ${want}` : "I'd like you to suggest a shade"}.`,
      from ? `I'd be flying in from ${from}.` : '',
      'Could you send me a shade plan and a quote?',
    ];
    const hasPhotos = photos.files && photos.files.length > 0;
    if (hasPhotos) lines.push("I'll attach my eye photos here.");
    openWhatsApp(lines.filter(Boolean).join('\n'));
    toast(hasPhotos ? 'WhatsApp is opening. Attach your photos in the chat, they don’t travel with the link.' : 'WhatsApp is opening with your message.');
  });

  /* ---------- Sample trips ---------- */
  const TRIPS = [
    {
      text: '<mark>Glacier Blue</mark> in both eyes, <mark class="h">three nights</mark> at a 5-star hotel and a driver waiting at <mark>Istanbul Airport</mark>.',
      shade: 'Glacier Blue', meta: 'IR-01, both eyes, about 20 minutes', c: '#9DBAD2', cool: true,
      nights: 3, from: 'LHR', langs: ['EN'], langNames: 'Speaks English with you',
      days: [['Day 1', 'Arrive, eye exam'], ['Day 2', 'Colour day'], ['Day 3', 'Check-up, free afternoon'], ['Day 4', 'Final check, fly home']],
    },
    {
      text: '<mark>Hazel</mark> for both eyes, <mark class="h">four nights</mark> near the Bosphorus and a coordinator who <mark>speaks Arabic</mark>.',
      shade: 'Hazel', meta: 'IR-07, both eyes, about 20 minutes', c: '#8C7E45', cool: false,
      nights: 4, from: 'DXB', langs: ['AR', 'EN'], langNames: 'Speaks Arabic and English',
      days: [['Day 1', 'Arrive, eye exam'], ['Day 2', 'Colour day'], ['Day 3–4', 'Rest, check-ups'], ['Day 5', 'Final check, fly home']],
    },
    {
      text: '<mark>Silver Grey</mark> in both eyes, <mark class="h">two nights</mark> and a <mark>90-minute</mark> flight home.',
      shade: 'Silver Grey', meta: 'IR-04, both eyes, about 20 minutes', c: '#A0A9B1', cool: true,
      nights: 2, from: 'OTP', langs: ['RO', 'EN'], langNames: 'Speaks Romanian and English',
      days: [['Day 1', 'Arrive, eye exam'], ['Day 2', 'Colour day'], ['Day 3', 'Final check, fly home']],
    },
  ];
  const tripCard = $('#tripCard');
  if (tripCard) {
    const tabs = $$('[data-trip]', tripCard);
    const askText = $('#askText');
    const pks = $$('.pk', tripCard);
    const days = $('#tripDays');
    const f = (k) => $(`[data-f="${k}"]`, tripCard);
    let cur = 0, picked = false, visible = false, hovering = false;

    const fill = (t) => {
      askText.innerHTML = t.text;
      f('shade').textContent = t.shade;
      f('shadeMeta').textContent = t.meta;
      const iris = f('iris');
      iris.style.setProperty('--c', t.c);
      iris.classList.toggle('cool', t.cool);
      f('nights').textContent = t.nights;
      f('from').textContent = t.from;
      f('langs').innerHTML = t.langs.map((l) => `<i>${l}</i>`).join('');
      f('langNames').textContent = t.langNames;
      // days in Istanbul = nights + 1; the plan list can fold two days into one row ("Day 3–4")
      f('days').textContent = t.nights + 1;
      f('plan').innerHTML = t.days.map(([d, what]) => `<li><span>${d}</span><b>${what}</b></li>`).join('');
    };
    const show = (i) => {
      if (i === cur) return;
      cur = i;
      tabs.forEach((b, k) => b.setAttribute('aria-pressed', String(k === i)));
      if (reduceMotion) { fill(TRIPS[i]); return; }
      askText.classList.add('fade');
      pks.forEach((p) => p.classList.add('swap'));
      days.classList.add('swap');
      setTimeout(() => {
        fill(TRIPS[i]);
        askText.classList.remove('fade');
        pks.forEach((p, k) => setTimeout(() => p.classList.remove('swap'), k * 70));
        days.classList.remove('swap');
      }, 300);
    };
    tabs.forEach((b, k) => b.addEventListener('click', () => { picked = true; show(k); }));
    // anyone reading or using the card stops the rotation
    tripCard.addEventListener('focusin', () => { picked = true; });
    inView(tripCard, (v) => { visible = v; }, 0.35);
    tripCard.addEventListener('mouseenter', () => { hovering = true; });
    tripCard.addEventListener('mouseleave', () => { hovering = false; });
    if (!reduceMotion) setInterval(() => { if (visible && !picked && !hovering && !document.hidden) show((cur + 1) % TRIPS.length); }, 7000);
  }

  /* ---------- Reveal on scroll ---------- */
  const revealEls = $$('[data-reveal]');
  const siblings = new Map();
  revealEls.forEach((el) => {
    const n = siblings.get(el.parentElement) || 0;
    siblings.set(el.parentElement, n + 1);
    if (n) el.style.transitionDelay = `${Math.min(n, 4) * 90}ms`;
  });
  const io = new IntersectionObserver((entries) => entries.forEach((en) => {
    if (!en.isIntersecting) return;
    en.target.classList.add('in');
    io.unobserve(en.target);
    setTimeout(() => { en.target.style.transitionDelay = ''; }, 1400);
  }), { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  revealEls.forEach((el) => io.observe(el));
  // bento cards also need .in for their diagrams
  $$('.b-card').forEach((el) => { if (!el.hasAttribute('data-reveal')) io.observe(el); });

  /* ---------- Why: the statement fills in word by word as you scroll ---------- */
  const why = $('#whyText');
  if (why) {
    [...why.childNodes].forEach((node) => {
      if (node.nodeType === Node.TEXT_NODE) {
        const frag = document.createDocumentFragment();
        node.textContent.split(/(\s+)/).forEach((part) => {
          if (!part) return;
          if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
          const w = document.createElement('span');
          w.className = 'w';
          w.textContent = part;
          frag.appendChild(w);
        });
        node.replaceWith(frag);
      } else if (node.nodeType === Node.ELEMENT_NODE) node.classList.add('w');
    });
    const words = $$('.w', why);
    const paint = () => {
      const r = why.getBoundingClientRect();
      const vh = window.innerHeight;
      const p = reduceMotion ? 1 : Math.min(1, Math.max(0, (vh * 0.85 - r.top) / (vh * 0.4 + r.height)));
      const n = Math.round(p * words.length);
      words.forEach((w, i) => w.classList.toggle('on', i < n));
    };
    paint();
    window.addEventListener('scroll', paint, { passive: true });
    window.addEventListener('resize', paint);
  }

  /* ---------- Count-up numbers ---------- */
  const fmt = new Intl.NumberFormat(document.documentElement.lang || 'en');
  $$('[data-count]').forEach((el) => {
    const target = +el.dataset.count;
    if (reduceMotion) return;
    el.textContent = '0';
    const ob = new IntersectionObserver((en) => {
      if (!en[0].isIntersecting) return;
      ob.disconnect();
      const t0 = performance.now();
      const step = (t) => {
        const k = Math.min(1, (t - t0) / 1400);
        el.textContent = fmt.format(Math.round(target * (1 - Math.pow(1 - k, 3))));
        if (k < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    }, { threshold: 0.6 });
    ob.observe(el);
  });

  /* ---------- How it works: card deck ---------- */
  const journey = $('#journey');
  if (journey) {
    const track = $('#journeyTrack');
    const cards = $$('.jcard', track);
    const dots = $$('#jDots button');
    const counter = $('#jCur');
    const bubble = $('#jDrag');
    let idx = 0, seen = false, hovering = false, dragging = false, timer = 0;
    const offset = (i) => cards[i].offsetLeft - cards[0].offsetLeft;
    const place = () => { track.style.transform = `translateX(${-offset(idx)}px)`; };
    const schedule = () => {
      clearTimeout(timer);
      if (reduceMotion) return;
      timer = setTimeout(() => {
        if (seen && !hovering && !dragging && !document.hidden) go(idx + 1);
        else schedule();
      }, 6000);
    };
    function go(i) {
      idx = (i + cards.length) % cards.length;
      place();
      cards.forEach((c, k) => {
        c.classList.toggle('active', k === idx);
        c.classList.toggle('before', k < idx);
        c.setAttribute('aria-hidden', String(k !== idx));
      });
      dots.forEach((d, k) => { d.classList.toggle('on', k === idx); d.setAttribute('aria-current', k === idx ? 'step' : 'false'); });
      counter.textContent = String(idx + 1).padStart(2, '0');
      schedule();
    }
    $('#jPrev').addEventListener('click', () => go(idx - 1));
    $('#jNext').addEventListener('click', () => go(idx + 1));
    dots.forEach((d, k) => d.addEventListener('click', () => go(k)));
    track.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') { e.preventDefault(); go(idx + 1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); go(idx - 1); }
    });
    inView(journey, (v) => { seen = v; }, 0.3);
    track.addEventListener('mouseenter', () => { hovering = true; });
    track.addEventListener('mouseleave', () => { hovering = false; });

    // drag or swipe
    let startX = 0, startY = 0, dx = 0, moved = false, axis = '';
    track.addEventListener('pointerdown', (e) => {
      if (e.button !== 0) return;
      dragging = true; moved = false; axis = ''; startX = e.clientX; startY = e.clientY; dx = 0;
      track.classList.add('dragging');
      journey.classList.add('is-dragging');
    });
    window.addEventListener('pointermove', (e) => {
      if (!dragging) return;
      dx = e.clientX - startX;
      if (!axis && (Math.abs(dx) > 6 || Math.abs(e.clientY - startY) > 6)) axis = Math.abs(dx) > Math.abs(e.clientY - startY) ? 'x' : 'y';
      if (axis !== 'x') return;
      moved = true;
      const edge = (idx === 0 && dx > 0) || (idx === cards.length - 1 && dx < 0);
      track.style.transform = `translateX(${-offset(idx) + (edge ? dx * 0.3 : dx)}px)`;
    });
    const endDrag = () => {
      if (!dragging) return;
      dragging = false;
      track.classList.remove('dragging');
      journey.classList.remove('is-dragging');
      if (moved && dx < -70 && idx < cards.length - 1) go(idx + 1);
      else if (moved && dx > 70 && idx > 0) go(idx - 1);
      else place();
    };
    window.addEventListener('pointerup', endDrag);
    window.addEventListener('pointercancel', endDrag);
    track.addEventListener('dragstart', (e) => e.preventDefault());
    cards.forEach((c, k) => c.addEventListener('click', () => { if (!moved && k !== idx) go(k); }));

    // a "Drag / Next / Back" bubble follows the mouse
    if (canHover && !reduceMotion) {
      journey.classList.add('has-cursor');
      track.addEventListener('pointermove', (e) => {
        const r = journey.getBoundingClientRect();
        bubble.style.transform = `translate(${e.clientX - r.left}px, ${e.clientY - r.top}px)`;
        const k = cards.indexOf(e.target.closest('.jcard'));
        bubble.textContent = dragging || k === idx || k < 0 ? 'Drag' : k > idx ? 'Next' : 'Back';
      });
      track.addEventListener('pointerenter', () => bubble.classList.add('show'));
      track.addEventListener('pointerleave', () => bubble.classList.remove('show'));
    }
    window.addEventListener('resize', place);
    go(0);
  }

  /* ---------- Patients worldwide: region list, lit frame and route card ----------
     The card cycles through the routes of the chosen region, then moves on to the next region.
     Once someone picks a region it stays on that region. Flight times are approximate direct flights. */
  const route = $('#routeCard');
  const regionList = $('#regions');
  if (route && regionList) {
    const ROUTES = {
      eu: [['LHR', 'London'], ['BER', 'Berlin'], ['CDG', 'Paris'], ['OTP', 'Bucharest']],
      me: [['DXB', 'Dubai'], ['DOH', 'Doha'], ['RUH', 'Riyadh'], ['KWI', 'Kuwait City']],
      us: [['JFK', 'New York'], ['ORD', 'Chicago'], ['MIA', 'Miami'], ['LAX', 'Los Angeles']],
    };
    const HOURS = { LHR: '4', BER: '3', CDG: '3.5', OTP: '1.5', DXB: '4.5', DOH: '4.5', RUH: '4', KWI: '3.5', JFK: '10', ORD: '10.5', MIA: '11', LAX: '13' };
    const order = Object.keys(ROUTES);
    const regionBtns = $$('.region', regionList);
    const frames = $$('.frame[data-region]', route.parentElement);
    let region = 'eu', r = 0, pinned = false, rVisible = false;

    const paint = (animate) => {
      const [code, city] = ROUTES[region][r];
      const apply = () => {
        $('[data-r="from"]', route).textContent = code;
        $('[data-r="city"]', route).textContent = `${city} to Istanbul`;
        $('[data-r="time"]', route).textContent = `Direct, about ${HOURS[code]} hours`;
        route.classList.remove('swap');
      };
      regionBtns.forEach((b) => { const on = b.dataset.region === region; b.classList.toggle('active', on); b.setAttribute('aria-pressed', String(on)); });
      frames.forEach((f) => f.classList.toggle('feat', f.dataset.region === region));
      if (!animate || reduceMotion) { apply(); return; }
      route.classList.add('swap');
      setTimeout(apply, 350);
    };

    regionBtns.forEach((b) => b.addEventListener('click', () => {
      pinned = true;
      if (b.dataset.region === region) return;
      region = b.dataset.region; r = 0;
      paint(true);
    }));

    if (!reduceMotion) {
      inView(route, (v) => { rVisible = v; }, 0.3);
      setInterval(() => {
        if (!rVisible || document.hidden) return;
        r += 1;
        if (r >= ROUTES[region].length) {
          r = 0;
          if (!pinned) region = order[(order.indexOf(region) + 1) % order.length];
        }
        paint(true);
      }, 3400);
    }
  }

  /* ---------- Patient stories: stage + picker with autoplay ---------- */
  const stage = $('#storyStage');
  if (stage) {
    const stories = $$('.story', stage);
    const pick = $('#storyPick');
    const tabs = $$('.spick-tab', pick);
    const sCur = $('#sCur');
    let s = 0, sVisible = false, sHover = false, sHold = false, started = false;
    const setPaused = () => pick.classList.toggle('paused', !sVisible || sHover || sHold);
    // before / after eye strips: the hidden range input moves the split; touching one pauses the autoplay
    const bas = $$('.ba', stage);
    const resetBa = (ba) => { ba.classList.remove('ba-touched'); ba.style.setProperty('--p', '50%'); $('.ba-range', ba).value = 50; };
    bas.forEach((ba) => {
      const r = $('.ba-range', ba);
      r.addEventListener('input', () => { ba.classList.add('ba-touched'); ba.style.setProperty('--p', r.value + '%'); });
      ba.addEventListener('pointerdown', () => { sHold = true; setPaused(); });
      ['pointerup', 'pointercancel'].forEach((ev) => ba.addEventListener(ev, () => { sHold = false; setPaused(); }));
    });
    const show = (i, focus) => {
      s = (i + stories.length) % stories.length;
      stories.forEach((st, k) => { st.classList.toggle('active', k === s); st.setAttribute('aria-hidden', String(k !== s)); });
      $$('.ba', stories[s]).forEach(resetBa);
      tabs.forEach((t, k) => {
        t.classList.toggle('active', k === s);
        t.classList.toggle('done', k < s);
        t.setAttribute('aria-selected', String(k === s));
        t.tabIndex = k === s ? 0 : -1;
      });
      sCur.textContent = String(s + 1).padStart(2, '0');
      const bar = $('.spick-bar i', tabs[s]);
      bar.style.animation = 'none'; void bar.offsetWidth; bar.style.animation = '';
      if (focus) tabs[s].focus({ preventScroll: true });
      if (pick.scrollWidth > pick.clientWidth) {
        const t = tabs[s];
        pick.scrollTo({ left: t.offsetLeft - (pick.clientWidth - t.offsetWidth) / 2, behavior: reduceMotion ? 'auto' : 'smooth' });
      }
    };
    if (!reduceMotion) {
      tabs.forEach((t, k) => $('.spick-bar i', t).addEventListener('animationend', () => { if (k === s) show(s + 1); }));
      stories[0].classList.remove('active'); // let the first portrait wipe in when the stage arrives
    }
    tabs.forEach((t, k) => t.addEventListener('click', () => show(k)));
    pick.addEventListener('keydown', (e) => {
      const d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
      if (d) { e.preventDefault(); show(s + d, true); }
    });
    $('#sPrev').addEventListener('click', () => show(s - 1));
    $('#sNext').addEventListener('click', () => show(s + 1));
    inView(stage, (v) => {
      sVisible = v;
      if (v && !started) { started = true; show(0); }
      setPaused();
    }, 0.35);
    [stage, pick].forEach((el) => {
      el.addEventListener('mouseenter', () => { sHover = true; setPaused(); });
      el.addEventListener('mouseleave', () => { sHover = false; setPaused(); });
    });
    let tx = null, ty = 0;
    stage.addEventListener('touchstart', (e) => {
      if (e.target.closest('.ba')) { tx = null; return; } // dragging the before / after split is not a swipe
      tx = e.touches[0].clientX; ty = e.touches[0].clientY;
    }, { passive: true });
    stage.addEventListener('touchend', (e) => {
      if (tx === null) return;
      const dx = e.changedTouches[0].clientX - tx, dy = e.changedTouches[0].clientY - ty;
      tx = null;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) show(s + (dx < 0 ? 1 : -1));
    });
    setPaused();
  }

  /* ---------- Review marquee: each row is copied once so the loop has no visible jump ---------- */
  $$('.marquee .track').forEach((track) => {
    [...track.children].forEach((card) => {
      const copy = card.cloneNode(true);
      copy.setAttribute('aria-hidden', 'true');
      track.appendChild(copy);
      watchPhotos(copy);
    });
  });

  /* ---------- Treatments: tabs ---------- */
  const tabBar = $('.tabs');
  if (tabBar) {
    const tabs = $$('.tab', tabBar);
    const panels = $$('.panel');
    const activate = (name, focus) => {
      tabs.forEach((t) => {
        const on = t.dataset.tab === name;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        if (!on) return;
        if (focus) t.focus({ preventScroll: true });
        if (tabBar.scrollWidth > tabBar.clientWidth) {
          tabBar.scrollTo({ left: t.offsetLeft - (tabBar.clientWidth - t.offsetWidth) / 2, behavior: reduceMotion ? 'auto' : 'smooth' });
        }
      });
      panels.forEach((p) => {
        const on = p.id === `panel-${name}`;
        if (on && p.hidden) { p.hidden = false; p.classList.remove('enter'); void p.offsetWidth; p.classList.add('enter'); }
        else if (!on) p.hidden = true;
      });
    };
    tabs.forEach((t) => t.addEventListener('click', () => activate(t.dataset.tab)));
    tabBar.addEventListener('keydown', (e) => {
      const i = tabs.findIndex((t) => t.getAttribute('aria-selected') === 'true');
      const k = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: tabs.length - 1 }[e.key];
      if (k === undefined) return;
      e.preventDefault();
      activate(tabs[(k + tabs.length) % tabs.length].dataset.tab, true);
    });
    $$('[data-tab-link]').forEach((a) => a.addEventListener('click', () => activate(a.dataset.tabLink)));

    // heterochromia: before / after
    const hx = $('#hxFrame');
    $$('[data-hx]').forEach((b, _, all) => b.addEventListener('click', () => {
      hx.classList.toggle('matched', b.dataset.hx === 'matched');
      all.forEach((o) => o.setAttribute('aria-pressed', String(o === b)));
    }));
  }

  // load the photos of hidden tabs and closed shade rows a little before they're needed
  $$('#treatments, #shades').forEach((sec) => {
    const ob = new IntersectionObserver((en) => {
      if (!en[0].isIntersecting) return;
      $$('img[loading="lazy"]', sec).forEach((img) => { img.loading = 'eager'; });
      ob.disconnect();
    }, { rootMargin: '800px 0px' });
    ob.observe(sec);
  });

  /* ---------- Shade library: hover or tap opens a row; it cycles until someone picks one ---------- */
  const cats = $('#cats');
  if (cats) {
    const rows = $$('.cat', cats);
    let open = 0, hold = false, picked = false, cVisible = false;
    const setRow = (i) => {
      open = i;
      rows.forEach((li, k) => {
        li.classList.toggle('open', k === i);
        $('.cat-btn', li).setAttribute('aria-expanded', String(k === i));
      });
    };
    rows.forEach((li, k) => {
      $('.cat-btn', li).addEventListener('click', () => { picked = true; setRow(k); });
      if (canHover) li.addEventListener('mouseenter', () => setRow(k));
    });
    cats.addEventListener('mouseenter', () => { hold = true; });
    cats.addEventListener('mouseleave', () => { hold = false; });
    cats.addEventListener('focusin', () => { hold = true; });
    cats.addEventListener('focusout', () => { hold = false; });
    inView(cats, (v) => { cVisible = v; }, 0.3);
    if (!reduceMotion) setInterval(() => { if (cVisible && !hold && !picked && !document.hidden) setRow((open + 1) % rows.length); }, 4200);
  }

  /* ---------- FAQ: topic filter, two balanced columns, one answer open at a time ---------- */
  const faqList = $('#faqList');
  if (faqList) {
    const items = $$('.faq-item', faqList);
    const filters = $$('.faq-filter');
    const cols = [0, 1].map(() => { const c = document.createElement('div'); c.className = 'faq-col'; faqList.appendChild(c); return c; });
    const setOpen = (item, open) => {
      item.classList.toggle('open', open);
      $('.faq-q', item).setAttribute('aria-expanded', String(open));
    };
    items.forEach((item, i) => {
      const q = $('.faq-q', item);
      const a = $('.faq-a', item);
      a.id = `faq-a-${i + 1}`;
      a.setAttribute('role', 'region');
      q.setAttribute('aria-controls', a.id);
      q.addEventListener('click', () => {
        const open = !item.classList.contains('open');
        items.forEach((o) => { if (o !== item) setOpen(o, false); });
        setOpen(item, open);
      });
    });
    filters.forEach((b) => {
      const cat = b.dataset.cat;
      $('small', b).textContent = cat === 'all' ? items.length : items.filter((it) => it.dataset.cat === cat).length;
    });
    const layout = (cat) => {
      const shown = items.filter((it) => cat === 'all' || it.dataset.cat === cat);
      items.forEach((it) => { it.hidden = !shown.includes(it); if (it.hidden) setOpen(it, false); });
      const half = Math.ceil(shown.length / 2);
      shown.forEach((it, i) => cols[i < half ? 0 : 1].appendChild(it));
    };
    filters.forEach((b) => b.addEventListener('click', () => {
      filters.forEach((o) => o.setAttribute('aria-pressed', String(o === b)));
      layout(b.dataset.cat);
    }));
    layout('all');
  }

  /* ---------- Footer form → WhatsApp: shade, region and note go into the message.
     Nothing chosen and no note still opens the chat with the default message. ---------- */
  const fForm = $('#footerForm');
  if (fForm) {
    const shadeName = $('#fShadeName');
    const picked = (name) => { const el = $(`input[name="${name}"]:checked`, fForm); return el ? el.value : ''; };
    fForm.addEventListener('change', (e) => {
      if (e.target.name === 'fShade') shadeName.textContent = e.target.value || 'Not sure yet';
    });
    fForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const shade = picked('fShade');
      const from = picked('fFrom');
      const note = $('#footerInput').value.trim();
      const details = [shade && `The shade I have in mind: ${shade}`, from && `I'd be flying in from ${from}.`].filter(Boolean);
      const blocks = [details.join('\n'), note].filter(Boolean);
      openWhatsApp(blocks.length ? `Hi İrisya Clinic, I'd like a free shade plan.\n\n${blocks.join('\n\n')}` : WHATSAPP_DEFAULT_MSG);
      toast('WhatsApp is opening with your message. Add your two photos in the chat.');
    });
  }

  const year = $('#year');
  if (year) year.textContent = new Date().getFullYear();
})();
