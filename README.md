# Reddit Stock Sentiment Analyzer 🧠📈

This is a full-stack web application that performs sentiment analysis on the top 100 posts from the [r/stocks](https://www.reddit.com/r/stocks/) subreddit using a **Multi-Layer Perceptron (MLP)** model with **FinBERT embeddings**. It is built with a **FastAPI** backend and a **React (Vite)** frontend.

---

## ✨ Features

- 🔍 Fetches and displays the top 100 posts from r/stocks subreddit.
- 🧠 Classifies each post as **Positive**, **Neutral**, or **Negative** using an MLP model.
- 📈 Uses FinBERT (pre-trained on financial text) for generating embeddings.
- ⚡ Built with FastAPI for robust backend performance.
- ⚛️ Clean and fast React interface via Vite.

---

## 🧠 Machine Learning Model

- **Model Type**: Multi-Layer Perceptron (MLP)
- **Embeddings**: FinBERT
- **Training Data**: Labeled financial news articles (not Reddit-specific)
- **Accuracy**: ~80% on the validation set

> FinBERT was used to convert raw text into contextualized embeddings. These embeddings were then used to train a lightweight MLP for classification.

---

## 🛠️ Tech Stack

**Frontend:**

- React (Vite)
- Axios
- TailwindCSS (optional)

**Backend:**

- FastAPI
- Pydantic
- PRAW or custom Reddit scraper
- FinBERT (via HuggingFace Transformers)
- scikit-learn / TensorFlow (for MLP)
- Uvicorn
