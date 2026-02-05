---
title: Entity Resolution is Recipe Matching
date: 2026-02-05
type: explanation
summary: When exact matching fails, probabilistic record linkage weighs evidence like a chef recognizes a dish—not by a single ingredient, but by the whole picture.
tags:
  - entity resolution
  - splink
  - data quality
  - financial services
  - python
---

Birria in Jalisco is goat, slow-braised in dried chiles and served in a bowl with consommé. In Tijuana, it's beef, crisped on a plancha and folded into a taco. At Chipotle, it's a menu item with queso. Three different presentations, three different proteins, three different contexts—but you recognize them as the same dish.

You're not matching on a single ingredient. You're weighing evidence across multiple dimensions: the chile base, the braising technique, the way it's served with its cooking liquid.

Entity resolution works the same way. When you have two database records—"José García, 123 Main St, DOB 1985-03-15" and "GARCIA, JOSE M., 123 Main Street, DOB 03/15/1985"—you need to determine if they represent the same person. No single field gives you certainty, but together, the evidence points strongly toward a match.

I solved this problem on a project in financial services: deduplicating customer records, linking transactions across systems, matching entities without shared keys. It's harder than it looks, and most engineers reach for exact matching first—which works until it doesn't.

---

## Why Exact Matching Fails

The instinct is to write rules:

> If name matches **AND** DOB matches **AND** address matches → same person

This is **deterministic matching**, and it breaks the moment it touches real-world data.

Consider what customer data actually looks like:

| Field | System A | System B |
|-------|----------|----------|
| Name | José García | GARCIA, JOSE M. |
| Address | 123 Main St | 123 Main Street, Apt 2B |
| DOB | 1985-03-15 | 03/15/1985 |
| Email | jose.garcia@gmail.com | jgarcia85@yahoo.com |

Exact matching finds **zero matches** here. Every field differs in format, abbreviation, or completeness. But a human reviewer immediately recognizes this as likely the same person.

You could write transformation rules—normalize names to uppercase, expand abbreviations, standardize date formats. This helps, but it's a game of whack-a-mole:

- "José" vs "Jose" vs "Joe"
- "García" vs "Garcia"
- "123 Main" vs "123 Main St" vs "123 Main Street"
- Typos: "Josè Garçia" → "José García"

Deterministic matching forces a binary decision: match or no match. Reality is probabilistic—some pairs are definite matches, some definite non-matches, and a large gray zone requires weighing evidence.

![Deterministic matching gives binary yes/no decisions, while probabilistic matching produces weighted scores with room for manual review](/deterministic-vs-probabilistic.svg)

---

## Probabilistic Matching: Weighing Evidence

Probabilistic record linkage flips the question. Instead of asking "do these records match?" it asks:

> How likely is it that these records refer to the same entity, given the evidence?

Each field comparison contributes evidence:

| Comparison | Evidence |
|------------|----------|
| Exact name match | Strong positive |
| Fuzzy name match (Jaro-Winkler > 0.9) | Moderate positive |
| DOB matches | Strong positive |
| DOB off by one digit | Weak positive (likely typo) |
| Completely different DOB | Strong negative |

The accumulated evidence produces a **match score**.

This mirrors how you recognize birria. If two recipes both have dried chiles, braised meat, and a rich cooking liquid served alongside, that's strong evidence they're the same dish. If one uses guajillo and the other uses ancho, that's weak variation—regional preference, not a different dish. If one serves it in a bowl and the other crisps it in a taco, that's presentation, not identity.

But if one is a quick stovetop stew without the slow braise? That's evidence you're looking at something else entirely—maybe carne guisada, but not birria.

---

## The Fellegi-Sunter Model (Without the Math)

The math behind probabilistic matching is the **Fellegi-Sunter model**, developed in 1969 and still the foundation of modern record linkage.

Fellegi-Sunter assigns each field comparison a weight based on two probabilities:

| Probability | Question |
|-------------|----------|
| **m-probability** | If two records truly match, how often would this field comparison look like this? |
| **u-probability** | If two records *don't* match, how often would this field comparison look like this by chance? |

The ratio of these probabilities determines the weight:

- **Names match exactly**: Common among true matches (high m), rare among random pairs (low u) → **positive weight**
- **Names completely differ**: Rare among true matches (low m), common among random pairs (high u) → **negative weight**

