/* ===== Group 8 — Edge Computing Cluster: Hero homepage styles ===== */
/* Drop this file at docs/stylesheets/extra.css and reference it in mkdocs.yml:
   extra_css:
     - stylesheets/extra.css
*/

:root {
  --ec-navy: #0f2942;
  --ec-navy-light: #163a5c;
  --ec-teal: #2dd4a7;
  --ec-subtext: #a9c4de;
}

/* Hide the default h1 spacing weirdness above the hero */
.md-content .ec-hero {
  margin: -1.2rem -1.2rem 2rem -1.2rem;
  padding: 3.5rem 2rem 3rem;
  background: linear-gradient(180deg, var(--ec-navy) 0%, var(--ec-navy-light) 100%);
  color: #fff;
  border-radius: 0 0 12px 12px;
}

.ec-hero__eyebrow {
  font-family: var(--md-code-font, monospace);
  letter-spacing: .12em;
  text-transform: uppercase;
  font-size: .78rem;
  color: var(--ec-teal);
  margin-bottom: .9rem;
}

.ec-hero__title {
  font-size: clamp(2.1rem, 5vw, 3.2rem);
  line-height: 1.08;
  font-weight: 800;
  margin: 0 0 1rem 0;
  letter-spacing: -0.01em;
}

.ec-hero__title span {
  color: var(--ec-teal);
}

.ec-hero__subtitle {
  max-width: 640px;
  font-size: 1.05rem;
  line-height: 1.6;
  color: var(--ec-subtext);
  margin-bottom: 1.8rem;
}

.ec-hero__badges {
  display: flex;
  flex-wrap: wrap;
  gap: .6rem;
}

.ec-badge {
  display: inline-flex;
  align-items: center;
  gap: .4rem;
  padding: .45rem .9rem;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.18);
  background: rgba(255,255,255,0.04);
  font-size: .82rem;
  color: #dce8f3;
  text-decoration: none !important;
}

.ec-badge--accent {
  border-color: rgba(45,212,167,0.5);
  color: var(--ec-teal);
}

/* ---- Quick link cards ---- */
.ec-links {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  margin: 1.5rem 0 2.5rem 0;
}

.ec-card {
  display: block;
  padding: 1.2rem 1.3rem;
  border: 1px solid var(--md-default-fg-color--lightest);
  border-radius: 10px;
  text-decoration: none !important;
  transition: transform .15s ease, box-shadow .15s ease;
  background: var(--md-default-bg-color);
}

.ec-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.08);
}

.ec-card__label {
  font-size: .72rem;
  letter-spacing: .1em;
  text-transform: uppercase;
  color: var(--ec-teal);
  font-weight: 700;
  margin-bottom: .35rem;
}

.ec-card__title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--md-default-fg-color);
}

/* ---- Metric strip ---- */
.ec-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin: 1.5rem 0 2.5rem 0;
}

.ec-metric {
  padding: 1rem;
  border-radius: 10px;
  background: var(--md-code-bg-color);
  text-align: center;
}

.ec-metric__value {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--ec-navy);
}

[data-md-color-scheme="slate"] .ec-metric__value {
  color: var(--ec-teal);
}

.ec-metric__label {
  font-size: .75rem;
  color: var(--md-default-fg-color--light);
  margin-top: .2rem;
}
