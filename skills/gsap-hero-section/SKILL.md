---
name: gsap-hero-section
description: Use when the user asks to upgrade a landing page hero section with GSAP animations, GSAP-style motion, or effects like split-text reveals, staggered entrances, magnetic buttons, and adaptive directional easing (easeReverse).
---

# GSAP Hero Section Skill

Use this skill when the task is to animate or upgrade the first viewport of a React/Tailwind website with GSAP, especially when the user references `gsap.com` or asks for "GSAP-level" hero motion.

Goal: ship a hero section with choreographed entrance animations, split-text title reveals, magnetic buttons, staggered feature cards, and polished ambient motion while keeping the bundle impact minimal and avoiding motion sickness.

## When to Use

- User says "用 GSAP 升级首页" / "对标 GSAP 首页" / "GSAP animation for hero"
- User references GSAP docs such as `Tween#easeReverse`, `useGSAP`, or SplitText-style effects
- The current hero feels static and needs entrance choreography

## When Not to Use

- The project already has a strong Framer Motion setup and the user did not ask for GSAP
- The page must minimize JS bundle (GSAP adds ~25-40 kB gzipped depending on imports)
- Accessibility requirements demand `prefers-reduced-motion` be strictly respected without wrappers

## Setup

Install GSAP and the React helper:

```bash
npm install gsap @gsap/react
```

## Implementation Blueprint

### 1. Replace the static HeroSection

Create or overwrite `src/components/home/HeroSection.tsx`.

Keep the existing data layer (i18n keys, buttons, feature cards) but replace the markup and motion layer.

### 2. Add a lightweight SplitText component

GSAP's official SplitText plugin is paid. For hero titles, implement a small React wrapper that splits text into per-character `<span>` elements and animates them with `gsap.fromTo`.

```tsx
function SplitText({
  children,
  className = '',
  delay = 0,
}: {
  children: string
  className?: string
  delay?: number
}) {
  const containerRef = useRef<HTMLSpanElement>(null)
  const chars = children.split('')

  useGSAP(
    () => {
      gsap.fromTo(
        containerRef.current?.querySelectorAll('.char') || [],
        { y: 80, opacity: 0, rotateX: -90 },
        {
          y: 0,
          opacity: 1,
          rotateX: 0,
          duration: 0.8,
          ease: 'back.out(1.7)',
          stagger: 0.03,
          delay,
        }
      )
    },
    { scope: containerRef }
  )

  return (
    <span ref={containerRef} className={`inline-block ${className}`}>
      {chars.map((char, index) => (
        <span
          key={index}
          className="char inline-block"
          style={{ display: char === ' ' ? 'inline' : 'inline-block' }}
        >
          {char === ' ' ? '\u00A0' : char}
        </span>
      ))}
    </span>
  )
}
```

Apply `perspective: 1000px` on the parent `<h1>` so `rotateX` has 3D depth.

### 3. Orchestrate entrance with a timeline

Use `useGSAP` with `gsap.timeline()` for badge, subtitle, buttons, and cards.

```tsx
useGSAP(
  () => {
    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } })

    tl.fromTo(badgeRef.current, { opacity: 0, y: 30, scale: 0.9 }, { opacity: 1, y: 0, scale: 1, duration: 0.8 }, 0.2)
    tl.fromTo(subtitleRef.current, { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.9 }, 0.8)
    tl.fromTo(
      buttonsRef.current?.children || [],
      { opacity: 0, y: 40, scale: 0.95 },
      { opacity: 1, y: 0, scale: 1, duration: 0.7, stagger: 0.12 },
      1.0
    )
    tl.fromTo(
      cardsRef.current?.children || [],
      { opacity: 0, y: 60, scale: 0.9 },
      { opacity: 1, y: 0, scale: 1, duration: 0.8, stagger: 0.15, ease: 'back.out(1.4)' },
      1.3
    )
  },
  { scope: sectionRef }
)
```

### 4. Ambient motion with `easeReverse`

For any `yoyo` loop, add `easeReverse: true` so the reverse phase keeps the same easing curve instead of mirroring it.

```tsx
// Background glow drift
gsap.to(glowRef.current, {
  x: 60,
  y: -40,
  scale: 1.1,
  duration: 10,
  repeat: -1,
  yoyo: true,
  ease: 'sine.inOut',
  easeReverse: true,
})

// Feature icons subtle pulse
gsap.to('.feature-icon', {
  scale: 1.08,
  duration: 2,
  repeat: -1,
  yoyo: true,
  ease: 'sine.inOut',
  easeReverse: true,
  stagger: { each: 0.4 },
})
```

### 5. Magnetic buttons with tween + reverse

Store per-element tweens in a `Map` and call `.reverse()` on leave.

```tsx
const magneticTweens = useRef<Map<HTMLElement, gsap.core.Tween>>(new Map())

const handleMouseMove = (e: React.MouseEvent<HTMLElement>) => {
  const el = e.currentTarget
  const rect = el.getBoundingClientRect()
  const x = e.clientX - rect.left - rect.width / 2
  const y = e.clientY - rect.top - rect.height / 2

  magneticTweens.current.get(el)?.kill()

  const currentX = (gsap.getProperty(el, 'x') as number) || 0
  const currentY = (gsap.getProperty(el, 'y') as number) || 0

  const tween = gsap.fromTo(
    el,
    { x: currentX, y: currentY },
    {
      x: x * 0.25,
      y: y * 0.25,
      duration: 0.4,
      ease: 'power2.out',
      easeReverse: true,
    }
  )

  magneticTweens.current.set(el, tween)
}

const handleMouseLeave = (e: React.MouseEvent<HTMLElement>) => {
  const tween = magneticTweens.current.get(e.currentTarget)
  if (tween) tween.reverse()
}
```

Bind the handlers to the actual anchor elements, not the `Button` wrapper, when using `asChild`.

## Design Defaults

- Keep the existing copy and CTA targets; only upgrade motion
- Preserve `prefers-reduced-motion`: the inline transforms from GSAP may still run. For production, consider wrapping GSAP animations in a reduced-motion guard or setting `gsap.globalTimeline.timeScale(0)` when the preference is active
- Use `will-change-transform` sparingly on animated buttons
- Keep the hero readable: animation should not delay the CTA by more than ~1.5 s

## Verification Checklist

- [ ] `npm install gsap @gsap/react`
- [ ] `npx tsc -b --noEmit` passes
- [ ] `npm run build` succeeds
- [ ] Hero title animates in with split-text effect
- [ ] Buttons and cards stagger in
- [ ] Magnetic buttons return to rest smoothly on mouse leave
- [ ] Background ambient motion loops without jank
