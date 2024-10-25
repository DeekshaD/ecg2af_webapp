import streamlit as st
import numpy as np
import os
import pandas as pd
import plotly.express as px
from .utils.model_utils import load_ecg2af_model, ecg_as_tensor, process_predictions

MODEL_PATH = '/app/ml4h/model_zoo/ECG2AF/ecg_5000_survival_curve_af_quadruple_task_mgh_v2021_05_21.h5'

def main():
    """Main function to run the Streamlit application."""
    st.title("ECG2AF Model Web Application")
    
    uploaded_file = st.file_uploader("Upload an ECG file (HD5 format)", type=['h5', 'hd5'])

    if uploaded_file is not None:
        with open("temp_ecg.h5", "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            model, output_tensormaps = load_ecg2af_model(MODEL_PATH)
            ecg_tensor = ecg_as_tensor("temp_ecg.h5")
            predictions = model.predict(np.expand_dims(ecg_tensor, axis=0))
            results = process_predictions(model, output_tensormaps, predictions)

            # Display results
            st.subheader("Prediction Results")
            
            # Display AF Risk
            st.write(f"AF Risk: {results['survival_curve']['af_risk']:.4f}")
            
            # Display Sex Prediction
            sex_pred = results['TensorMap(sex_from_wide, (2,), categorical)']
            st.write("Sex Prediction:")
            st.write(f"- Male: {sex_pred[0]:.4f}")
            st.write(f"- Female: {sex_pred[1]:.4f}")
            
            # Display Age Prediction
            age_pred = results['TensorMap(age_from_wide_csv, (1,), continuous)']
            st.write(f"Age Prediction (normalized): {age_pred[0]:.4f}")
            
            # Display AF Classification
            af_pred = results['TensorMap(af_in_read, (2,), categorical)']
            st.write("AF Classification:")
            st.write(f"- No AF: {af_pred[0]:.4f}")
            st.write(f"- AF Present: {af_pred[1]:.4f}")

            # Display Survival Curve
            st.subheader("AF Survival Curve")
            
            survival_df = pd.DataFrame({
                'Days': results['survival_curve']['days'],
                'Survival Probability': results['survival_curve']['values']
            })
            
            fig = px.line(survival_df, 
                         x='Days', 
                         y='Survival Probability',
                         title='AF Survival Probability Over Time')
            
            fig.update_layout(
                xaxis_title="Days",
                yaxis_title="Survival Probability",
                yaxis_range=[0.7, 1.0],
                showlegend=True
            )
            
            st.plotly_chart(fig)
            
            if st.checkbox("Show raw survival data"):
                st.dataframe(survival_df)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.error("Stack trace:", exc_info=True)

        finally:
            if os.path.exists("temp_ecg.h5"):
                os.remove("temp_ecg.h5")

if __name__ == "__main__":
    main()
