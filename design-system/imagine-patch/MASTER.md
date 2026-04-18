# Imagine Patch — Design System MASTER
> Source of truth for all pages. Page-specific overrides live in `pages/[page].md`.
> When building a page, check `design-system/imagine-patch/pages/[page].md` first — it overrides this file.

---

## Brand Concept
**Rainbow magic shop run by a friendly witch.** Light and welcoming on the outside, enchanted and mysterious if you look closer. Y2K magical girl energy meets celestial witchy undertones.

---

## Color Palette

| Token | Hex | Usage |
|---|---|---|
| `purple` | `#7B2FBE` | Primary brand, CTAs, borders |
| `purple-dark` | `#5B1A9A` | Hover states, depth |
| `purple-light` | `#9D4EDD` | Secondary accents |
| `purple-deep` | `#1A0A2E` | Mystical dark sections |
| `midnight` | `#0F0624` | Footer, deepest dark |
| `gold` | `#F5C842` | Star/sparkle accents |
| `gold-light` | `#FFE580` | Star highlights |
| `pink` | `#FF6EB4` | Heart accents |
| `pink-light` | `#FFB3D9` | Soft pink fills |
| `cream` | `#FDF8FF` | Page background |
| `lavender` | `#F3E8FF` | Section alternate background |

**Rainbow accents (sparingly — highlight only):**
Red `#FF6B6B` | Orange `#FF9F43` | Yellow `#FECA57` | Cyan `#48DBFB` | Pink `#FF9FF3`

**Rules:**
- Never use generic purple/pink AI gradients — brand purple `#7B2FBE` only
- Dark sections allowed but must be <30% of total page area
- Rainbow: max 1–2 elements per section, never as backgrounds

---

## Typography

| Role | Font | Usage |
|---|---|---|
| Hero Display | Pacifico | Hero headlines only |
| Section Headlines | Fredoka One | Section headers, product titles |
| Body | Nunito 300/400/600 | All body copy |
| Mystical Accent | Cormorant Garamond 300 italic | Labels, mystical callouts |

```css
@import url('https://fonts.googleapis.com/css2?family=Pacifico&family=Fredoka+One&family=Nunito:wght@300;400;600;700&family=Cormorant+Garamond:ital,wght@0,300;1,300;1,400&display=swap');
```

**Scale:** Hero 56px (mob:36px) | H2 36px (mob:28px) | H3 card 20px | Body 16px min | Label 13px
**Line height:** 1.6 body | 1.2 headlines | **Max line length:** 65ch

---

## Spacing
Base: 4px. Section vpad: 64–96px desktop / 48px mobile. Container: max-w-[1200px] px-4 md:px-6 lg:px-8. Card gap: 24px.

---

## Component Styles

### Primary Button
bg `#7B2FBE`, white text, radius 50px, border 3px solid `#5B1A9A`, padding 14px 32px, min-h 44px
Shadow: `4px 4px 0px #5B1A9A` | Hover: bg `#5B1A9A`, translateY(2px), shadow `2px 2px 0px #3D0F70`

### Secondary Button
white bg, border 2px `#7B2FBE`, purple text | Hover: bg `#F3E8FF`

### Ghost Button (dark sections only)
transparent, border 1px white, white text | Hover: bg `rgba(255,255,255,0.1)`

### Product Cards
- bg white, border 2px solid `#E9D5FF`, radius 20px, shadow `0 4px 16px rgba(123,47,190,0.08)`
- Hover: border `#7B2FBE`, shadow `0 8px 32px rgba(123,47,190,0.25)`, translateY(-4px), 250ms ease-out
- Image: aspect-ratio 1:1, object-fit cover, radius 16px top
- Price: Fredoka One, `#7B2FBE`

### Badges
radius 50px, pad 4px 12px, Cormorant Garamond italic 13px
New: bg `#F5C842` dark text | Sale: bg `#FF6EB4` white | Mystical: bg `#1A0A2E` gold text

### Navigation
Sticky, bg white/95 backdrop-blur, border-bottom 1px `#E9D5FF`. Z-index 30.

---

## Animations
- duration: 150ms micro | 250ms hover/nav | 400ms entrance
- ease-bounce: `cubic-bezier(0.34, 1.56, 0.64, 1)`
- `sparkle-float`: translateY -6px + scale 1.05, 3s infinite alternate
- `star-pulse`: scale 1→1.2, opacity flicker, 2s infinite
- All gated behind `@media (prefers-reduced-motion: no-preference)`

## Z-Index
Base 0 | Cards 10 | Sticky nav 30 | Overlays 40 | Modals 50

## Anti-Patterns
- No generic purple/pink AI gradients
- No emojis as icons (inline SVG only)
- No rainbow backgrounds
- No dark mode default
- Mystical dark sections ≤ 30% page
- No layout-shifting hover (transform/opacity only)
