import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(page_title="Predictive Maintenance", page_icon="ML", layout="centered")

st.title("Predictive Maintenance")
st.caption("Enter machine readings and get a failure prediction from the FastAPI model service.")

with st.form("prediction_form"):
    product_type = st.selectbox("Product Type", ["L", "M", "H"], index=1)
    air_temperature = st.number_input("Air temperature [K]", min_value=250.0, max_value=350.0, value=298.0, step=0.1)
    process_temperature = st.number_input("Process temperature [K]", min_value=250.0, max_value=400.0, value=309.0, step=0.1)
    rotational_speed = st.number_input("Rotational speed [rpm]", min_value=0.0, value=1500.0, step=10.0)
    torque = st.number_input("Torque [Nm]", min_value=0.0, value=40.0, step=0.1)
    tool_wear = st.number_input("Tool wear [min]", min_value=0.0, value=100.0, step=1.0)

    submitted = st.form_submit_button("Predict")

if submitted:
    payload = {
        "Type": product_type,
        "air_temperature_k": air_temperature,
        "process_temperature_k": process_temperature,
        "rotational_speed_rpm": rotational_speed,
        "torque_nm": torque,
        "tool_wear_min": tool_wear,
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()

        if result["prediction"] == 1:
            st.error("Prediction: Failure")
        else:
            st.success("Prediction: No Failure")

        probability = result.get("failure_probability")
        if probability is not None:
            st.metric("Failure probability", f"{probability:.2%}")

        st.write(f"Model used: {result.get('model_name')}")
    except requests.exceptions.ConnectionError:
        st.error("FastAPI server is not running. Start it with: uvicorn main:app --app-dir fastapi --reload")
    except Exception as exc:
        st.error(f"Prediction failed: {exc}")
