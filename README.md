
# ZIA — ZetoLabs Intelligent Assistant



<p align="center">
  <img src="assets/av.png" alt="ZIA Icon" width="150" style="border-radius:12px;" /><br/>
</p>

<p align="center">
   ZIA — Modular AI assistant framework with handlers for Slack, Discord, and Web. <br/>
   Built by <strong>Zachary Ford</strong>
</p>

---

## About this project

ZIA is a **proof‑of‑concept** experiment in building modular AI assistants.  
It connects Slack, Discord, and a simple web interface to local or external AI models.  

The goal isn’t a polished app yet — it’s a framework to show what’s possible:
- **Cross‑platform routing** between multiple chat platforms.  
- **Persona switching** for different conversation styles.  
- **Persistent memory** stored in JSON files per channel (no database setup required).  
- **Config‑driven setup** — all variables are kept in `.json` configs, so no code edits are needed.  

If there’s community interest, future directions could include:
- A GUI for easier setup.  
- Integrated AI hosting (instead of BYOAI).  
- More polished packaging and installers.  

---

## Project structure

```
ZIA/
├── README.md              # Intro + docs
├── assets/                # Icons + docs
├── gateway/               # Core API service
├── bots/                  # Platform integrations
│   ├── slack/
│   ├── discord/
│   └── web/
├── config/                # JSON configs
│   ├── app.json
│   ├── web.json
│   └── persona.json
├── memory/                # JSON memory per channel
├── secrets/               # .gitignored
├── runtime/               # .gitignored (logs, temp files)
└── .gitignore
```

---

## How to use

Because this is a proof‑of‑concept, setup is manual:

1. Clone the repo and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Add your tokens to `secrets/`.  
3. Run a handler directly, e.g.:
   ```bash
   python bots/discord/zia.py
   ```
4. Messages are logged into `memory/[channel ID].json`.  

👉 For a live demo, join our Discord and see ZIA in action:  
[💬 Discord](https://discord.gg/4RGzagyt7C)

---

## Known issues

- Slack replies were slower due to ngrok tunneling. **(FIXED with direct link!)**  
- Web handler is still experimental.  
- Docs loader (offline knowledge base) is planned but not yet implemented.  

---

## Roadmap

**Completed:**  
- Gateway API with persona templates  
- Discord + Slack handlers  
- Persistent JSON memory  

**Planned:**  
- Web handler improvements  
- Offline docs integration  
- GUI or launcher script (if interest grows)  
- Documentation polish (quickstart + diagrams)  

---

## Contributions welcome

This is open source — contributions are encouraged:
- **Fork & PR:** Bug fixes, features, refactors  
- **Issues:** Report bugs or suggest improvements  
- **Discord:** Join our community for feedback & collaboration  

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

---
