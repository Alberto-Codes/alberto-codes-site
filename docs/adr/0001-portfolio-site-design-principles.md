# ADR-0001: Portfolio Site Design Principles

## Status

Accepted

## Date

2026-02-01

## Context

We are building a personal portfolio site for Alberto Nieto (alberto-codes-site) using the Reflex framework in Python. The site serves as a professional presence for a Generative AI Principal Engineer with 25+ years of experience. We need to establish design principles that align with current best practices for developer portfolio sites in 2026.

Key questions:

- What layout and design approach should the site follow?
- What content sections are essential?
- How should performance and UX be handled?
- What level of animation/interactivity is appropriate?

## Decision

We will follow these design principles for the portfolio site:

### 1. Minimalist, Clean Design

The site will use a minimalist layout with bold typography, clear section hierarchy, and generous whitespace. This aligns with the dominant trend in top developer portfolios in 2026 and provides the best UX across devices.

### 2. Required Content Sections

The site will include at minimum:

- **Home/Hero** - Name, title, headshot photo, brief tagline, and CTA buttons
- **About** - Professional bio with headshot, personal story, and key stats
- **Experience** - Career timeline
- **Projects** - Showcase of technical work (quality over quantity)
- **Contact** - Contact information and social links
- **Blog** - Articles to establish thought leadership (planned)
- **Resume** - Downloadable PDF

### 3. Performance First

- Compress and optimize all images (headshot cropped to square, minimal file size)
- Minimize JavaScript bundle size
- Leverage Reflex's built-in SSR capabilities where possible

### 4. Mobile-Responsive

All layouts must work across mobile, tablet, and desktop. Use Reflex breakpoints (`rx.breakpoints`) for responsive sizing. Complex layouts (e.g., side-by-side headshot + bio) should stack or hide elements on smaller screens.

### 5. Subtle Animation Only

Use minimal, purposeful animations (hover effects, smooth scrolling). Avoid heavy animation libraries or distracting motion. The focus is on content and professionalism.

### 6. Personal Branding

- Consistent color scheme anchored around blue accent tones
- Professional headshot prominently displayed on home and about pages
- Custom domain (when deployed)

## Consequences

### Positive

- Clean, professional presentation appropriate for a principal-level engineer
- Fast load times and good SEO from minimal design
- Responsive layout works across all devices
- Clear structure makes content easy to find and update

### Negative

- Minimalist approach may feel less visually striking than heavily animated portfolio sites
- Reflex framework is less common than Next.js/React, which limits available component libraries and community examples
- Single-page or few-page structure may need rethinking if content grows significantly

## References

- [Colorlib - Developer Portfolios 2026](https://colorlib.com/wp/developer-portfolios/)
- [Elementor - Best Web Developer Portfolio Examples](https://elementor.com/blog/best-web-developer-portfolio-examples/)
- [Colorlib - Portfolio Design Trends 2026](https://colorlib.com/wp/portfolio-design-trends/)
- [Webflow - Portfolio Examples & Best Practices](https://webflow.com/blog/design-portfolio-examples)
- [ADR GitHub Organization](https://adr.github.io/)
- [MADR Template](https://adr.github.io/madr/)
