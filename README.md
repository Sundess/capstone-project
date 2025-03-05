# Capstone Project: Product Review Analysis & Chatbot

## Overview

This project is a web-based application designed to analyze product reviews, summarize text, perform sentiment analysis, and provide an interactive chatbot for users to engage with product-related queries. The application features an admin dashboard with detailed insights into product sentiment, recommendations, and review summaries.

## Features

- **Admin Dashboard**: View detailed product insights, including overall sentiment, review summaries, and recommendations.
- **Sentiment Analysis**: Analyzes user reviews and determines the sentiment polarity.
- **Text Summarization**: Generates concise summaries of product reviews using Gemini-7B.
- **Chatbot**: Interactive chatbot powered by LLAMA-8B that answers product-related questions.
- **Vectorization & Similarity Search**: Uses Google Embeddings for text vectorization and FAISS for efficient similarity search.

## Tech Stack

### Backend

- **Django**: Web framework for handling API requests and managing application logic.
- **FAISS**: Used for similarity search and efficient retrieval of relevant reviews.

### Frontend

- **HTML, CSS, JavaScript**: For building a responsive user interface.
- **Streamlit: For building chatbot interface.**

### NLP & AI

- **TextBlob**: For sentiment analysis of user reviews.
- **Gemini-7B**: Used for text summarization via the Groq API.
- **LLAMA-8B**: Chatbot powered by Groq for product-related conversations.
- **Google Embeddings**: Converts text into vector representations for similarity search.

## Installation & Setup

### Prerequisites

- Ensure Python is installed on your system.
- Set up a virtual environment.

### Steps to Run the Project

1. **Activate Virtual Environment** (if using virtualenv or conda):
   ```sh
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   ```
2. **Install Dependencies**:
   ```sh
   pip install -r requirements.txt
   ```
3. **Set Up Environment Variables**:
   - Rename `.env_change` to `.env`.
   - Add your API key to the `.env` file.
4. **Run Migrations**:
   ```sh
   python manage.py migrate
   ```
5. **Start the Django Server**:
   ```sh
   python manage.py runserver
   ```

## Usage

- Access the **Admin Dashboard** at `http://127.0.0.1:8000/admin/`.
- Interact with the **Chatbot** for product-related inquiries.
- Check **Sentiment Analysis** and **Summarized Reviews** on the product details page.

## Contributing

Contributions are welcome! Feel free to submit a pull request or open an issue for improvements.

## License

This project is licensed under the MIT License.

## Contact

For any queries or contributions, feel free to reach out!

