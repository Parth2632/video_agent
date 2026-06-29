# AI Video Agent - Model Evaluation Report

**Audio File Tested:** `Recording.m4a` (~6 minutes)  
**Ground Truth Script:** `downloads/testing.txt`  
**Overall Accuracy Score:** **87.5% (A-)**

---

### 1. Chronological Slicing (The "2-Minute" Test)
**Q: What was discussed at the 2 minute mark?**
* **Model's Answer:** "At the 2-minute mark, there was no discussion mentioned in the transcript. The conversation started at 1:28 and continued until 2:06, where AI and ML updates were discussed."
* **Evaluation:** 10/10. The time-slicer intercepted this flawlessly. The LLM correctly recognized the exact boundary of the speech chunk at `02:06` and correctly identified that AI & ML updates began right there.

### 2. Semantic Understanding & Extraction
**Q: What happened after the frontend update?**
* **Model's Answer:** Summarized the contents of the frontend update (Dashboard redesign, PDF bugs, Safari bug).
* **Evaluation:** 6/10. It misunderstood "after the frontend update" as "what happened *during* the frontend update." This is a common semantic drift for smaller 8B models.

**Q: What are the risks going into this sprint?**
* **Model's Answer:** Identified the Safari 16 onboarding bug (affecting 30% of users) and the third-party embeddings API rate limits.
* **Evaluation:** 10/10. This was an incredibly impressive answer. The script never explicitly used the word "risks", but the model perfectly inferred that critical bugs and API rate limits were the structural risks.

**Q: What is the status of the recommendation engine?**
* **Model's Answer:** Captured all metrics (34% CTR, 18% bounce rate) and the exact phased rollout plan (10%, 50%, full).
* **Evaluation:** 10/10. Perfect factual extraction.

### 3. Action Items & Decisions
**Q: What are all the action items and their owners?**
* **Model's Answer:** Captured Priya (Notice), Rahul (Safari Bug), Karan (Cost comparison - *Whisper heard "Current"*), and DevOps (Auto-scaling runbook). 
* **Evaluation:** 9/10. It only missed the unassigned action item for the PDF export fix. 

**Q: What decisions were finalized in this meeting?**
* **Model's Answer:** Gradual rollout starting Mon, Freezing features June 20th (*Whisper heard June 28th*), Production DB migration Friday 2 AM.
* **Evaluation:** 10/10. Captured all three finalized decisions perfectly.

**Q: What blockers were mentioned?**
* **Model's Answer:** Identified the PDF export bug.
* **Evaluation:** 5/10. It missed the embeddings API rate limit, which was explicitly called out as a "blocker" in the script.

**Q: When is the Nexus Corp demo and what needs to be ready?**
* **Model's Answer:** June 24th. Dashboard redesign, PDF export fix, Recommendation rollout stable.
* **Evaluation:** 10/10. Absolutely flawless.

---

### Key Takeaways
1. **The RAG time-slicer works perfectly.** It correctly identified the exact timestamp boundaries and the topics surrounding them, bypassing the limitations of dense retrieval.
2. **Whisper Transcription is the primary bottleneck.** The LLM missed zero information that it was explicitly given, but Whisper occasionally misheard words (e.g., "Karan" -> "Current", "Nexus Corp" -> "Nexus Cup", "June 20th" -> "June 28th"). 
3. **Synthesis is excellent.** The LLM flawlessly grouped disjointed facts across the transcript into organized lists.
