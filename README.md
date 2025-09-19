<div align="center">
   
# HeX Peeker 🔍  
*A sleek Python app to peek into binary and hexadecimal data with a modern, intuitive GUI.*  
**Built for developers, reverse engineers, and curious minds.**

> ✨ **v3.3 Beta** — Data Export ready • Under active development • MIT Licensed

[![Version](https://img.shields.io/badge/Version-v3.3%20Beta-yellow)](https://github.com/nadhilm12/HeX_Peeker/releases)

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-v6.9.1-orange)](https://www.riverbankcomputing.com/software/pyqt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Contributions Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/nadhilm12/HeX_Peeker/issues)

</div>
---

## 🚀 Why HeX Peeker?

HeX Peeker is your go-to tool for inspecting binary and hex data with ease. Whether you're debugging binaries, exploring files, or just satisfying curiosity — this app delivers a **fast analyze experience, clean, easy to use, and modular experience**.

### ✨ Features

- 📄=📄 **2 Document Comparison** — Compare 2 Document with Higlight marking, to see the difference.
- 🔍 **Visual Hex Analysis** — Dive into binary files with a powerful, interactive hex viewer.
- 🎨 **Modern GUI** — Smooth, responsive interface with **light/dark themes** using PyQt6 (v6.9.1), drag-drop coming soon!.
- 🧩 **Clean Codebase** — Modular architecture for easy maintenance and extension.
- ⚡ **Performance** — Optimized to handle large binary files without breaking a sweat.
- 🧪 **Tested** — Comprehensive unit tests with `pytest` for reliability.
- 📦 **Ready to Run** — Simple setup with `requirements.txt`.

---

## 🖼️ Sneak Peek

> *Click to enlarge*

| Light Mode | Dark Mode | Compare Mode (Beta) |
|------------|-----------|---------------------|
| ![Light Mode](assets/Mode_Light.PNG) | ![Dark Mode](assets/Mode_Dark.PNG) | ![Compare Mode](assets/Mode_Analyzing.PNG)|

> 💡 **Compare Mode**: Load two files to view byte-level differences side-by-side. Export diffs as text or CSV. *(Drag-drop support coming soon!)*

---

## 🚀 Get Started

### ✅ Prerequisites

- Python 3.8 or higher (cross-platform)
- PyQt6==6.9.1
- Tested on **Windows 10** — *should work on macOS/Linux; please report issues!*

---

### 📥 Installation

1. **Clone the repo:**
   ```bash
   git clone https://github.com/nadhilm12/HeX_Peeker.git
   cd HeX_Peeker
   ```

2. **Set up a virtual environment (recommended):**

   ```bash
   # Create venv
   python -m venv venv

   # Activate (Windows)
   venv\Scripts\activate

   # Activate (macOS/Linux)
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🛠️ Run It

Launch the app:
```bash
python main.pyw
```

> 💡 **Pro Tip**: Double-click `main.pyw` on Windows for quick launch!

---

## 🔥 How to Use

- **📂 Load a File** → `File → Open` → Pick any binary file (`.bin`, `.exe`, `.dll`, etc.).
- **🔍 Search Patterns** → Hit `Ctrl+F` to find hex or text patterns in the data.
- **📋 Explore** → Right-click in the hex viewer for options like copying hex values or byte offsets.
- **🌙 Switch Themes** → Toggle between light and dark mode for comfy viewing.
- **⚖️ Compare Files** → Load two files → View differences → Export Diff (text/CSV).
- **📤 Export Data** → Save hex/ASCII views or comparison diffs to file.

> 🐞 **Hit a snag?** Check `utils/logs/` — logs got your back!

---

## 🧪 Testing

Run the test suite to ensure everything's rock-solid:
```bash
pytest tests/ -v
```

Want a coverage report? Try:
```bash
pytest tests/ --cov=. --cov-report=term-missing
```

> ✅ Make sure `pytest-cov` is installed — included in `requirements.txt`.

---

## 📂 Project Structure

```
HeX_Peeker/
├── assets/         # Screenshots, icons, and visual assets
├── core/           # Hex parsing, file loading, diff engine
├── helpers/        # Utility functions (search, export, etc.)
├── ui/             # GUI components (MainWindow, HexView, ThemeManager)
├── utils/          # Config, logging, exporters
├── tests/          # Unit and integration tests
├── main.pyw        # App entry point (double-clickable!)
├── requirements.txt # Dependencies
└── README.md       # You're reading it!
```

---

## 🤝 Contribute

We ❤️ contributors! Whether you’re fixing bugs, improving dark mode contrast, or adding drag-drop file loading — your help matters.

### 🌟 Good First Issues
- Add **drag-and-drop file loading** to main window
- Improve **dark mode contrast** for accessibility
- Add **new export formats** (JSON, HTML, etc.)
- Write **more unit tests** for edge cases

> 💬 Open an [Issue](https://github.com/nadhilm12/HeX_Peeker_/issues) or submit a PR — we’ll buy you a coffee ☕ (figuratively... for now).

---

## ⭐ Show Some Love

If HeX Peeker helps you out — **drop a ⭐ on GitHub!**  
It keeps the project alive and motivates us to keep building cool stuff.

---

## 📜 License

HeX Peeker is licensed under the **MIT License** — feel free to use, modify, and share!

<div align="center">
<details>
<summary>📜 MIT License (click to expand)</summary>

Copyright (c) 2025 Nadhilm12

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

</details>
</div>
---

> **Built with 💻 and ☕ — by curious minds, for curious minds.**  
> *HeX Peeker — because sometimes, you just need to peek under the hood.*
```

---
