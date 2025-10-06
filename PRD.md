# 🧠 PRD: Agentic Game Playtester AI

**Product Name (Working Title):** *PlaytestAI*
**Version:** Draft v0.1
**Author:** [Your Name]
**Date:** October 2025

---

## 1. Overview

### 1.1 Purpose

PlaytestAI automates game testing using intelligent agents that can *play*, *observe*, and *analyze* games in real time — identifying bugs, glitches, performance issues, and gameplay inconsistencies.
Each agent embodies a distinct *playstyle* (e.g., "speedrunner," "explorer," "chaotic bug-hunter") to explore different aspects of a game's behavior and surface edge cases that human testers or scripted bots may miss.

### 1.2 Vision

> "Build an army of AI playtesters that can play any game, find bugs, and explain what went wrong."

PlaytestAI will drastically reduce manual QA overhead and increase test coverage across complex, emergent gameplay systems — paving the way for AI-assisted continuous playtesting during game development.

---

## 2. Goals & Non-Goals

### ✅ Goals

* Create autonomous agents capable of playing binary-only games (no source or debug hooks needed).
* Detect and log crashes, visual anomalies, performance drops, or softlocks.
* Generate reproducible replay sequences that developers can review and rerun.
* Support multiple "playstyles" to test games in diverse ways.
* Provide modular, scalable architecture for future ML/LLM enhancements.

### 🚫 Non-Goals (v0 Prototype)

* Not focused on multiplayer or online games (risk of anti-cheat interference).
* Not a replacement for full QA — focuses on *automation & discovery*, not subjective feedback.
* No game engine integration (e.g., Unity Editor hooks) — initial target is black-box desktop binaries.

---

## 3. User Stories

| Role          | Story                                                                                        |
| ------------- | -------------------------------------------------------------------------------------------- |
| QA Lead       | "I want to run PlaytestAI overnight to explore my level and log any visual bugs or crashes." |
| Developer     | "I want reproducible sequences that cause crashes, so I can fix them quickly."               |
| PM / Producer | "I want analytics about how stable our build is across different agents and versions."       |
| Researcher    | "I want to study how different AI agents explore a game differently."                        |

---

## 4. Key Features

### 4.1 Automated Game Interaction

* Detect and focus on target game window.
* Inject keyboard and mouse input (via `pydirectinput`, `SendInput`, or OS APIs).
* Capture screen region at 10–30 FPS using `mss` or GPU-based capture.
* Work on binary-only builds (no code access).

### 4.2 Visual & State Perception

* Real-time frame capture and analysis.
* Visual anomaly detection using SSIM, perceptual hash, and/or template matching.
* Optional OCR for HUD/score/lives.
* Optional object detection for dynamic entities (YOLOv8 lightweight model).

### 4.3 Bug & Anomaly Detection

* **Crash detection:** game process termination, OS crash dialogs.
* **Visual regression:** unexpected UI/state changes.
* **Softlock detection:** same frame or position for >N seconds.
* **Performance drop detection:** CPU/memory usage spikes or FPS drop.

### 4.4 Reproducible Replays

* Record all actions with timestamps and optional screenshots.
* Auto-generate replay artifacts: `replay.json`, video (`ffmpeg`), and logs.
* Implement delta-debugging to minimize action sequences reproducing bugs.
* Export shareable bug bundles (zip or web dashboard).

### 4.5 Multi-Agent Playstyles

* **Random Agent:** baseline random actions.
* **Explorer:** moves toward unexplored regions.
* **Glitch-Seeker:** spams inputs or boundary exploits.
* **LLM-Driven Agent:** chooses actions based on visible game state and textual reasoning.

### 4.6 Logging & Reporting

* Structured JSON logs per run (action sequence, screenshots, detected issues).
* Aggregated summary dashboard (per-game stability metrics).
* CLI or web interface for browsing test sessions.

---

## 5. System Architecture

### 5.1 Components

| Component                  | Description                                                        |
| -------------------------- | ------------------------------------------------------------------ |
| **Controller**             | Manages agent lifecycle, game launch, and result aggregation.      |
| **Agent Core**             | Executes actions, observes frames, and makes decisions.            |
| **Input Injector**         | Handles keyboard/mouse events via OS API.                          |
| **Frame Grabber**          | Captures game visuals using `mss` (fast screen capture).           |
| **Analyzer**               | Compares frames, detects anomalies, runs OCR/object detection.     |
| **Logger**                 | Saves actions, screenshots, and performance data.                  |
| **Replay Engine**          | Replays recorded sequences for bug reproduction.                   |
| **LLM Adapter (optional)** | Interfaces with OpenAI API or local LLM for reasoning-driven play. |

