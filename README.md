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

I know it’s still early — but I’m sharing it here because:  
- **Build in public:** I want to keep learning by shipping real changes and showing the process.  
- **Collaborate:** Community input makes projects stronger, especially when designing for scalability and developer empathy.  
- **Career growth:** I’m actively building my portfolio, and showing progress helps me grow my craft and credibility.  

If you think ZIA is interesting, please follow along or contribute — every bit of feedback helps shape it into something better.

---

## Project structure

```
ZIA/
├── README.md              # Intro + docs link
├── assets/                # Icons + docs
│   └── docs/
├── gateway/               # Core API service
├── handlers/              # Platform integrations
│   ├── slack/
│   ├── discord/
│   └── web/
├── config/                # JSON configs
│   ├── app.json
│   ├── routes.json
│   └── persona.json
├── memory/                # Shared SQLite memory manager
├── secrets/               # .gitignored
├── runtime/               # .gitignored (logs, db, temp files)
└── .gitignore
```

---

## Key Features

- **Cross‑platform assistant** – one brain, multiple voices (Slack, Discord, Web).  
- **Modular gateway** – clean API design that makes adding new platforms or models simple.  
- **Persona control** – switch between Balanced, Playful, or Professional styles instantly.  
- **Persistent memory** – SQLite master chat record, filterable by platform + channel.  
- **Secure setup** – `.env` + JSON config with secrets safely ignored in Git.  

---

## How to use

Setup is still evolving, but here’s the current workflow:

1. Clone the repo and install dependencies (`pip install -r requirements.txt`).  
2. Add your tokens to `secrets/.env`.  
3. Run a handler directly, e.g.:  
   ```bash
   python handlers/discord/bot.py
   ```  
4. Messages will be logged into `runtime/chat.db`.

More detailed quickstart docs are coming soon.

---

## Known issues

- Slack replies are slower due to ngrok tunneling.  
- Web handler not yet implemented.  
- Docs loader (offline knowledge base) is still planned.  

---

## Roadmap

**Completed:**  
- Gateway API with persona templates  
- Discord + Slack handlers  
- SQLite persistent memory  

**Planned:**  
- Web handler  
- Offline docs integration  
- Launcher script (`zia.py`) to start all enabled handlers  
- Documentation polish (quickstart + architecture diagram)  

---

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
- [**Find this project on GitHub**](https://github.com/ZFordDev/ZIA)  
- [**Connect on Facebook**](https://www.facebook.com/zachary.ford.944654)

---

## ❤️ Support

ZIA is free and open source. If it helps you, consider supporting the creator via ZetoLabs:  
- [**Ko‑Fi**](https://ko-fi.com/zetolabs)