# Memory Documentation & Architecture Repository

Welcome to the `docs/memory/` knowledge repository. This folder serves as persistent context and long-term memory for human maintainers and AI assistants working on this Home Assistant configuration.

---

## 🎯 Purpose
Rather than re-scanning dozens of package files, automations, or device registries on every task, agents and contributors should consult this directory first. It captures the **living state**, **contracts**, and **design rationale** of the smart home setup.

---

## 📂 Memory Taxonomy

| File | Purpose | When to Consult | When to Update |
| :--- | :--- | :--- | :--- |
| [`entities.md`](./entities.md) | Verified inventory of physical and logical entity IDs grouped by room and domain | Before writing any script, automation, or dashboard card (never guess IDs) | When adding, renaming, or retiring physical devices, integrations, or template helpers |
| [`subsystems.md`](./subsystems.md) | Behavioral contracts for core house functions (Presence, Audio/TTS, Gemini AI Briefings, Anti-Blinding, Climate, etc.) | Before modifying automations that interact with sound, lights, heating, presence, or AI voice | When changing global rules or adding a new cross-room subsystem |
| [`architecture.md`](./architecture.md) | Architectural Decision Records (ADRs) and design patterns explaining *why* decisions were made | When questioning a pattern, considering a refactor, or adding architectural components | When making significant structural or architectural changes |

---

## 📌 Rules for AI Agents & Developers
1. **Source of Truth**: Treat `subsystems.md` and `architecture.md` as non-negotiable architectural contracts (e.g., always route TTS through `script.play_media_tts_message`, always query Gemini via `script.play_media_tts_gemini`, always apply low brightness before turning off ambient lights).
2. **Entity Accuracy**: Always look up entity IDs in `entities.md`. If an entity does not exist or changes, update `entities.md` immediately.
3. **Keep it Concise & High-Level**: Do not dump raw YAML files or micro-automation triggers here. Memory files should capture patterns, rationale, and indexes that remain valid across minor edits.
