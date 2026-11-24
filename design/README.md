# design

The documents behind the rules: why they are the way they are, what's still open, and how design work is done. The rules themselves are in `rules/`. Frozen records that no longer need to sync to the claude.ai project are in `archive/`.

| File | What it is | Live or frozen |
|---|---|---|
| `Design_Notes_for_Design_Bible.md` | The designer's stated or endorsed principles, with sources: the raw material for a design bible. The pillars in §2 are drafts the designer hasn't adopted. | **Live.** Principles only; the pillars are to be settled here. |
| `Fix_Order_and_Dependencies.md` | What each of the v0.9 review's findings (F1–F14) depends on and ripples to, the original fix order, a section per packet since 0.11.0, and an index of the findings with where each stands now (section 10). | **Live.** A new section with each packet. |
| `Rules_Reconciliation_Ledger_v0.8-to-v0.9.md` | Where each v0.9 rule came from and how firm it is. Engine code cites its IDs (MV-3, CB-2…). | **Mixed.** Parts A–D (the v0.9 entries) and G (the designer's verbatim rulings) are frozen at v0.9, apart from "Later changes" lines. Part H (shelved ideas) is live; the rules note Not in This Version is the current list. |
| `Instructions_for_Design_Chats.md` | How any assistant helping with design should work. The claude.ai project carries a copy as its instructions. | **Live.** The master copy. |

The v0.9 review is archived at `archive/design/Review_Playtest_Packet_v0.9.md`. Section 10 of the fix-order doc keeps what's still useful from it.
