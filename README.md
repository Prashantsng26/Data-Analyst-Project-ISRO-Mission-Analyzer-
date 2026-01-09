# 🚀 ISRO Mission Analyzer

## 📖 Overview

**ISRO Mission Analyzer** is a data-driven web application designed to analyze the historical missions of the Indian Space Research Organisation (ISRO). It features an interactive dashboard to visualize mission trends and uses a Random Forest classifier for **exploratory success probability estimation** based on historical launch parameters.

## 📊 Data Source

The mission data is sourced from the **[ISRO Space Missions 1963-2025 Dataset on Kaggle](https://www.kaggle.com/datasets/prashantsng26/isro-space-missions-1963-2025)**, provided as an SQL dump (`isro-missions.sql`).

## ✨ Features

- **📊 Historical Data Analysis**: Explore mission trends, analyzing success rates across different vehicle families and decades.
- **🚀 Space-Themed UI**: Immersive dark-mode design for an enhanced analytics experience.
- **📈 Enhanced Visualizations**: Integrated Plotly charts showing vehicle capabilities and orbital distributions.
- **🤖 Exploratory ML Modeling**:
  - Trained a Random Forest Classifier to estimate success probability.
  - **Performance**: ~92.6% Accuracy, ~96.1% F1-Score.
  - *Note: Metrics are influenced by class imbalance (93% historical success rate). ROC-AUC is de-emphasized in favor of precision-recall transparency.*
- **Top Influential Features**: Visualizes tree-based feature importance for launch vehicle and orbit configurations.
- **🔌 RESTful API**: FastAPI backend serving analysis data and ML estimates.

## ⚠️ Model Limitations & Transparency

- **Class Imbalance**: The historical data is heavily skewed towards successful missions (~93%). This naturally inflates accuracy and recall.
- **Scope**: The model is intended for **exploratory analysis** and as a demonstration of a data science pipeline; it is not for operational mission forecasting.
- **Parameters**: External variables like weather, real-time sensor data, and payload complexities are not captured in this historical dataset.

## 🛠️ Tech Stack

### Frontend
- **Streamlit**: For building the interactive web dashboard.
- **Plotly**: For creating rich, interactive data visualizations.

### Backend
- **FastAPI**: High-performance API for data serving and model inference.
- **Pandas**: For data manipulation and feature engineering.
- **scikit-learn**: For the machine learning pipeline (Random Forest).
- **SQLite**: Lightweight storage for mission data.

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- Pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Prashantsng26/Data-Analyst-Project-ISRO-Mission-Analyzer-.git
   cd Data-Analyst-Project-ISRO-Mission-Analyzer-
   ```

2. **Set up a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## ☁️ Deployment

The application is optimized for **self-contained deployment** on [Streamlit Cloud](https://streamlit.io/cloud).

1. Push your code to GitHub.
2. Connect your repository to Streamlit Cloud.
3. Select `app.py` as the main file.

## 🏃‍♂️ How to Run

### Method 1: VS Code (Recommended)
1. Open the **Run and Debug** view.
2. Select **"Run Full Stack App"**.
3. Click the green Play button.

### Method 2: Manual Terminal Commands
Run the Streamlit app directly (includes integrated backend logic):
```bash
streamlit run app.py
```

## 📂 Project Structure

```
├── backend/                # Backend logic (FastAPI, Model, Data)
├── data/                   # Data files (SQL dumps)
├── app.py                  # Streamlit Dashboard (Entry point)
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

---
Made with ❤️ by [Prashant Singh](https://github.com/Prashantsng26)
