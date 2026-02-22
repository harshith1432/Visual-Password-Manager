# 🔐 SecureVault: Visual Password Manager

**SecureVault** is a next-generation, high-security password management system that replaces traditional master passwords with an innovative **Visual Image Verification** system. Designed with a stunning **Glassmorphism UI**, it offers advanced features like **Plausible Deniability (Shadow Vaults)** and **Context-Aware Decoys**.

![Preview](https://img.shields.io/badge/UI-Glassmorphism-blueviolet)
![Security](https://img.shields.io/badge/Security-AES--Encryption-green)
![Python](https://img.shields.io/badge/Backend-Flask-lightgrey)

---

## ✨ Key Features

### 🖼️ Visual Identity Verification
Instead of a master password, SecureVault uses a secret image. When you want to reveal a password, you must identify your secret image among a **shuffled 20-image grid**.

### 🌑 Dynamic Shadow Vaults (Plausible Deniability)
Entering an incorrect PIN doesn't just block you; it **secretly creates a completely functional, empty vault**. This allows you to maintain "plausible deniability" by showing decoys if forced to unlock your vault.

### 🎭 Category-Based Decoys
Security through blending. If your secret image is a 'Pet', SecureVault automatically populates the 20-image grid with other animals from the same category, making your secret key perfectly camouflaged.

### 💎 Premium Glassmorphism UI
- **Translucent Design**: High-end aesthetics with modal blurs and glass effects.
- **Micro-animations**: Liquid transitions and state-aware hover effects.
- **Dual Themes**: Full support for a deep indigo Dark Mode and a crisp Light Mode.

### 🛡️ Smart Security Suite
- **AES-256 Encryption**: Every platform password is encrypted before hitting the database.
- **Brute Force Protection**: 3 failed image attempts will lock the platform for 24 hours.
- **Security Alerts**: Real-time browser notifications and in-app alerts for lockouts.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL (or Neon for serverless PG)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-link>
   cd "Visual Password Manager"
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=your_postgresql_connection_string
   SECRET_KEY=your_flask_secret_key
   ENCRYPTION_KEY=your_fernet_encryption_key
   ```

4. **Initialize Database**:
   ```bash
   python fix_db.py
   ```

5. **Run the Application**:
   ```bash
   python app.py
   ```
   Open `http://127.0.0.1:5000` in your browser.

---

## 📂 Project Structure

```text
├── app.py              # Main Flask application & routes
├── models.py           # SQLAlchemy database models
├── utils.py            # Encryption/Decryption & Image logic
├── static/
│   ├── css/style.css   # Premium design system
│   ├── js/main.js      # Theme & Notification logic
│   ├── decoys/         # Categorized decoy images
│   └── uploads/        # User-uploaded secret images
└── templates/          # Modern HTML5 templates
```

---

## 🤝 Contributing
Contributions are welcome! If you have suggestions for new security categories or UI improvements, please feel free to fork and submit a PR.

---
*Built with ❤️ for Privacy and Aesthetic Excellence.*
