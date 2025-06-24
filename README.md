# Portfolio Visualization App

This Streamlit application visualizes stock and ETF portfolio holdings and performance.

## Setup

1.  Clone the repository (if applicable).
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Ensure the API endpoint in `config.py` is active and accessible.
4.  Place performance CSV data in the folder specified in `config.py` (e.g., `performance_reports/`).

## Running the App

```bash
streamlit run app.py
```

To run the app on a specific port (e.g., 8502), use:
```bash
streamlit run app.py --server.port 8502
```
