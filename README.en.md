# Writing Telegram Bots with aiogram 3.x

**README languages:** [RU](README.md) · [EN](README.en.md) · [UK](README.uk.md) · [ZH](README.zh.md)

This is a book on developing Telegram bots in Python using the **[aiogram 3.x](https://github.com/aiogram/aiogram/tree/dev-3.x)** framework (current example baseline: **3.27.0+**).

You can find the book here: https://mastergroosha.github.io/aiogram-3-guide/  
The source texts for all chapters are located [in the code folder](https://github.com/MasterGroosha/aiogram-3-guide/tree/master/code).

Previous versions:
* aiogram 2.x (2019-2021): https://mastergroosha.github.io/aiogram-2-guide/
* pyTelegramBotAPI (2015-2019): https://mastergroosha.github.io/telegram-tutorial/

---
Available interface/translation languages: **RU**, **EN**, **UK**, **ZH** (Chinese is currently being expanded).
---
### Translated by [VAI || Programmer](https://github.com/Vadim-Khristenko)
**The book's translation is not supported by the author personally**, but by the Translator (mentioned above), if the translation lags behind the original, you may directly complain to [VAI || Programmer](https://github.com/Vadim-Khristenko).
You can also write to the Translator's [Telegram DM](https://t.me/VAI_Programmer).

The book is built using [mkdocs-material](https://squidfunk.github.io/mkdocs-material/).

For local dependency setup, both `pip` and `uv` are supported.

### Quick start (pip)

```bash
python -m pip install -r requirements.txt
mkdocs build --strict
```

### Quick start (uv)

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
mkdocs build --strict
```
