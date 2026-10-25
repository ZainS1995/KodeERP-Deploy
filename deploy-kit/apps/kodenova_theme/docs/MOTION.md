# Kodenova motion reference (kodenova.com, inspected 2026-10-19 22:35 PKT, UTC+5)

Source: homepage HTML + inline CSS/JS (`curl https://kodenova.com`). **No animation library**: no GSAP, Framer, Lenis, AOS, anime or Lottie. Only one script is external, Cloudflare's email-decode. Motion comes from plain CSS transitions/keyframes plus a tiny `IntersectionObserver` that adds `.in` to `.rv` / `.reveal-lines` elements.

| Pattern | kodenova.com value |
|---|---|
| Main easing ("out-expo-ish") | `cubic-bezier(.2,.7,.2,1)` (19 uses), `cubic-bezier(.2,.8,.2,1)` (10) |
| Springy overshoot (toggles, chips) | `cubic-bezier(.3,1.5,.5,1)` / `(.3,1.6,.5,1)`, 0.4–0.5s |
| Card hover lift | `transition: transform .25s, box-shadow .25s`; hover `translateY(-4px)` + `0 24px 50px #0000000d` |
| Button hover | `translateY(-1px)`, background `#0e0e10 → #26262a/#2a2a2e`, `.2s` |
| Scroll reveal | `.rv{opacity:0;transform:translateY(16px);transition:opacity .5s ease,transform .5s ease}` → `.rv.in{opacity:1;transform:none}`, only under `prefers-reduced-motion:no-preference` |
| Headline line reveal | `.ln>span{transform:translateY(105%);transition:transform .9s cubic-bezier(.2,.7,.2,1)}`, 120ms stagger per line |
| Highlighter sweep | `.hl` background-size `0 → 100%`, `.9s cubic-bezier(.2,.7,.2,1) .55s` |
| Card/chat entrance | `@keyframes kcIn{0%{opacity:0;transform:translateY(14px) scale(.98)}}`, `tkIn .35–.45s forwards` |
| Ambient | `float` (translateY −14/−16px, infinite), `drift` (translate 14px,−12px + rotate 12deg), `bob`, marquee, slow `rot`/`spin` 22–26s |
| Underline accent | `.svc-c:after` orange `#ff6a3d` 3px bar, width `0 → 40%`, `.35s ease` |
| Stagger | `calc(var(--i)*60ms)` delays |
| Reduced motion | `@media (prefers-reduced-motion:reduce){ … animation:none }` and reveals skipped |

## Applied to KodeERP (theme v0.4, `public/css/kodenova_motion.css`)

The site's 0.5–0.9s marketing reveals are compressed to **150–350ms** for an app, keeping the same curves. `--knm-ease: cubic-bezier(.2,.7,.2,1)` and `--knm-spring: cubic-bezier(.3,1.5,.5,1)`.

- Login: card `kcIn`-style entrance (320ms), highlighter sweep on the tagline (600ms, decorative, once), slow drifting brand-tint blobs behind the card (`drift`, 18–22s, GPU transform only).
- Desk: route enter fade-up of `.page-body` (220ms; only on `page-change`, never on form refresh/typing).
- Workspace: staggered fade-up of widget blocks, number cards included (240ms, 35ms steps, capped at 10).
- Hover lift + shadow on cards and shortcut tiles (`-2px`), and on buttons (`-1px`) with press feedback (`scale(.97)`, 90ms).
- Sidebar: active/hover background and colour transitions (180ms).
- Modals: scale/fade enter (240ms). Dropdowns/menus: fade/slide 160ms. Toasts: slide-up 260ms spring.
- Skeleton loaders: brand-tint shimmer (blue-soft ↔ soft grey), 1.2s loop.
- Charts: bars grow from the baseline (scaleY, 350ms staggered) and lines draw in (stroke-dash, 450ms).
- List rows: background hover transition 120ms.
- Excluded on purpose: inputs and grids (no transitions on value/typing; grid rows/cells are never animated), the datatable, the print view, and drag-and-drop.
- `prefers-reduced-motion: reduce` turns all of it off, leaving only instant state changes.
