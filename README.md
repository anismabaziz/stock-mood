# Reddit Stock Sentiment Analyzer 🧠📈

This is a full-stack web application that performs sentiment analysis on the top 100 posts from the r/stocks subreddit using machine learning models with **FinBERT embeddings** and additional text features. It is built with a **FastAPI** backend and a **React (Vite)** frontend.

## ✨ Features

- 🔍 Fetches and displays the top 100 posts from r/stocks subreddit.
- 🧠 Classifies each post as **Positive**, **Neutral**, or **Negative** using trained ML models.
- 📈 Uses FinBERT (pre-trained on financial text) for generating embeddings.
- 📊 Incorporates additional text features like word count and VADER sentiment scores.
- ⚡ Built with FastAPI for robust backend performance.
- ⚛️ Clean and fast React interface via Vite.

## 📸 Screenshots

![Main Dashboard](screenshots/sc4.png)

![Sentiment Results](screenshots/sc3.png)

![Post Details](screenshots/sc1.png)

![Post Details](screenshots/sc2.png)

## 🚀 Getting Started

#### 1. Clone the Repository

```bash
git clone https://github.com/anismabaziz/stock-mood
cd stock-mood
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Environment Configuration

Create a `.env` file in the backend directory:

```bash
reddit_client_id='your reddit client_id'
reddit_client_secret='your reddit client_secret'
reddit_user_agent='your reddit user_agent'
frontend_url='frontend dev url'
frontend_build='frontend production url'
```

Create a `.env` file in the frontend directory:

```bash
VITE_API_URL='backend dev url'
```

#### 4. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install
# or
yarn install
```

### 🏃‍♂️ Running the Application

#### Start Backend Server

```bash
cd backend
uvicorn main:app --reload
```

#### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

## 🧠 Machine Learning Model

### Model Selection & Testing

I tested multiple models to find the best performer:

- **Logistic Regression**: Baseline linear classifier
- **Random Forest**: Ensemble method with decision trees
- **Gradient Boosting**: Sequential ensemble learning
- **SVM**: Support Vector Machine with probability estimation
- **XGBoost**: Gradient boosting framework
- **MLP (scikit-learn)**: Multi-Layer Perceptron classifier
- **Custom Neural Network**: Self-implemented deep learning model - **Selected Model**

### Feature Engineering

- **FinBERT Embeddings**: Contextualized embeddings from financial domain pre-trained BERT
- **Text Statistics**: Word count and other linguistic features
- **VADER Sentiment**: Rule-based sentiment analysis scores as additional features
- **Training Data**: Labeled financial news articles (not Reddit-specific)
- **Model Accuracy**: ~80% on the validation set

The final model uses a **custom-built neural network** that combines FinBERT's powerful contextual understanding with traditional text features and VADER sentiment scores to achieve robust sentiment classification on financial discussions.

## 🛠️ Tech Stack

### Frontend:

- React (Vite)
- Axios

### Backend:

- FastAPI
- PRAW or custom Reddit scraper
- FinBERT (via HuggingFace Transformers)
- VADER Sentiment (via NLTK)
- scikit-learn / TensorFlow (for ML models)
- XGBoost
