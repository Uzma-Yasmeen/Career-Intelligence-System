# AI Career Intelligence System 🚀

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0-red.svg)](https://streamlit.io/)
[![XGBoost](https://img.shields.io/badge/XGBoost-1.7.6-orange.svg)](https://xgboost.ai/)
[![Gemini](https://img.shields.io/badge/Google-Gemini_2.0-green.svg)](https://aistudio.google.com/)

An explainable, data-driven framework for software engineering career progression. This project leverages the Stack Overflow Developer Survey data to provide localized salary benchmarks, role forecasting, and personalized upskilling roadmaps using Gradient Boosting and Generative AI.

---

## 🌟 Key Features

- **Multi-Modal Profile Analysis:** Integrates manual input, Resume PDF parsing (`pdfplumber`), and GitHub portfolio mining (`PyGithub`).
- **Predictive Role Forecasting:** Uses a Balanced Random Forest Classifier to identify the user's next career trajectory.
- **Localized Salary Benchmarking:** Calibrated XGBoost Regressor providing market-specific compensation data for 50+ countries.
- **Explainable AI (XAI):** Integrated **SHAP** (SHapley Additive exPlanations) to clarify which skills drive your market value.
- **AI Career Narratives:** Personalized career summaries and 90-day roadmaps generated via the **Google Gemini API**.
- **Interactive Dashboard:** A multi-page Streamlit application for a seamless user experience.

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Machine Learning:** Scikit-learn, XGBoost, SHAP
- **LLM Integration:** Google Gemini API (`google-genai`)
- **Data Processing:** Pandas, NumPy
- **Storage/Auth:** Firebase (Firestore & Auth)
- **Reporting:** fpdf2 (PDF Generation)

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/Uzma-Yasmeen/Career-Intelligence-System.git
cd Career-Intelligence-System
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Secrets
Create a `.streamlit/secrets.toml` file and add your credentials:
```toml
# .streamlit/secrets.toml
GEMINI_API_KEY = "your_gemini_api_key"

# Firebase Config (Optional)
FIREBASE_TYPE = "service_account"
FIREBASE_PROJECT_ID = "..."
...
```

### 4. Run the Application
```bash
streamlit run app/main.py
```

---

## 📊 Methodology & Research

For detailed info on the machine learning models and research methodology used in this project, please refer to the conference paper documentation.

### Model Training
The models were trained on 60,000+ responses from the Stack Overflow Developer Survey, using advanced feature engineering:
- **Skill Interaction Signals:** `devops_signal`, `ml_signal`, etc.
- **Localized Market Calibration:** Custom post-inference ratio system to mitigate US-centric bias.

---

## 👥 Contributors

- **Uzma Yasmeen** - Lead Developer & Researcher

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

