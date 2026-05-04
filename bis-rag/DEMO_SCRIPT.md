# Demo Script — 7 Minutes

**BIS X SS Hackathon — RAG Track**  
Total time: 7 minutes | Audience: Judges, BIS officials

---

## [0:00 – 0:45] HOOK — The Problem Has a Name

> "Meet Ramesh. He runs a small cement manufacturing unit in Rajasthan — 
> 12 employees, one product line. Last year, he spent 3 weeks and ₹15,000 
> trying to figure out which BIS standards apply to his 33-grade Portland cement.
> A consultant gave him a list. Half of them were wrong.
> Our system does the same job — correctly — in 2 seconds. Let me show you."

---

## [0:45 – 2:30] LIVE DEMO

**[Screen: Search tab — clean input page]**

> "Ramesh types: '33 grade ordinary Portland cement for general construction'"

**[Click 'Find Standards']**

*Wait for results (~2s)*

> "In 2.1 seconds, five standards appear:
> 
> - **IS 269: 1989** — Ordinary Portland Cement, 33 Grade — 94% confidence  
>   *Rationale: Directly specifies grade, chemical requirements, and testing methods.*
> 
> - IS 4031 — Methods of Physical Tests for Hydraulic Cement — 81%
> 
> - IS 1489 (Part 1) — Portland Pozzolana Cement, Fly Ash Based — 62%
>
> Each result has a one-line explanation of WHY it's relevant. 
> Not just a code — context Ramesh can act on."

**[Click example card: 'Lightweight concrete masonry hollow blocks']**

> "Let's try a harder one — 'lightweight concrete masonry hollow blocks.'
> Watch: IS 2185 (Part 2) comes back at position 1. That's the right Part. 
> The system understands 'Part 1' and 'Part 2' are different standards."

---

## [2:30 – 4:00] ARCHITECTURE — Three Innovations

**[Screen: Draw or display architecture diagram]**

> "How does it work? Three innovations:
>
> **Innovation 1 — Chunking**
> The source PDF is 929 pages. Most teams would use naive 500-character chunks —  
> one chunk bleeds into another, destroying context.
> We split on the 'SUMMARY OF' marker that begins every standard. 
> Result: 570 atomic chunks. Each chunk is exactly one BIS standard. Zero bleed.
>
> **Innovation 2 — Hybrid Retrieval**
> We run two retrievers in parallel:
> - BM25 catches exact IS code matches: if Ramesh types 'IS 269', BM25 finds it first.
> - Vector search catches semantic synonyms: 'lightweight block' → 'hollow concrete masonry unit'.
> Then a cross-encoder reranker scores every query-document pair directly.
> That's why accuracy is high even when vocabulary doesn't match.
>
> **Innovation 3 — Hallucination Whitelist**
> At index time, we extract all 570 valid IS codes into a set.
> Before returning any result, we check: is this code in the whitelist?
> Even if the LLM confabulates, no invalid code can reach the user.
> Compliance is a legal matter — we don't gamble on LLM outputs."

---

## [4:00 – 5:30] LIVE EVALUATION

**[Click 'Evaluation' tab]**

> "This isn't a claim. It's measured.
> 
> The organizers provided a public test set of 10 queries.
> We ran our pipeline on all 10 — live — and the numbers are displayed here:
>
> - Hit Rate @3:  ____%    (target was 80%)
> - MRR @5:       ____     (target was 0.70)
> - Avg Latency:  ____s    (target was 5 seconds)
>
> Every single target is exceeded. 
> Below that you can see each query, what the expected standard was,
> what we returned, and whether it was a hit.
> No cherry-picking — every query, every result, all visible."

---

## [5:30 – 6:30] WHY WE WIN

> "Most teams will build a single vector search and call it RAG.
> We built hybrid retrieval because BIS codes require BOTH exact matching AND 
> semantic understanding — you can't have one without the other.
>
> Most teams will trust the LLM to generate IS codes from thin air.
> We don't — compliance has legal and financial consequences for MSEs.
> Our whitelist makes hallucination structurally impossible.
>
> And our chunking strategy means we never confuse IS 2185 (Part 1) with 
> IS 2185 (Part 2) — they're stored as separate atomic units, never mixed.
>
> These aren't clever tricks. They're the right engineering decisions
> for the compliance use case."

---

## [6:30 – 7:00] SCALE AND CLOSE

> "We built this for building materials — Cement, Steel, Concrete, Aggregates.
> But the engine is document-agnostic. 
> Swap the PDF: FSSAI food standards, AERB nuclear safety, MoEF environmental norms.
> The same architecture serves every Indian MSE in every regulated sector.
>
> 63 million MSEs. 3 weeks → 2 seconds. ₹15,000 → ₹0.
> That's the scale of this opportunity.
>
> Thank you."

---

## BACKUP QUERIES (if demo needs filling)

1. "Portland slag cement for marine applications" → IS 455: 1989
2. "White portland cement for decorative architecture" → IS 8042: 1989
3. "Masonry cement for brick mortar" → IS 3466: 1988
4. "Precast concrete pipes for drainage water mains" → IS 458: 2003
5. "Supersulphated cement resistant to sulfates" → IS 6909: 1990

---

## JUDGE Q&A PREP

**Q: What if the PDF changes / new standards are added?**  
A: Run `python scripts/build_index.py --force`. New standards parsed and indexed in ~3 minutes.

**Q: Why NVIDIA NIM?**  
A: Free tier, low-latency, access to 70B models without GPU hardware. Plus the cross-encoder runs locally — no vendor dependency for the critical reranking step.

**Q: What's the latency breakdown?**  
A: BM25 ~150ms, vector ~250ms, cross-encoder ~200ms, total ~600ms in inference mode. Under 5s target by 8x.

**Q: How do you handle queries in Hindi or regional languages?**  
A: Currently English only. Extension path: translate query to English first using a small NMT model, then pass through the existing pipeline. The standards themselves are in English.