### 5.2 Architecture Diagram (textual)

```
        +---------------------------+
        |     Controller / CLI      |
        +-----------+---------------+
                    |
                    v
        +-----------+-----------+
        |     Agent Core        |
        |-----------------------|
        |  - Perception         |
        |  - Decision Loop      |
        |  - Action Execution   |
        +-----------+-----------+
                    |
    +---------------+----------------+
    |               |                |
    v               v                v
Input Injector   Frame Grabber     Analyzer
  (pyautogui)      (mss)          (OpenCV, OCR)
    |                                   |
    +---------------+-------------------+
                    |
                    v
                Logger / Replay
                    |
                    v
             Issue Reporter / LLM
```

---

## 6. Technical Requirements

### 6.1 Platform

* **OS:** Windows (initially), later Linux support.
* **Languages:** Python 3.10+ (prototype), optional Rust/C++ modules later.
* **Dependencies:**

  * `mss`, `opencv-python`, `pydirectinput`, `pynput`, `psutil`, `pytesseract`, `scikit-image`, `imagehash`, `ffmpeg`.

### 6.2 Performance Targets

* Min 10 FPS capture rate.
* <100 ms input latency.
* Able to run 2–4 concurrent agents on midrange PC.

### 6.3 Data Outputs

* `repro/` folder structure per test.
* Logs in JSON and CSV for analysis.
* Optional local web dashboard (FastAPI + React).

### 6.4 Extensibility

* Modular agent API: easily plug in new decision logic.
* Optional GPU acceleration for frame analysis.
* Future: integrate reinforcement learning policies.

---

## 7. MVP Scope (Milestone 1)

**Goal:** Working single-agent prototype for one simple game (e.g., *Celeste*, *Hollow Knight*, or a local indie build).

**Includes:**

* Game window capture + input injection.
* Random-agent play loop.
* Frame differencing (SSIM) anomaly detection.
* Crash/termination logging.
* Replay recording and export.

**Excludes:**

* LLM-driven reasoning.
* Multi-agent scaling.
* GUI dashboard (CLI-only).

---

## 8. Future Enhancements

| Phase   | Feature                      | Description                                     |
| ------- | ---------------------------- | ----------------------------------------------- |
| Phase 2 | LLM-driven playstyles        | Use GPT or local models for strategy decisions. |
| Phase 3 | Web dashboard                | Visualize sessions, heatmaps, and bug clusters. |
| Phase 4 | Multi-instance orchestration | Distributed runs across machines or VMs.        |
| Phase 5 | Reinforcement learning       | Train policies for automated exploration.       |
| Phase 6 | Integration with CI/CD       | Auto-run PlaytestAI on new builds.              |

---

## 9. Risks & Mitigations

| Risk                              | Impact    | Mitigation                                      |
| --------------------------------- | --------- | ----------------------------------------------- |
| Anti-cheat systems blocking input | High      | Restrict to offline/local builds.               |
| False positives in visual diff    | Medium    | Mask dynamic HUD elements, tune SSIM threshold. |
| High CPU/GPU load during capture  | Medium    | Lower FPS, use mss partial capture regions.     |
| LLM latency too high              | Low (MVP) | Use local caching or async batching.            |
| Game crashes PC                   | Low       | Isolate process, use watchdog.                  |

---

## 10. Success Metrics

| Metric                             | Target                           |
| ---------------------------------- | -------------------------------- |
| Visual anomaly detection precision | ≥80% on test suite               |
| Repro replay success rate          | ≥90%                             |
| Agent stability (no hangs)         | 1000+ steps continuous           |
| Developer feedback                 | Positive in first internal tests |
| Average CPU usage per agent        | <35% on test PC                  |

---

## 11. Example Workflow

1. Developer runs:

   ```bash
   python playtest.py --window "Celeste" --agent random --steps 1000
   ```
2. PlaytestAI locates the window, injects inputs, and captures frames.
3. Detects a visual anomaly → saves replay JSON + video.
4. Developer replays issue:

   ```bash
   python replay.py --repro repro_2025-10-06T1420/
   ```
5. The bug reproduces exactly → dev fixes it.

---

## 12. Deliverables (for prototype)

* `/src/playtest_ai/` Python package
* CLI tools: `playtest.py`, `replay.py`, `analyze.py`
* `requirements.txt`
* Sample config and baseline image set
* README with setup guide and demo instructions

---

Would you like me to write the **next step version of this PRD** — e.g. a **technical spec (design doc)** that maps this PRD into specific modules/classes/files (so it's implementable immediately)?
That would be the next logical step before coding.
