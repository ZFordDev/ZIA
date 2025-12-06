<h1 align="center">
  <img src="assets/av.png" alt="ZIA Icon" width="150" style="border-radius:12px;" /><br/>
</h1>

<p align="center">
   ZIA — Modular AI assistant framework with handlers for Slack, Discord, and Web. <br/>
  Built by <strong>Zachary Ford</strong>
</p>

---

## About this project

Hi! I’m a self‑taught developer, and ZIA is my next big experiment.  
It started as a proof‑of‑concept to connect Slack, Discord, and a simple web window to a local AI model. What began as a way to learn event handling and API integration has grown into something I think could become a genuinely useful framework: a modular assistant that can scale across platforms and evolve into its own ecosystem.

I know it’s still early — right now it’s just handlers and scaffolding — but I’m sharing it here because:  
- **Build in public:** I want to keep learning by shipping real changes and showing the process.  
- **Collaborate:** I believe community input makes projects stronger, especially when designing for scalability and developer empathy.  
- **Career growth:** I’m actively building my portfolio, and showing progress helps me grow my craft and credibility.  

If you think ZIA is interesting, please follow along or contribute — every bit of feedback helps shape it into something better.

---

## Project structure

```
ZIA/
├── README.md              # Short intro + link to docs
├── assets/
│   └── docs/
├── gateway/               # Core API service
├── handlers/
│   ├── slack/
│   ├── discord/
│   └── web/
├── config/
│   ├── app.json
│   ├── routes.json
│   └── persona.json
├── secrets/               # .gitignored
├── runtime/               # .gitignored (logs, db, temp files)
└── .gitignore
```

---

## Key Features

- **Cross‑platform assistant** – one brain, multiple voices (Slack, Discord, Web).  
- **Modular gateway** – clean API design that makes adding new platforms or models simple.  
- **Persona control** – switch between Balanced, Playful, or Professional styles instantly.  
- **Lightweight memory** – remembers recent context without bloating prompts.  
- **Secure setup** – `.env` + JSON config with secrets safely ignored in Git.  

---

## How to use

nothing here yet, were working on it!

---

## Known issues 

- Currently in early development — handlers and gateway scaffolding are in progress.

---

## Roadmap

- **Gateway API** – single `/chat` endpoint to unify all platforms (planned)  
- **Cross‑platform handlers** – Slack, Discord, and Web integrations (planned)  
- **Persona templates** – Balanced, Playful, and Professional styles (planned)  
- **Conversation memory** – sliding window with lightweight summarization (planned)  
- **Secure config** – `.env` + JSON setup with secrets safely ignored in Git (planned)  
- **Documentation** – polished quickstart guide and architecture diagram (planned)  

👉 For the full architectural blueprint and detailed phases, see [assets/docs/project-ZIA.md](assets/docs/project-ZIA.md).


## Contributions welcome

This is open source, and I’d be thrilled if you contribute:
- **Fork & PR:** Bug fixes, features, refactors
- **Issues:** Report bugs or suggest improvements
- **Discord:** Join our community for feedback & collaboration

- [💬 Discord](https://discord.gg/4RGzagyt7C)

---

## License

MIT License — free to use, modify, and distribute. Please keep this notice.

---

## 🫂 Stay Connected

- [**Join me on Discord**](https://discord.gg/4RGzagyt7C)
- [**find this project on GitHub**](https://github.com/ZFordDev/ZIA)
- [**Connect on Facebook**](https://www.facebook.com/zachary.ford.944654)

---

## ❤️ Support

ZIA is free and open source. If it helps you, consider supporting the creator via ZetoLabs:
- [**Ko‑Fi**](https://ko-fi.com/zetolabs)

---