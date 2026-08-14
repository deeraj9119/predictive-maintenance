# Predictive Maintenance FastAPI + Streamlit

Run the notebook first so it creates:

```bash
models/predictive_maintenance_model.pkl
```

Start the FastAPI server from the project root:

```bash
python -m uvicorn main:app --app-dir fastapi --reload
```

In another terminal, start Streamlit:

```bash
python -m streamlit run fastapi/streamlit_app.py
```

If `uvicorn` gives a "Fatal error in launcher" message, reinstall it into the
Python environment you are currently using:

```bash
python -m pip install --upgrade fastapi uvicorn streamlit requests
```

API docs will be available at:

```text
http://127.0.0.1:8000/docs
```
