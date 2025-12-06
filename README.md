# NUST Helpbot

A local, privacy-first Retrieval-Augmented Generation (RAG) chatbot for answering questions about NUST's UG Student Handbook and other institutional documents. Powered by Ollama (DeepSeek R1 1.5B), LangChain, and Streamlit.

## 🌟 Features

- **Document-Based Q&A**: Get accurate answers from official NUST handbooks and documents
- **Multiple Handbooks Support**: Easily switch between different handbooks/documents
- **Conversation History**: Maintains context of your conversation
- **Follow-up Questions**: Suggests relevant follow-up questions based on context
- **Private & Secure**: No data leaves your machine, runs fully offline with Ollama
- **Modern Chat Interface**: Intuitive, user-friendly interface built with Streamlit
- **No Hallucination**: Strict prompt engineering to ensure responses are based solely on provided documents

## 🚀 Quickstart

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) installed and running locally
- DeepSeek R1 1.5B model: `ollama pull deepseek-r1:1.5b`

### Installation
1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd NUST-Helpbot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Prepare Your Documents
1. Create a `data` directory in the project root
2. Place your PDF documents (e.g., handbooks, guides) in the `data` directory
   - Each subdirectory in `data/` will be treated as a separate handbook
   - Ensure PDFs are properly formatted and text is selectable

### Initialize the Database
```bash
python populate_database.py --reset
```

### Start the Application
```bash
streamlit run app.py
```
- Open [http://localhost:8501](http://localhost:8501) in your web browser

## 🎯 Usage

1. **Select a Handbook**: Choose from available handbooks in the dropdown menu
2. **Ask Questions**: Type your question in the chat input
3. **Get Answers**: The bot will respond using information from the selected handbook
4. **Follow-up**: Use suggested follow-up questions to explore related information

## 🔧 Advanced Configuration

### Database Management
- To clear and rebuild the vector database:
  ```bash
  python populate_database.py --reset
  ```

### Adding New Documents
1. Add new PDF files to the `data/` directory
2. Run the database population script:
   ```bash
   python populate_database.py
   ```

## 📊 Logging

User interactions are logged to `chat_logs.db` for analysis and improvement. This helps in:
- Understanding common queries
- Improving response accuracy
- Identifying areas where the knowledge base needs expansion

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## 📄 License

[Specify License]

## 📧 Contact

For support or questions, please contact [your-email@example.com]

## 🙏 Acknowledgments

- Built with [Ollama](https://ollama.com/), [LangChain](https://www.langchain.com/), and [Streamlit](https://streamlit.io/)
- Uses the DeepSeek R1 1.5B model for local inference

---

## Troubleshooting
- **Ollama not found:** Ensure Ollama is installed and running (`ollama serve`).
- **Model not found:** Run `ollama pull deepseek-r1:1.5b`.
- **No answers returned:** Ensure your PDFs are in `data/` and database is populated.
- **Deprecation warnings:** This project uses the latest LangChain packages as of July 2025.

---

## Credits
- Built with [LangChain](https://www.langchain.com/), [Ollama](https://ollama.com/), [Streamlit](https://streamlit.io/), [DeepSeek R1 1.5B](https://huggingface.co/deepseek-ai/DeepSeek-V2), and [PyPDF](https://pypdf.readthedocs.io/).

---