### Common vs. Rare Values

Here's the key insight: **common values provide weaker evidence than rare values**.

"María García" matching "María García" is less compelling than "Xiomara Tlapoyawa" matching "Xiomara Tlapoyawa." The first could happen by coincidence in any large dataset; the second almost certainly indicates the same person.

Think of it like identifying a mole. If two recipes both contain chiles, that tells you almost nothing—every mole has chiles. But if both call for chocolate, banana, and chipotle in specific proportions, you're probably looking at variations of mole negro from Oaxaca.

> The rare, specific ingredients carry more weight than the ubiquitous ones.

Splink handles all of this automatically. You define what fields to compare and how (exact match, fuzzy match, within a date range), and Splink estimates the m and u probabilities using unsupervised learning—no labeled training data required.

---

## The Blocking Problem

There's a computational catch. If you have a million records, comparing every pair means:

```
1,000,000 × 999,999 / 2 = 499,999,500,000 comparisons
```

That's **500 billion comparisons**. Not feasible.

**Blocking** solves this by only comparing records that could plausibly match. You define rules like:

- Only compare records where first name initial AND birth year match
- Only compare records in the same city
- Only compare records with similar phone area codes

![Without blocking: 500 billion comparisons taking weeks. With blocking: grouped comparisons completing in minutes](/blocking-comparison.svg)

This is **mise en place** for data matching—organizing your workspace before you start cooking. A chef doesn't wander the entire kitchen looking for ingredients during service. They set up their station with everything they'll need in reach. Blocking sets up your comparison space so you're only looking where matches are likely to be found.

The art is in the balance:

| Problem | Cause |
|---------|-------|
| Missing matches | Blocking too aggressive—true pairs never compared |
| Slow performance | Blocking too loose—comparing pairs that obviously don't match |

---

## Why Splink?

You could implement Fellegi-Sunter from scratch, but [Splink](https://moj-analytical-services.github.io/splink/) handles the hard parts:

| Feature | What it does |
|---------|--------------|
| **Unsupervised training** | Estimates m/u probabilities without labeled data (Expectation-Maximization) |
| **Multiple backends** | DuckDB (laptop), Spark (cluster), AWS Athena (serverless) |
| **Fuzzy matching** | Jaro-Winkler, Levenshtein, phonetic matching built-in |
| **Term frequency** | Automatically down-weights common values like "José García" |
| **Visualization** | Inspect match weights, debug blocking rules, understand model behavior |

It's open source, built by the UK Ministry of Justice, and battle-tested on national-scale datasets including the 2021 Census.

---

## Why This Matters in Financial Services

Entity resolution isn't an academic exercise. In financial services, getting it wrong has real consequences:

| Use Case | Cost of Getting It Wrong |
|----------|--------------------------|
| **KYC/AML compliance** | Fragmented risk profiles, regulatory failures |
| **Fraud detection** | Missed patterns across linked identities |
| **M&A data migration** | Duplicate customers in merged systems |
| **Regulatory reporting** | Incorrect unique customer counts |

The cost of **false negatives** (missed matches) is fragmented data and compliance risk. The cost of **false positives** (incorrect matches) is merged records for different people—a data quality nightmare.

Probabilistic matching lets you tune the tradeoff for your specific use case.

---

## Key Takeaways

- **Entity resolution** determines if records refer to the same real-world entity when no shared key exists
- **Exact matching breaks** on real-world data—typos, format variations, and abbreviations defeat deterministic rules
- **Probabilistic matching** weighs evidence across fields, producing a match score rather than a binary decision
- **Common values** (María, García) provide weaker evidence than **rare values** (Xiomara, Tlapoyawa)
- **Blocking** reduces the comparison space from n² to something tractable
- **Splink** handles the math, scales from laptops to clusters, and requires no labeled training data

---

## Further Reading

- [Splink Documentation](https://moj-analytical-services.github.io/splink/)
- [Fellegi-Sunter Model Explained](https://www.robinlinacre.com/probabilistic_linkage/)
- [Data Matching (Springer)](https://link.springer.com/book/10.1007/978-3-642-31164-2)
- [Record Linkage at Scale: A UK Government Perspective](https://dataingovernment.blog.gov.uk/2022/09/23/splink-fast-accurate-and-scalable-record-linkage/)
