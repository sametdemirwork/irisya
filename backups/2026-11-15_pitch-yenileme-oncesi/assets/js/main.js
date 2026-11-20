/* ==========================================================================
   İrisya Clinic — interactions
   ========================================================================== */

/* ---- CONFIG: replace with the clinic's real WhatsApp number (country code, digits only) ---- */
const WHATSAPP_NUMBER = '905000000000';
const WHATSAPP_DEFAULT_MSG = "Hi İrisya Clinic, I'd like a free shade plan and a quote for eye colour change.";

(() => {
  'use strict';
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const waLink = (msg) => `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(msg)}`;

  /* ---------- Content placeholders ----------
     Every photo slot points at assets/img/content/<name>. Until that file exists,
     the slot shows a labelled frame with the expected file name and size. */
  const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  function placeholderSvg(label, file, size, w, h, yPos) {
    const text = w >= 220 && h >= 140;
    const fs = Math.round(Math.max(13, Math.min(w / 26, h / 10, 34)));
    const cy = h * (yPos || 0.5);
    const ico = Math.round(Math.min(w, h) * (text ? 0.12 : 0.34));
    const iy = text ? cy - fs * 1.9 - ico / 2 : cy - ico / 2;
    const inset = Math.max(6, Math.round(Math.min(w, h) * 0.04));
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" preserveAspectRatio="xMidYMid slice">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0E2D57"/><stop offset="1" stop-color="#04132B"/></linearGradient>
<pattern id="p" width="26" height="26" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="9" height="26" fill="#fff" fill-opacity=".035"/></pattern></defs>
<rect width="${w}" height="${h}" fill="url(#g)"/><rect width="${w}" height="${h}" fill="url(#p)"/>
<rect x="${inset}" y="${inset}" width="${w - inset * 2}" height="${h - inset * 2}" rx="${inset}" fill="none" stroke="#A8C7E3" stroke-opacity=".45" stroke-width="1.5" stroke-dasharray="7 6"/>
<g transform="translate(${w / 2 - ico / 2} ${iy}) scale(${ico / 24})" fill="none" stroke="#CFE7F8" stroke-width="1.6" stroke-linejoin="round" opacity=".85"><path d="M4 8h3l1.6-2.4h6.8L17 8h3v11H4z"/><circle cx="12" cy="13.2" r="3.4"/></g>
${text ? `<g font-family="Jost, Helvetica, Arial, sans-serif" text-anchor="middle">
<text x="${w / 2}" y="${cy + fs * 0.35}" font-size="${fs}" font-weight="600" fill="#fff">${esc(label)}</text>
<text x="${w / 2}" y="${cy + fs * 1.75}" font-size="${Math.round(fs * 0.72)}" fill="#A8C7E3">content/${esc(file)} · ${size}</text></g>` : ''}</svg>`;
  }
  const watched = new WeakSet();
  const watchPh = (img) => {
    const file = img.getAttribute('src').split('/').pop();
    const fail = () => {
      if (img.classList.contains('is-ph')) return;
      const aw = +img.getAttribute('width') || 1200;
      const ah = +img.getAttribute('height') || 800;
      // draw at the box's own proportions so the label is never cropped; the label keeps the recommended size
      const bw = img.clientWidth, bh = img.clientHeight;
      const k = bw && bh ? Math.max(aw / bw, ah / bh) : 1;
      const w = bw && bh ? Math.round(bw * k) : aw;
      const h = bw && bh ? Math.round(bh * k) : ah;
      const pic = img.parentElement && img.parentElement.tagName === 'PICTURE' ? img.parentElement : null;
      if (pic) $$('source', pic).forEach((s) => s.remove());
      img.removeAttribute('srcset');
      img.classList.add('is-ph');
      img.title = `${img.dataset.ph} — assets/img/content/${file}`;
      img.src = `data:image/svg+xml,${encodeURIComponent(placeholderSvg(img.dataset.ph, file, `${aw}×${ah}`, w, h, parseFloat(img.dataset.phY)))}`;
    };
    if (img.complete) { if (!img.naturalWidth) fail(); } else img.addEventListener('error', fail, { once: true });
  };
  const watchPlaceholders = (root = document) => $$('img[data-ph]:not(.is-ph)', root).forEach((img) => {
    if (watched.has(img)) return;
    watched.add(img);
    watchPh(img);
  });
  watchPlaceholders();

  /* ---------- Toast ---------- */
  const toastEl = $('#toast');
  let toastTimer;
  function toast(msg, ms = 3800) {
    toastEl.textContent = msg;
    toastEl.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove('show'), ms);
  }

  /* ---------- WhatsApp links ---------- */
  // a non-empty data-whatsapp value replaces the default message
  $$('[data-whatsapp]').forEach((a) => {
    a.href = waLink(a.dataset.whatsapp || WHATSAPP_DEFAULT_MSG);
    a.target = '_blank';
    a.rel = 'noopener';
  });

  /* ---------- Header: scroll state, banner, mobile menu ---------- */
  const header = $('#header');
  const waFloat = $('.wa-float');
  const onScrollHeader = () => {
    const y = window.scrollY;
    header.classList.toggle('scrolled', y > 40);
    waFloat.classList.toggle('show', y > 700);
  };
  onScrollHeader();
  window.addEventListener('scroll', onScrollHeader, { passive: true });

  // storage can throw (private mode, blocked site data, sandboxed frames)
  let bannerClosed = false;
  try { bannerClosed = !!sessionStorage.getItem('irisya-banner-closed'); } catch (e) { /* ignore */ }
  if (bannerClosed) header.classList.add('no-banner');
  $('#bannerClose').addEventListener('click', () => {
    header.classList.add('no-banner');
    try { sessionStorage.setItem('irisya-banner-closed', '1'); } catch (e) { /* ignore */ }
  });

  const burger = $('#burger');
  burger.addEventListener('click', () => {
    const open = header.classList.toggle('menu-open');
    burger.setAttribute('aria-expanded', String(open));
  });
  $$('#mobileMenu a').forEach((a) => a.addEventListener('click', () => {
    header.classList.remove('menu-open');
    burger.setAttribute('aria-expanded', 'false');
  }));

  /* ---------- Hero headline: split into letters (inline <em> keeps its style) ---------- */
  const h1 = $('[data-split]');
  if (h1 && !reduceMotion) {
    let i = 0;
    const splitInto = (target, text) => {
      text.split(/(\s+)/).forEach((part) => {
        if (!part) return;
        if (/^\s+$/.test(part)) { target.appendChild(document.createTextNode(' ')); return; }
        const w = document.createElement('span');
        w.className = 'word';
        [...part].forEach((ch) => {
          const c = document.createElement('span');
          c.className = 'char';
          c.style.setProperty('--i', i++);
          c.textContent = ch;
          w.appendChild(c);
        });
        target.appendChild(w);
      });
    };
    const frag = document.createDocumentFragment();
    Array.from(h1.childNodes).forEach((node) => {
      if (node.nodeType === Node.TEXT_NODE) splitInto(frag, node.textContent);
      else if (node.nodeType === Node.ELEMENT_NODE && node.tagName !== 'BR') {
        const el = node.cloneNode(false);
        splitInto(el, node.textContent);
        frag.appendChild(el);
      } else frag.appendChild(node.cloneNode(true));
    });
    h1.setAttribute('aria-label', h1.textContent.replace(/\s+/g, ' ').trim());
    h1.innerHTML = '';
    h1.appendChild(frag);
  }

  /* ---------- Hero film: cinematic background video (assets/img/content/hero*.mp4|webm) ---------- */
  const hero = $('.hero');
  const film = $('#heroVideo');
  const media = $('#heroMedia');
  if (hero && film) {
    // Chapter cuts of the edit (seconds) — keep in sync with CUES in /hero-film/irisya/build.py
    const CUES = [
      { t: 0, label: 'Laser eye colour change' },
      { t: 2.4, label: 'Istanbul', fx: 'flash' },
      { t: 3.85, fx: 'whip' },
      { t: 5.2, label: 'VIP transfer', fx: 'whip' },
      { t: 6.15, fx: 'whip' },
      { t: 7, label: 'Five-star stay', fx: 'flash' },
      { t: 8.7, label: 'Your shade, planned', fx: 'flash' },
      { t: 10.5, label: 'Ophthalmologist-led', fx: 'flash' },
      { t: 12.4, label: 'Your eyes, reimagined', fx: 'flash' },
    ];
    const START_AT = 1; // the frame hero.webp was taken from, so poster → film is seamless
    const toggle = $('#heroToggle');
    const sheen = $('#heroSheen');
    const pulseEl = $('#heroPulse');
    const reelN = $('#reelN');
    const reelLabel = $('#reelLabel');
    const reelBar = $('#reelBar');
    const saveData = !!(navigator.connection && navigator.connection.saveData);
    let wanted = !reduceMotion && !saveData;
    let inView = true;
    let available = true;
    let started = false;

    const loadFilm = () => {
      if (film.querySelector('source')) return;
      const portrait = window.matchMedia('(max-aspect-ratio: 4/5) and (max-width: 700px)').matches;
      const need = Math.max(window.innerWidth, window.innerHeight * 16 / 9) * Math.min(window.devicePixelRatio || 1, 2);
      const base = portrait ? film.dataset.portrait : need > 1500 ? film.dataset.hd : film.dataset.sd;
      // Safari decodes VP9 in software on many devices; give it H.264 straight away
      const safari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
      const exts = safari ? ['mp4'] : ['webm', 'mp4'];
      exts.forEach((ext, i) => {
        const s = document.createElement('source');
        s.src = `${base}.${ext}`;
        s.type = ext === 'webm' ? 'video/webm; codecs="vp9"' : 'video/mp4';
        // no file at all: keep the still image / placeholder and hide the control
        if (i === exts.length - 1) s.addEventListener('error', () => { available = false; toggle.hidden = true; });
        film.appendChild(s);
      });
      film.addEventListener('loadedmetadata', () => { if (!started) film.currentTime = START_AT; }, { once: true });
      film.load();
    };

    const sync = () => {
      if (!available) return;
      if (wanted && inView && !document.hidden) {
        loadFilm();
        const p = film.play();
        // autoplay refused (e.g. iOS low-power mode): stay on the poster and offer the play button
        if (p && p.catch) p.catch((e) => { if (e && e.name === 'NotAllowedError') setWanted(false); });
      } else if (!film.paused) film.pause();
    };

    function setWanted(v) {
      wanted = v;
      hero.classList.toggle('film-paused', !v);
      toggle.setAttribute('aria-label', v ? 'Pause background video' : 'Play background video');
      sync();
    }

    film.addEventListener('playing', () => {
      toggle.hidden = false;
      if (started) return;
      started = true;
      hero.classList.add('film-on');
    });
    toggle.addEventListener('click', () => setWanted(!wanted));
    if (!wanted) hero.classList.add('film-paused');

    new IntersectionObserver((en) => {
      inView = en[0].isIntersecting;
      hero.classList.toggle('in-view', inView);
      sync();
    }, { threshold: 0.02 }).observe(hero);
    document.addEventListener('visibilitychange', sync);

    // Caption + light pulses follow the cuts of the film
    if (reelLabel) {
      const chapterNo = {};
      CUES.forEach((c) => { if (c.label && !(c.label in chapterNo)) chapterNo[c.label] = Object.keys(chapterNo).length + 1; });
      const fxFrames = {
        flash: { el: pulseEl, k: [{ opacity: 0 }, { opacity: 1, offset: 0.18 }, { opacity: 0 }], d: 1100 },
        whip: { el: sheen, k: [{ opacity: 0.8, transform: 'translateX(60%)' }, { opacity: 0, transform: 'translateX(-60%)' }], d: 700 },
      };
      const kick = {
        flash: [{ transform: 'scale(1)' }, { transform: 'scale(1.018)', offset: 0.2 }, { transform: 'scale(1)' }],
        whip: [{ transform: 'translateX(18px)' }, { transform: 'none' }],
      };
      let cueIdx = -1;
      const onFrame = (t) => {
        let i = CUES.length - 1;
        while (i > 0 && CUES[i].t > t) i--;
        if (i !== cueIdx) {
          const first = cueIdx === -1;
          cueIdx = i;
          let j = i;
          while (!CUES[j].label) j--;
          const label = CUES[j].label;
          if (reelLabel.textContent !== label) {
            reelLabel.textContent = label;
            reelN.textContent = String(chapterNo[label]).padStart(2, '0');
            reelLabel.classList.remove('swap');
            void reelLabel.offsetWidth; // restart the swap animation
            reelLabel.classList.add('swap');
          }
          const fx = CUES[i].fx;
          if (!first && fx && !reduceMotion && media.animate) {
            const f = fxFrames[fx];
            f.el.animate(f.k, { duration: f.d, easing: 'cubic-bezier(.22,.8,.24,1)' });
            media.animate(kick[fx], { duration: 900, easing: 'cubic-bezier(.22,.8,.24,1)' });
          }
        }
        if (film.duration) reelBar.style.transform = `scaleX(${t / film.duration})`;
      };
      let ticking = false;
      const tick = () => {
        ticking = false;
        onFrame(film.currentTime);
        schedule();
      };
      function schedule() {
        if (ticking || film.paused) return;
        ticking = true;
        if (film.requestVideoFrameCallback) film.requestVideoFrameCallback(tick);
        else requestAnimationFrame(tick);
      }
      film.addEventListener('play', schedule);
    }

    sync();

    // Depth: the media drifts slower than the page and leans gently away from the pointer
    if (!reduceMotion) {
      const glow = $('#heroGlow');
      let tx = 0, ty = 0, cx = 0, cy = 0, sy = 0, raf = 0;
      let heroH = hero.offsetHeight;
      const draw = () => {
        cx += (tx - cx) * 0.06;
        cy += (ty - cy) * 0.06;
        media.style.translate = `${cx * -16}px ${cy * -12 + sy * 0.22}px`;
        glow.style.translate = `${cx * 26}px ${cy * 18}px`;
        raf = Math.abs(tx - cx) + Math.abs(ty - cy) > 0.002 ? requestAnimationFrame(draw) : 0;
      };
      const req = () => { if (!raf) raf = requestAnimationFrame(draw); };
      if (window.matchMedia('(pointer: fine)').matches) {
        window.addEventListener('pointermove', (e) => {
          if (!inView) return;
          tx = e.clientX / window.innerWidth - 0.5;
          ty = e.clientY / window.innerHeight - 0.5;
          req();
        }, { passive: true });
      }
      window.addEventListener('scroll', () => {
        if (window.scrollY > heroH) return;
        sy = window.scrollY;
        req();
      }, { passive: true });
      window.addEventListener('resize', () => { heroH = hero.offsetHeight; }, { passive: true });
    }
  }

  /* ---------- Hero prompt (free shade plan → WhatsApp) ---------- */
  const form = $('#promptForm');
  const input = $('#promptInput');
  const go = $('#promptGo');
  const fileInput = $('#fileInput');
  const fileChip = $('#promptFile');
  const examples = [
    'My eyes are dark brown. Could I go to a soft hazel or green?',
    "I'd love ice-blue eyes. Am I a good candidate?",
    "What's the difference between keratopigmentation and laser lightening?",
    'I have one brown and one blue eye. Can you match them?',
    'How many days do I need in Istanbul, including the hotel?',
  ];
  let exIdx = 0;
  const updateReady = () => go.classList.toggle('ready', input.value.trim().length > 0);
  input.addEventListener('input', updateReady);

  // Typewriter placeholder
  if (!reduceMotion) {
    let p = 0, ch = examples[0].length, deleting = true, hold = 0;
    setInterval(() => {
      if (document.activeElement === input || input.value) return;
      const full = examples[p];
      if (hold > 0) { hold--; return; }
      if (deleting) {
        ch = Math.max(0, ch - 2);
        if (ch === 0) { deleting = false; p = (p + 1) % examples.length; }
      } else {
        ch = Math.min(examples[p].length, ch + 1);
        if (ch === examples[p].length) { deleting = true; hold = 60; }
      }
      input.placeholder = (deleting ? full : examples[p]).slice(0, ch);
    }, 40);
  }

  $('#promptShuffle').addEventListener('click', () => {
    input.value = examples[exIdx % examples.length];
    exIdx++;
    updateReady();
    input.focus();
  });

  fileInput.addEventListener('change', () => {
    const files = Array.from(fileInput.files || []);
    if (!files.length) { fileChip.hidden = true; return; }
    $('span', fileChip).textContent = files.length === 1 ? files[0].name : `${files.length} photos selected`;
    fileChip.hidden = false;
  });
  $('button', fileChip).addEventListener('click', () => { fileInput.value = ''; fileChip.hidden = true; });

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) {
      input.focus();
      toast('Tell us a little about your eyes, or tap "Examples" to get started.');
      return;
    }
    const hasFiles = fileInput.files && fileInput.files.length > 0;
    let msg = `Hi İrisya Clinic, I'd like a free shade plan.\n\n${text}`;
    if (hasFiles) msg += '\n\n(I have daylight photos of my eyes ready to share.)';
    window.open(waLink(msg), '_blank', 'noopener');
    toast(hasFiles ? 'Opening WhatsApp — please attach your eye photos in the chat.' : 'Opening WhatsApp — our coordinators usually reply within minutes.');
  });

  /* ---------- Vision card: prompt builds a package ---------- */
  const visionCard = $('.vision-card');
  const agentText = $('#agentText');
  const agentGo = $('.agent-go');
  const agentStatus = $('#agentStatus');
  const pkCards = $$('.pk', visionCard);
  const trip = $('#trip');
  const tripSteps = $$('.trip-steps li', trip);
  const priceCard = $('#priceCard');
  // chip.k = which card that chip "creates"; cards without a chip appear after send
  const scenarios = [
    {
      segments: [
        { t: 'Book my ' }, { c: 'Glacier Blue', k: 'treatment' }, { t: ' eye colour change in ' }, { c: 'Istanbul', k: 'coord' },
        { t: ' with a ' }, { c: '5-star hotel', k: 'hotel' }, { t: ' and ' }, { c: 'VIP transfer', k: 'transfer' }, { t: '.' },
      ],
      cards: {
        treatment: ['Laser keratopigmentation', 'Both eyes · about 20 minutes'],
        hotel: ['5-star hotel', '4 nights · breakfast included'],
        transfer: ['VIP transfer', 'Airport → hotel → clinic'],
        coord: ['Your personal coordinator', 'English · Arabic', ['EN', 'AR']],
      },
      trip: ['Your 4-day trip', [['Day 1', 'Arrival & eye exam'], ['Day 2', 'Your colour day'], ['Day 3', 'Check-up & rest'], ['Day 4', 'Final check, fly home']]],
    },
    {
      segments: [
        { t: 'A ' }, { c: 'hazel', k: 'treatment' }, { t: ' shade for both eyes, flying from ' }, { c: 'Dubai', k: 'transfer' },
        { t: ' and staying ' }, { c: '5 nights', k: 'hotel' }, { t: '.' },
      ],
      cards: {
        treatment: ['Keratopigmentation · Hazel', 'Shade IR-07 · designed with you'],
        hotel: ['5-star hotel', '5 nights · minutes from the clinic'],
        transfer: ['DXB → IST, VIP pickup', 'Private driver, door to door'],
        coord: ['Your personal coordinator', 'Arabic · English', ['AR', 'EN']],
      },
      trip: ['Your 5-day trip', [['Day 1', 'Arrival & eye exam'], ['Day 2', 'Your colour day'], ['Day 3–4', 'Rest & check-ups'], ['Day 5', 'Final check, fly home']]],
    },
    {
      segments: [
        { t: "I'd like " }, { c: 'laser iris lightening', k: 'treatment' }, { t: ' with ' }, { c: 'hotel', k: 'hotel' },
        { t: ' and ' }, { c: 'transfers', k: 'transfer' }, { t: ' included.' },
      ],
      cards: {
        treatment: ['Laser iris lightening', 'Gradual change over weeks'],
        hotel: ['5-star hotel', 'Breakfast included'],
        transfer: ['VIP transfer', 'Airport → hotel → clinic'],
        coord: ['Your personal coordinator', 'English · German · Romanian', ['EN', 'DE', 'RO']],
      },
      trip: ['Your lightening plan', [['Step 1', 'Eye exam & pressure check'], ['Step 2', 'Laser session'], ['Step 3', 'Pressure check'], ['Step 4', 'Follow-ups from home']]],
    },
  ];
  const caret = document.createElement('span');
  caret.className = 'caret';
  const chipEl = (s) => { const c = document.createElement('span'); c.className = 'chip'; c.textContent = s.c; return c; };

  function fillScenario(sc) {
    pkCards.forEach((card) => {
      const [title, meta, langs] = sc.cards[card.dataset.k];
      $('[data-f="title"]', card).textContent = title;
      $('[data-f="meta"]', card).textContent = meta;
      const l = $('[data-f="langs"]', card);
      if (l) l.innerHTML = langs.map((x) => `<i>${x}</i>`).join('');
    });
    $('[data-f="trip"]', trip).textContent = sc.trip[0];
    tripSteps.forEach((li, i) => {
      $('.trip-day', li).textContent = sc.trip[1][i][0];
      $('b', li).textContent = sc.trip[1][i][1];
    });
    agentText.setAttribute('aria-label', sc.segments.map((s) => s.t || s.c).join(''));
  }

  function renderAgentFull() {
    fillScenario(scenarios[0]);
    agentText.innerHTML = '';
    scenarios[0].segments.forEach((s) => agentText.appendChild(s.t ? document.createTextNode(s.t) : chipEl(s)));
  }

  const cardFor = (k) => pkCards.find((c) => c.dataset.k === k);
  const flash = (card) => { card.classList.add('hl'); setTimeout(() => card.classList.remove('hl'), 900); };

  let agentRunning = false;
  async function runAgent() {
    if (agentRunning) return;
    agentRunning = true;
    visionCard.classList.add('anim');
    const wait = (ms) => new Promise((r) => setTimeout(r, ms));
    for (let n = 0; ; n = (n + 1) % scenarios.length) {
      const sc = scenarios[n];
      fillScenario(sc);
      agentText.innerHTML = '';
      agentText.style.opacity = 1;
      agentText.appendChild(caret);
      await wait(500);
      for (const s of sc.segments) {
        if (s.t) {
          const node = document.createTextNode('');
          agentText.insertBefore(node, caret);
          for (const ch of s.t) { node.textContent += ch; await wait(38 + Math.random() * 36); }
        } else {
          await wait(160);
          agentText.insertBefore(chipEl(s), caret);
          const card = cardFor(s.k);
          if (card) { card.classList.add('on'); flash(card); }
          await wait(320);
        }
      }
      await wait(500);
      caret.remove();
      agentGo.classList.remove('pulse'); void agentGo.offsetWidth; agentGo.classList.add('pulse');
      agentStatus.classList.add('on');
      for (const card of pkCards) {
        if (!card.classList.contains('on')) { await wait(260); card.classList.add('on'); flash(card); }
      }
      await wait(400);
      trip.classList.add('on');
      for (const li of tripSteps) { await wait(520); li.classList.add('on'); }
      await wait(300);
      priceCard.classList.add('on');
      agentStatus.classList.remove('on');
      await wait(4200);
      agentText.style.opacity = 0;
      [...pkCards, trip, priceCard, ...tripSteps].forEach((el) => el.classList.remove('on'));
      await wait(800);
    }
  }
  if (reduceMotion) renderAgentFull();
  else {
    new IntersectionObserver((entries, obs) => {
      if (entries[0].isIntersecting) { runAgent(); obs.disconnect(); }
    }, { threshold: 0.35 }).observe(visionCard);
  }

  /* ---------- Reveal on scroll ---------- */
  const revealEls = $$('[data-reveal], .bcard');
  const parents = new Map();
  revealEls.forEach((el) => {
    const p = el.parentElement;
    const idx = parents.get(p) || 0;
    parents.set(p, idx + 1);
    if (el.hasAttribute('data-reveal')) el.style.transitionDelay = `${Math.min(idx, 5) * 90}ms`;
  });
  const io = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (en.isIntersecting) {
        en.target.classList.add('in');
        io.unobserve(en.target);
        // clear stagger delay after reveal so hover transitions stay snappy
        setTimeout(() => { en.target.style.transitionDelay = ''; }, 1400);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  revealEls.forEach((el) => io.observe(el));

  /* ---------- Why: word-by-word highlight on scroll ---------- */
  const why = $('#whyText');
  if (why) {
    // split text nodes into word spans; inline <mark> chips stay whole and fill as one "word"
    [...why.childNodes].forEach((node) => {
      if (node.nodeType === Node.TEXT_NODE) {
        const frag = document.createDocumentFragment();
        node.textContent.split(/(\s+)/).forEach((part) => {
          if (!part) return;
          if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
          const sp = document.createElement('span');
          sp.className = 'w';
          sp.textContent = part;
          frag.appendChild(sp);
        });
        node.replaceWith(frag);
      } else if (node.nodeType === Node.ELEMENT_NODE) {
        node.classList.add('w');
      }
    });
    const ws = $$('.w', why);
    // progress follows the whole grid, because the text column is sticky and barely moves
    const grid = why.closest('.why-grid') || why;
    const update = () => {
      const r = grid.getBoundingClientRect();
      const vh = window.innerHeight;
      const prog = Math.min(1, Math.max(0, (vh * 0.8 - r.top) / (r.height * 0.7)));
      const n = reduceMotion ? ws.length : Math.round(prog * ws.length);
      ws.forEach((w, i) => w.classList.toggle('on', i < n));
    };
    update();
    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
  }

  /* ---------- Stats: rolling digits ---------- */
  $$('.stat-num').forEach((el) => {
    const val = el.dataset.count;
    el.setAttribute('aria-label', val);
    el.innerHTML = '';
    const cols = [];
    [...val].forEach((ch) => {
      if (/\d/.test(ch)) {
        const d = +ch;
        const col = document.createElement('span');
        col.className = 'col';
        col.setAttribute('aria-hidden', 'true');
        for (let k = 0; k <= d + 10; k++) {
          const s = document.createElement('span');
          s.textContent = k % 10;
          col.appendChild(s);
        }
        col.dataset.target = d + 10;
        cols.push(col);
        el.appendChild(col);
      } else {
        const s = document.createElement('span');
        s.className = 'static';
        s.setAttribute('aria-hidden', 'true');
        s.textContent = ch;
        el.appendChild(s);
      }
    });
    const ob = new IntersectionObserver((en, o) => {
      if (!en[0].isIntersecting) return;
      cols.forEach((col, idx) => {
        const steps = +col.dataset.target;
        const total = col.children.length;
        col.style.transitionDelay = `${idx * 120}ms`;
        col.style.transform = `translateY(-${(steps / total) * 100}%)`;
      });
      o.disconnect();
    }, { threshold: 0.6 });
    ob.observe(el);
  });

  /* ---------- Scale boxes (fixed-size mockups that scale to their container) ---------- */
  const fitBoxes = [
    { sel: '.bv-b', w: 432, h: 190 },
    { sel: '.bv-c', w: 432, h: 170 },
    { sel: '.bv-d', w: 640, h: 220 },
    { sel: '.bv-e', w: 328, h: 190 },
    { sel: '.bv-f', w: 328, h: 184 },
  ];
  function rescale() {
    fitBoxes.forEach(({ sel, w, h }) => {
      $$(sel).forEach((el) => {
        const avail = el.parentElement.clientWidth - parseFloat(getComputedStyle(el.parentElement).paddingLeft) * 2;
        if (avail < w) {
          const s = avail / w;
          el.style.width = `${w}px`;
          el.style.transform = `scale(${s})`;
          el.style.transformOrigin = '0 0';
          el.style.marginBottom = `${-(1 - s) * h}px`;
        } else {
          el.style.width = el.style.transform = el.style.marginBottom = '';
        }
      });
    });
  }
  rescale();
  window.addEventListener('resize', rescale);

  /* ---------- Journey carousel (steps + progress autoplay, arrows, drag) ---------- */
  const journey = $('#journey-carousel');
  const track = $('#journeyTrack');
  const cards = $$('.jcard', track);
  const jNav = $('#journeyNav');
  const jSteps = $$('.jstep', jNav);
  const jCur = $('#jCur');
  const jDrag = $('#jDrag');
  let jIdx = 0, inView = false, hovering = false, dragging = false;
  const offsetFor = (i) => cards[i].offsetLeft - cards[0].offsetLeft;
  const place = () => { track.style.transform = `translateX(${-offsetFor(jIdx)}px)`; };
  const setPaused = () => jNav.classList.toggle('paused', !inView || hovering || dragging);
  function goTo(i) {
    jIdx = (i + cards.length) % cards.length;
    place();
    cards.forEach((c, k) => {
      c.classList.toggle('active', k === jIdx);
      c.classList.toggle('before', k < jIdx);
      c.setAttribute('aria-hidden', String(k !== jIdx));
    });
    jSteps.forEach((s, k) => {
      s.classList.toggle('active', k === jIdx);
      s.classList.toggle('done', k < jIdx);
      s.setAttribute('aria-selected', String(k === jIdx));
    });
    jCur.textContent = String(jIdx + 1).padStart(2, '0');
    // restart the active step's progress bar
    const bar = $('.jstep-bar i', jSteps[jIdx]);
    bar.style.animation = 'none'; void bar.offsetWidth; bar.style.animation = '';
  }
  // autoplay: when the active step's progress bar fills, move on
  if (!reduceMotion) {
    jSteps.forEach((s, k) => $('.jstep-bar i', s).addEventListener('animationend', () => { if (k === jIdx) goTo(jIdx + 1); }));
  }
  jSteps.forEach((s, k) => s.addEventListener('click', () => goTo(k)));
  $('#jPrev').addEventListener('click', () => goTo(jIdx - 1));
  $('#jNext').addEventListener('click', () => goTo(jIdx + 1));

  let nudged = false;
  new IntersectionObserver((en) => {
    inView = en[0].isIntersecting;
    setPaused();
    // first time in view: nudge the cards sideways to show they can be dragged
    if (inView && !nudged && !reduceMotion) { nudged = true; setTimeout(() => journey.classList.add('nudge'), 600); }
  }, { threshold: 0.4 }).observe(track);
  journey.addEventListener('animationend', (e) => { if (e.target === journey) journey.classList.remove('nudge'); });
  track.addEventListener('mouseenter', () => { hovering = true; setPaused(); });
  track.addEventListener('mouseleave', () => { hovering = false; setPaused(); });

  // drag / swipe
  let startX = 0, dx = 0, moved = false;
  track.addEventListener('pointerdown', (e) => {
    if (e.button !== 0) return;
    dragging = true; moved = false; startX = e.clientX; dx = 0;
    track.classList.add('dragging');
    journey.classList.add('is-dragging');
    setPaused();
  });
  window.addEventListener('pointermove', (e) => {
    if (!dragging) return;
    dx = e.clientX - startX;
    if (Math.abs(dx) > 6) moved = true;
    const atEdge = (jIdx === 0 && dx > 0) || (jIdx === cards.length - 1 && dx < 0);
    track.style.transform = `translateX(${-offsetFor(jIdx) + (atEdge ? dx * 0.3 : dx)}px)`;
  });
  const endDrag = () => {
    if (!dragging) return;
    dragging = false;
    track.classList.remove('dragging');
    journey.classList.remove('is-dragging');
    setPaused();
    if (dx < -70 && jIdx < cards.length - 1) goTo(jIdx + 1);
    else if (dx > 70 && jIdx > 0) goTo(jIdx - 1);
    else place();
  };
  window.addEventListener('pointerup', endDrag);
  window.addEventListener('pointercancel', endDrag);
  track.addEventListener('dragstart', (e) => e.preventDefault());
  cards.forEach((c, k) => c.addEventListener('click', () => { if (!moved && k !== jIdx) goTo(k); }));
  track.setAttribute('tabindex', '0');
  track.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') goTo(jIdx + 1);
    if (e.key === 'ArrowLeft') goTo(jIdx - 1);
  });

  // "Drag" cursor bubble on devices with a mouse
  if (jDrag && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    const label = $('span', jDrag);
    journey.classList.add('has-cursor');
    track.addEventListener('pointermove', (e) => {
      const r = journey.getBoundingClientRect();
      jDrag.style.transform = `translate(${e.clientX - r.left}px, ${e.clientY - r.top}px)`;
      const k = cards.indexOf(e.target.closest('.jcard'));
      label.textContent = dragging || k === jIdx || k < 0 ? 'Drag' : k > jIdx ? 'Next' : 'Back';
    });
    track.addEventListener('pointerenter', () => jDrag.classList.add('show'));
    track.addEventListener('pointerleave', () => jDrag.classList.remove('show'));
  }

  window.addEventListener('resize', place);
  goTo(0);

  /* ---------- Patients worldwide: the route card cycles through the main markets ---------- */
  const route = $('#routeCard');
  if (route && !reduceMotion) {
    const routes = [
      ['LHR', 'London → Istanbul', 'Daily direct flights · approx. 4 h'],
      ['DXB', 'Dubai → Istanbul', 'Daily direct flights · approx. 4 h 30 min'],
      ['OTP', 'Bucharest → Istanbul', 'Daily direct flights · approx. 1 h 30 min'],
      ['JFK', 'New York → Istanbul', 'Direct flights · approx. 10 h'],
      ['FRA', 'Frankfurt → Istanbul', 'Daily direct flights · approx. 3 h'],
      ['YYZ', 'Toronto → Istanbul', 'Direct flights · approx. 10 h'],
    ];
    let rIdx = 0, rInView = false;
    new IntersectionObserver((en) => { rInView = en[0].isIntersecting; }, { threshold: 0.3 }).observe(route);
    setInterval(() => {
      if (!rInView || document.hidden) return;
      rIdx = (rIdx + 1) % routes.length;
      const [code, city, time] = routes[rIdx];
      route.classList.add('swap');
      setTimeout(() => {
        $('[data-r="from"]', route).textContent = code;
        $('[data-r="city"]', route).textContent = city;
        $('[data-r="time"]', route).textContent = time;
        route.classList.remove('swap');
      }, 350);
    }, 3200);
  }

  /* ---------- Testimonials marquee: duplicate tracks for a seamless loop ---------- */
  $$('.t-row').forEach((row) => {
    const t = $('.t-track', row);
    const clone = t.cloneNode(true);
    clone.setAttribute('aria-hidden', 'true');
    row.appendChild(clone);
    watchPlaceholders(clone);
  });

  /* ---------- Patient stories: story stage + picker with progress autoplay ---------- */
  const stage = $('#storyStage');
  if (stage) {
    const stories = $$('.story', stage);
    const pick = $('#storyPick');
    const sTabs = $$('.spick-tab', pick);
    const sCur = $('#sCur');
    let sIdx = 0, sInView = false, sHover = false, sStarted = false;
    const setSPaused = () => pick.classList.toggle('paused', !sInView || sHover);
    function showStory(i, focus) {
      sIdx = (i + stories.length) % stories.length;
      stories.forEach((s, k) => {
        s.classList.toggle('active', k === sIdx);
        s.setAttribute('aria-hidden', String(k !== sIdx));
      });
      sTabs.forEach((t, k) => {
        const on = k === sIdx;
        t.classList.toggle('active', on);
        t.classList.toggle('done', k < sIdx);
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
      });
      sCur.textContent = String(sIdx + 1).padStart(2, '0');
      // restart the active tab's progress bar
      const bar = $('.spick-bar i', sTabs[sIdx]);
      bar.style.animation = 'none'; void bar.offsetWidth; bar.style.animation = '';
      if (focus) sTabs[sIdx].focus({ preventScroll: true });
      // phones: the picker scrolls sideways, keep the active tab centred
      if (pick.scrollWidth > pick.clientWidth) {
        const t = sTabs[sIdx];
        pick.scrollTo({ left: t.offsetLeft - (pick.clientWidth - t.offsetWidth) / 2, behavior: reduceMotion ? 'auto' : 'smooth' });
      }
    }
    // autoplay: when the active tab's progress bar fills, move on
    if (!reduceMotion) {
      sTabs.forEach((t, k) => $('.spick-bar i', t).addEventListener('animationend', () => { if (k === sIdx) showStory(sIdx + 1); }));
      // hold the first portrait wipe until the stage scrolls into view
      stories[0].classList.remove('active');
    }
    sTabs.forEach((t, k) => t.addEventListener('click', () => showStory(k)));
    pick.addEventListener('keydown', (e) => {
      const d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
      if (d) { e.preventDefault(); showStory(sIdx + d, true); }
    });
    $('#sPrev').addEventListener('click', () => showStory(sIdx - 1));
    $('#sNext').addEventListener('click', () => showStory(sIdx + 1));
    new IntersectionObserver((en) => {
      sInView = en[0].isIntersecting;
      if (sInView && !sStarted) { sStarted = true; showStory(0); }
      setSPaused();
    }, { threshold: 0.35 }).observe(stage);
    [stage, pick].forEach((el) => {
      el.addEventListener('mouseenter', () => { sHover = true; setSPaused(); });
      el.addEventListener('mouseleave', () => { sHover = false; setSPaused(); });
    });
    // swipe between stories on touch screens
    let sx = null, sy = 0;
    stage.addEventListener('touchstart', (e) => { sx = e.touches[0].clientX; sy = e.touches[0].clientY; }, { passive: true });
    stage.addEventListener('touchend', (e) => {
      if (sx === null) return;
      const dx = e.changedTouches[0].clientX - sx, dy = e.changedTouches[0].clientY - sy;
      sx = null;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) showStory(sIdx + (dx < 0 ? 1 : -1));
    });
    setSPaused();
  }

  /* ---------- Treatment tabs: sliding underline, arrow keys ---------- */
  const tabBar = $('.tabs');
  const tabs = $$('.tab', tabBar);
  const panels = $$('.panel');
  const tabInd = $('.tabs-ind', tabBar);
  const moveInd = () => {
    const t = tabs.find((x) => x.classList.contains('active'));
    if (!t) return;
    tabInd.style.width = `${t.offsetWidth}px`;
    tabInd.style.transform = `translateX(${t.offsetLeft}px)`;
  };
  function activateTab(name, focus) {
    tabs.forEach((t) => {
      const on = t.dataset.tab === name;
      t.classList.toggle('active', on);
      t.setAttribute('aria-selected', String(on));
      t.tabIndex = on ? 0 : -1;
      if (!on) return;
      if (focus) t.focus({ preventScroll: true });
      // phones: the tab bar scrolls sideways, keep the active tab centred
      if (tabBar.scrollWidth > tabBar.clientWidth) {
        tabBar.scrollTo({ left: t.offsetLeft - (tabBar.clientWidth - t.offsetWidth) / 2, behavior: reduceMotion ? 'auto' : 'smooth' });
      }
    });
    panels.forEach((p) => p.classList.toggle('active', p.dataset.panel === name));
    if (tabInd) moveInd();
  }
  if (tabInd) {
    tabBar.classList.add('has-ind');
    moveInd();
    window.addEventListener('resize', moveInd);
    if (document.fonts) document.fonts.ready.then(moveInd);
  }
  tabs.forEach((t) => t.addEventListener('click', () => activateTab(t.dataset.tab)));
  // phones: drop the right-edge fade once the bar is scrolled to its end
  const tabsEnd = () => tabBar.classList.toggle('at-end', tabBar.scrollLeft + tabBar.clientWidth >= tabBar.scrollWidth - 4);
  tabsEnd();
  tabBar.addEventListener('scroll', tabsEnd, { passive: true });
  window.addEventListener('resize', tabsEnd);
  tabBar.addEventListener('keydown', (e) => {
    const i = tabs.findIndex((t) => t.classList.contains('active'));
    const k = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: tabs.length - 1 }[e.key];
    if (k === undefined) return;
    e.preventDefault();
    activateTab(tabs[(k + tabs.length) % tabs.length].dataset.tab, true);
  });
  $$('[data-tab-link]').forEach((a) => a.addEventListener('click', () => activateTab(a.dataset.tabLink)));
  // fetch the hidden tabs' and closed rows' photos before their section arrives,
  // so switching never shows an empty frame
  [$('#treatments'), $('.tlist')].forEach((sec) => new IntersectionObserver((en, obs) => {
    if (!en[0].isIntersecting) return;
    $$('img[loading="lazy"]', sec).forEach((img) => { img.loading = 'eager'; });
    obs.disconnect();
  }, { rootMargin: '800px 0px' }).observe(sec));

  // heterochromia tab: before / after toggle
  const hx = $('#hxFrame');
  $$('[data-hx]').forEach((b, _, all) => b.addEventListener('click', () => {
    hx.classList.toggle('matched', b.dataset.hx === 'matched');
    all.forEach((o) => { o.classList.toggle('on', o === b); o.setAttribute('aria-pressed', String(o === b)); });
  }));

  /* ---------- Shade library: hover/click opens a row, auto-cycles until the visitor picks one ---------- */
  const tl = $('#tlist');
  if (tl) {
    const items = $$('li', tl);
    let tIdx = 0, tlHold = false, tlInView = false, tlPicked = false;
    const setItem = (i) => {
      tIdx = i;
      items.forEach((li, k) => {
        li.classList.toggle('active', k === i);
        $('.tl-btn', li).setAttribute('aria-expanded', String(k === i));
      });
    };
    items.forEach((li, k) => {
      $('.tl-btn', li).addEventListener('click', () => { tlPicked = true; setItem(k); });
      if (window.matchMedia('(hover: hover)').matches) li.addEventListener('mouseenter', () => setItem(k));
    });
    // hovering or keyboard focus inside the list holds the cycle
    tl.addEventListener('mouseenter', () => { tlHold = true; });
    tl.addEventListener('mouseleave', () => { tlHold = false; });
    tl.addEventListener('focusin', () => { tlHold = true; });
    tl.addEventListener('focusout', () => { tlHold = false; });
    new IntersectionObserver((en) => { tlInView = en[0].isIntersecting; }, { threshold: 0.3 }).observe(tl);
    if (!reduceMotion) setInterval(() => { if (tlInView && !tlHold && !tlPicked) setItem((tIdx + 1) % items.length); }, 4200);
  }

  /* ---------- FAQ: topic filter, two balanced columns, one open at a time ---------- */
  const faqList = $('#faqList');
  const faqs = $$('.faq-item');
  const faqFilters = $$('.faq-filter');
  if (faqList) {
    const cols = [0, 1].map(() => { const c = document.createElement('div'); c.className = 'faq-col'; return c; });
    faqList.classList.add('split');
    faqList.append(...cols);
    faqFilters.forEach((f) => {
      const cat = f.dataset.cat;
      $('small', f).textContent = cat === 'all' ? faqs.length : faqs.filter((d) => d.dataset.cat === cat).length;
    });
    const layoutFaq = (cat) => {
      const vis = faqs.filter((d) => cat === 'all' || d.dataset.cat === cat);
      faqs.forEach((d) => { d.hidden = !vis.includes(d); if (d.hidden) d.open = false; });
      const half = Math.ceil(vis.length / 2);
      vis.forEach((d, i) => cols[i < half ? 0 : 1].appendChild(d));
    };
    faqFilters.forEach((f) => f.addEventListener('click', () => {
      faqFilters.forEach((o) => { const on = o === f; o.classList.toggle('active', on); o.setAttribute('aria-selected', String(on)); });
      layoutFaq(f.dataset.cat);
    }));
    layoutFaq('all');
  }
  faqs.forEach((d) => d.addEventListener('toggle', () => {
    if (d.open) faqs.forEach((o) => { if (o !== d) o.open = false; });
  }));

  /* ---------- Footer closing prompt → WhatsApp (an empty message still opens the chat) ---------- */
  const fForm = $('#footerPrompt');
  if (fForm) {
    fForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const text = $('#footerInput').value.trim();
      const msg = text ? `Hi İrisya Clinic, I'd like a free shade plan.\n\n${text}` : WHATSAPP_DEFAULT_MSG;
      window.open(waLink(msg), '_blank', 'noopener');
      toast('Opening WhatsApp — our coordinators usually reply within minutes.');
    });
  }

  /* ---------- Footer year ---------- */
  const yr = $('#year');
  if (yr) yr.textContent = new Date().getFullYear();
})();
