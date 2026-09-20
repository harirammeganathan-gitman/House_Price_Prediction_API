import streamlit as st
import requests

st.title("🏠 House Price Prediction")

# Input field for single or multiple sizes
sizes_input = st.text_input("Enter house sizes (comma separated)", "1500")

if st.button("Predict Price"):
    try:
        # Convert input string to list of numbers
        sizes = [float(s.strip()) for s in sizes_input.split(",") if s.strip()]

        # Send request to Flask API
        response = requests.post(
            "http://localhost:5010/predict",
            json={"sizes": sizes}
        )

        if response.status_code == 200:
            results = response.json()
            # Handle single vs multiple results
            if isinstance(results, dict):
                st.success(f"Size: {results['size']} → Predicted Price: {results['predicted_price']}")
            else:
                st.table(results)
        else:
            st.error(f"Error: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        st.error(f"Invalid input: {e}")
