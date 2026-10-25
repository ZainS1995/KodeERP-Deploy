# Kodenova Design System — ERP Implementation Spec (from Zain, 2026-10-19)
Source: real Kodenova CSS (global.css, home-l.css, inner.css, Base.astro script). Values copied from code. Live site is the LIGHT theme (body.tl). Dark values only for footer/dark accents. THIS IS THE SOURCE OF TRUTH; it overrides earlier extracted values.

## 1. Tokens, fonts, base
FONTS (self-host woff2, font-display: swap)
- Urbanist (variable 100–900): ALL headings, body, buttons, nav, labels. Fallback: Inter, system-ui, sans-serif
- Inter (variable 100–900): fallback / dense data tables
- DM Mono 400: only code/IDs/small technical labels
- Instrument Serif 400: ONLY one big decorative display word (e.g. "Grow"), 80–150px

COLOR TOKENS
:root{ --bg:#f3f3f4; --card:#ffffff; --ink:#0e0e10; --ink2:#3a3a40; --mute:#6c6c74; --hl:#ffd23f; /* yellow highlighter */ --blue:#2a5ff0; /* primary; button-blue also #2f6bff, hover #1f58e6 */ --dk:#0f0f10; --dk2:#18181a; --line:#00000017; --hair:#0000000d; --ok:#18b26b; --ok-text:#0f7a43; --warn:#ff6a3d; --amber:#f5b800; }
Other greys: #f6f6f7 (inner surface), #ececef (skeleton lines), #e6e6e9, #cfd0d6 (wires), #1f2a44 (card titles). Page bg = var(--bg). Cards = white, NO border, soft shadow. Selection: background var(--hl), color #000.

TYPE
- body: Urbanist 17px, lh 1.55, antialiased
- h1: 700, clamp(44px,5.6vw,80px), lh 1.05, ls -.03em (hero weight 400)
- h2: 700, clamp(34px,4.6vw,60px), lh 1.05, ls -.025em
- h3 card: 700, 18–24px, lh 1.2–1.3, ls -.01em
- body small: 14.5–15px / lh 1.55–1.6, color var(--mute)
- eyebrow/labels: 600 12–13px uppercase, ls .04–.08em, 8px round yellow dot before
- .hl{background:var(--hl);padding:0 .12em;border-radius:.12em;box-decoration-break:clone}

RADII / SHADOWS
- Buttons 10–14px; cards 14–28px (service 14, big 22–28); pills 99px; shell sections 40px
- card shadow: 0 18px 40px #0000000d, 0 2px 6px #00000008
- card hover: 0 28px 60px #00000014
- floating header bar: 0 2px 10px #0000000a, 0 0 0 1px #0000000d
- blue button shadow: 0 10px 24px #2f6bff40

LAYOUT
- container max 1200px, side padding clamp(20px,4vw,48px); section padding clamp(70px,9vw,120px) 0
- grids 4→2 col at ≤1000px →1 col at ≤520–560px, gap 18–22px

## 2. Components
HEADER: floating white bar, centered, max-width 900px, h 60px, radius 16px, top 30px (absolute), padding 0 6px 0 26px. Logo left, nav Urbanist 400 14.5px gap 24–28px color #1d1d20 hover #000; right: round 44px white icon buttons (ring 0 0 0 1px #00000014) + dark CTA (h48, radius 12, bg #0e0e10, #fff 500 16px, hover #26262a). Mobile ≤960px: nav becomes white dropdown card (radius 20, shadow 0 20px 40px #0000001a).

BUTTONS
- Primary blue: bg #2f6bff, white, 500–600 16px Urbanist, padding 14px 26px, radius 10 (variant .l-btn: radius 14, padding 10px 10px 10px 22px with 28px circular outlined arrow ring right). Hover translateY(-1/-2px), bg #1f58e6, bigger shadow. Transition .2s.
- Secondary/ghost: white bg, 1px #0000001a border, ink text, radius 14.
- Dark pill: bg #0e0e10, white, radius 99, 14.5px 600; hover #2a2a2e.

CARDS
- Service card: white, radius 14, padding 40px 26px 36px, centered, 64px line-illustration, h3 18px/700 #1f2a44, p 14.5px #6c6c74 max-w 230px. Hover: translateY(-6px), larger shadow, icon scale(1.1) rotate(-4deg), h3 → #ff6a3d, 3px orange underline grows from center to 40%.
- Case study: white radius 22, image header 190–210px (radius 16, inset 10px), white country pill top-left (600 12px radius 99), industry label 11px uppercase ls .08em #ff6a3d, title 19–20px/700, 2-line clamp, "→" link slides 5px on hover, image scale 1.06 (.8s). Slider scroll-snap, 48px round prev/next, dots 8px (active 26px pill #111).
- Plan/feature cards: white radius 24, padding 52px 26px 26px, 60px circular icon badge overlapping top edge, tag pill #f3f3f4, checklist with 17px circle-check bullets.
- Tabs: left list of white 14px-radius tab buttons (selected bg ink, text white, count in yellow), right white panel radius 24.
- FAQ: details/summary 600 18px, "+" blue, "–" open, divider #00000014.
- Chips: white, 1px #0000001a, radius 99, 13px.
- KPI/status: green #18b26b check circles, ok text #0f7a43, pending #ff6a3d.
- Glass cards: bg #ffffff47, backdrop-filter blur(14px), inset ring #ffffff80, radius 26.

HERO: gradient linear-gradient(180deg,#a9a9ac 0%,#c9c9cc 45%,#f1f1f2 100%), centered h1 weight 400, sub 16px #3a3a40 max-w 440, one blue CTA, animated growth chart (white translucent bars #ffffffa6, amber line #f5b800 4px round caps, pulsing dot, black pill tooltip, floating white chips with green check).
FOOTER: white, radius 40px 40px 0 0, 4-col links #6c6c74 (hover ink), round 30–40px social buttons #f3f3f4, bottom row border #0000000f, 12px #6c6c74.
DARK ACCENT ZONE (optional): bg #0f0f10, radius 40 40 0 0, cards linear-gradient(180deg,#1d1d20,#151517) + inset ring #ffffff12, text #f5f5f7, muted #9a9aa2.

## 3. Animations
Easing everywhere: cubic-bezier(.2,.7,.2,1). Spring pop: cubic-bezier(.3,1.5,.5,1).
SCROLL REVEAL (IntersectionObserver adds .in; threshold .1; "both" observer toggles on enter/exit rootMargin '-22% 0px -8% 0px'; hero fires once; .js/.no-js on <html>, show all when JS off)
- .fade: opacity 0, translateY(18px) → none, .8s, delay .3s
- .reveal-lines: each line in overflow:hidden wrapper, inner span translateY(105%)→0, .9s, stagger .12s; on white sections from translateX(-105%) (1s, stagger .15s); .hl highlight wipes background-size 0→100% .9s delay .55s
- [data-ani]: opacity 0 + translateY(28px) → none (.7s opacity/.9s transform); page h1 translateY(40px)+blur(6px) → clear (1s); grid children translateY(30px) scale(.97) → none (.8s) stagger 70ms up to 8, then .55s
- Service grid: cards translateY(46px) scale(.94) → none .8s stagger 80ms*i; icon strokes draw (dasharray 240 → offset 0, 1.4s, delay .3s+80ms*i), fills fade after .9s; icons float 0 -6px 4s ease-in-out delay 1.6s+.25s*i
- Mock rows: opacity 0 translateY(10px) → none .6s stagger .1s; one row pops scale(1.03) with shadow
- Flow diagram: wires draw (offset 1→0, 1.4s, delay .2s), steps fade-up .7s delay 1s+.15s*i
- Orbit: rings scale(.6)→1 + fade (.8–1s stagger .1s), satellites .3→1 spring (.6s, delays .7/.85/1s)
- Growth chart: card translateY(60px)→0 (1s delay .2s); bars scaleY 0→1 from bottom (.7s delay .5s+60ms*i); line draws 2s delay 1.1s cubic-bezier(.45,.05,.2,1); dot ping 1.8s infinite (scale .6→1.8, opacity .9→0); chips spring .6s delays 1.8/2.3/2.8s then bob 5s
- Grow visual: photo translateY(40px) scale(.96) → none 1.1s; chips/glass translateY(20px) → none spring delays .5/.65/.8/.95s
CONTINUOUS: float translateY(-14px)@50% 6s; rot orbit 22s linear; bob 0 -6px 5s; drift translate(14px,-12px) rotate(12deg) 9s; marquee translateX(-50%) 40s linear; micro: tkPulse, tkNudge, tkShine, tkJiggle, tkFlash, kcDot.
HOVER/MICRO: cards translateY(-4…-8px)+shadow .25–.3s; buttons translateY(-1…-2px); link arrows translateX(5px); card images scale(1.06) .8s; carousel dots 8→26 .3s.
ACCESSIBILITY: prefers-reduced-motion: reduce → disable all animations/transitions, opacity 1, transform none, stroke-dashoffset 0. :focus-visible{outline:3px solid var(--blue);outline-offset:3px}
JS: ~15 lines vanilla IntersectionObserver; 3s safety timeout adds .in to everything.

## ERP adaptation rules
- Light bg #f3f3f4 + white cards; yellow only highlighter/accent; blue only for primary actions.
- Dense tables: Inter/Urbanist 14px, row hover #f6f6f7, header 12px uppercase 600 ls .06em #6c6c74, no heavy borders (1px #00000017).
- Animations only for entrances and hover; no looping animation inside data screens.
