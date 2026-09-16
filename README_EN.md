# NEC · New Energy Coder Club

[![License](https://img.shields.io/badge/License-Mulan%20PSL%20v2-green)](LICENSE.md)
[![Website](https://img.shields.io/badge/Website-newenergycoder.club-orange?style=flat-square)](https://www.newenergycoder.club/)

> [中文版 README](./README.md)

## About NEC

NEC is an open-source engineering community focused on **RISC-V edge AI** (KPU/NPU inference × robotics × NearLink connectivity), built around the openEuler Embedded / RT-Thread ecosystems. We run a dual-track repository: competition assets (ROBOCON etc.) + long-term projects, supporting online collaboration and an offline lab at CZU A416.

## 🔧 RISC-V × AI Open-Source Practice

| Track | Core Asset | Status | Entry |
|---|---|---|---|
| 🐶 K230 Edge Inference | Wheel-legged robot dog on Canaan K230 (RISC-V dual-core C908 + KPU NPU), with a deployable kmodel image-classification pipeline (nncase 2.9.0) | ✅ Deployable; 📋 full open training pipeline planned as an OSPP topic | [Project](./projects/robotics/机器狗-k230/) · [Guide](./docs/learn/riscv-ai/k230-getting-started.md) |
| ⚡ NearLink × openEuler | HiSilicon WS63 (RISC-V core) NearLink SLE gamepad; OSPP 2024 participant | ✅ Samples + OSPP experience | [Project](./projects/星闪手柄/) · [Guide](./docs/learn/riscv-ai/ws63-nearlink-guide.md) |
| 👁️ CURC2026 Vision SIG | K230 / Raspberry Pi 5 / Jetson Nano vision platforms, inheriting the K230 deployment know-how | 📋 Planning | [Vision SIG](./competitions/CURC2026ROBOCON/视觉SIG/) |
| 🏆 OSPP Archive | AGL × openEuler Embedded adaptation (completed OSPP project) | ✅ Completed | [Report](./projects/research-horizontal/AGL-openEuler.md) · [OSPP Zone](./docs/ospp/) |

> 🌱 **Open Source Promotion Plan (OSPP)**: topic pool, mentors and student guide live in [docs/ospp/](./docs/ospp/). Our transformation roadmap: [RISC-V × AI OSPP Plan](./docs/ospp/RISCV_AI_OSPP_PLAN.md).

## 📁 Repository Layout

```
new_energy_coder_club/
├── 🏆 competitions/      # Competition-driven assets (ROBOCON, smart car, ...)
├── 🚀 projects/          # Project-driven work (robotics, NearLink, AI)
├── 📚 docs/              # Community core: onboarding, learning paths, governance
├── 🛠️ shared/            # Shared resources: 3D models (STEP), images
└── 🤝 CONTRIBUTING.md    # How to contribute
```

## 🧭 Start Here

- Quickstart: [60-minute onboarding](./docs/start-here/60min.md) · [First Good Issue](./docs/start-here/first-good-issue.md)
- Learning paths: [Role roadmaps](./docs/learn/roles.md) · [RISC-V × AI](./docs/learn/riscv-ai/)
- Indexes: [Competitions](./docs/indexes/competition_index.md) · [Projects](./docs/indexes/project_index.md)
- Community: [Maintainers/SIGs](./docs/community/maintainers.md) · [Governance](./docs/GOVERNANCE.md)

## 🤝 Contributing

1. Open or pick an Issue (`good first issue` / `help wanted` labels)
2. Branch from `master`, use Conventional Commits, open a Draft PR early
3. See [CONTRIBUTING.md](./CONTRIBUTING.md) and the [branch model](./docs/GOVERNANCE.md)

## License

Mulan Permissive Software License, Version 2 (Mulan PSL v2). See [LICENSE](./LICENSE.md).
Third-party components retain their original licenses — see project-level `NOTICE.md` files.
