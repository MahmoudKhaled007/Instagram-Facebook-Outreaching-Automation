# 📣 Instagram & Facebook Outreaching Automation

An end-to-end RPA solution for automating personalized outreach via Instagram and Facebook using AI (online and offline models), Chrome automation, and Excel-configured workflows. Ideal for freelancers, agencies, and outreach teams targeting users via social media with hyper-personalized DMs and comments.

---

## 🔧 Features

- ✅ Input profile list via Excel
- ✅ Excel config for model prompts, action settings & limits
- ✅ GUI to select platform (Facebook/Instagram), action (Message/Comment/Both), and model type (Online/Offline)
- ✅ Auto screenshots via Chrome extension (`Screenshot & Screen Recorder`)
- ✅ AI-generated personalized DMs/comments via:
  - 🌐 **Online Mode** using OpenRouter APIs + [imgbb.com](https://imgbb.com) (image hosting)
  - 💻 **Offline Mode** using local Ollama models (LLM+Vision)
- ✅ Auto-check if a user is available (Follow + Message + Posts present)
- ✅ Auto-like post before commenting
- ✅ Auto-check DM history before messaging
- ✅ Switch Chrome profiles when hitting message limits
- ✅ Rotate through multiple API keys
- ✅ Logs + error screenshots saved
- 🔄 On-going dev: Proxy rotation, error recovery enhancements

---

## 🧠 Model Support

### Online Mode
- Upload screenshot to [imgbb.com](https://imgbb.com)
- Call model via [OpenRouter API](https://openrouter.ai/)
- Rotate API keys if limits are hit

### Offline Mode
- Requires [Ollama](https://ollama.com/) installed locally
- Base64 encode image, send to local endpoint
- Model name must match the one listed in config Excel

---

## 🧪 How It Works (Flow)

1. User selects actions (DM/Comment/Both), platform (IG/FB), model mode (Online/Offline)
2. Profile is read from Excel
3. Screenshot of profile is taken
4. User availability is checked
5. If available:
    - Analyze image
    - Generate personalized DM/comment using LLM
    - Check past messages (if applicable)
    - Interact (comment/DM)
6. All actions are logged
7. Message/API/Chrome limits trigger circular rotation
8. Errors are logged with screenshots

---

## 🧰 Requirements

- Python 3.10+
- [Ollama](https://ollama.com/) (for offline mode)
- Chrome browser
- Screenshot & Screen Recorder Extension
- Excel
- Free or Paid [OpenRouter API key(s)](https://openrouter.ai/settings/keys)

---

## 🔁 Rotation Logic

- 🌐 **API Keys**: Rotate across keys if free limits are hit
- 👤 **Chrome Profiles**: Switch Chrome user if message limit exceeded
- ♻️ **Circular Rotation**: Once all APIs/Chrome profiles are exhausted, start over

---

## 🚀 Getting Started

1. Clone this repo
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Setup your config Excel with:
  - Prompts
  - Limits
  - Model names (OpenRouter/Ollama)

4. Set Shortcut to Activate **CTRL + Y** Chrome Extention [Screenshot & Screen Recorder Tool](https://chromewebstore.google.com/detail/ijejnggjjphlenbhmjhhgcdpehhacaal?utm_source=item-share-cb)
5. Run The workflow from Main

---

## 🛡️ Error Handling

- If any error occurs (missing element, failed API, screenshot issue), it will:
  - Take a screenshot of the error
  - Log it to the output Excel with error details
  - Skip the profile safely

---

## 📌 TODO / In Progress
- 🔄 Proxy rotation support
- ⛔ Smarter pause/resume if rate-limited
- 📦 Turn into a packaged installer

---

## 🤝 Contributing

Want to improve the automation or UI? PRs are welcome. Create an issue or pull request.

## 📜 License
This project is licensed under the **Apache 2.0 License**. See [LICENSE](LICENSE) for details.

## 📧 Contact

For freelance projects or RPA consulting:  
**Mahmoud Khaled**  
Freelance UiPath | Power Automate | Python  
Email: **Mahmoud.khkamal@gmail.com**
