import streamlit as st
import numpy as np
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.model_utils import load_ecg2af_model, ecg_as_tensor, process_predictions

MODEL_PATH = '/app/ml4h/model_zoo/ECG2AF/ecg_5000_survival_curve_af_quadruple_task_mgh_v2021_05_21.h5'

def create_risk_gauge(risk_score):
    """Create a horizontal bar plot for risk visualization."""
    colors = ['#2ecc71', '#f1c40f', '#e74c3c']  # green, yellow, red
    
    if risk_score <= 0.3:
        color = colors[0]
    elif risk_score <= 0.7:
        color = colors[1]
    else:
        color = colors[2]
        
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = risk_score * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 30], 'color': '#ebfaef'},
                {'range': [30, 70], 'color': '#fef9e7'},
                {'range': [70, 100], 'color': '#fdedec'}
            ]
        },
        number = {'suffix': "%"}
    ))
    
    fig.update_layout(height=300)
    return fig

def create_two_column_metric(label1, value1, label2, value2):
    """Create a two-column layout for displaying paired metrics."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"<h2 style='text-align: center;'>{label1}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center;'>{value1:.1%}</h2>", unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"<h2 style='text-align: center;'>{label2}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center;'>{value2:.1%}</h2>", unsafe_allow_html=True)

def main():
    """Main function to run the Streamlit application."""
    st.set_page_config(page_title="ECG2AF Analysis")#, layout="wide")
    
    st.title("ECG2AF Model Analysis")
    
    st.markdown("""
    ## Welcome to the ECG2AF Analysis Tool
    
    This application analyzes electrocardiogram (ECG) data to:
    - Predict the risk of developing Atrial Fibrillation (AF)
    - Probability of AF at the time of ECG
    - Estimate demographic information (age and sex)
    - Generate a survival probability curve - shows the survival curve prediction for incident atrial fibrillation

    For more information on the methods please visit : https://www.ahajournals.org/doi/full/10.1161/CIRCULATIONAHA.121.057480
    
    Simply upload your ECG file in HD5 format to begin the analysis.
    
    ---
    """)
    
    uploaded_file = st.file_uploader("Upload an ECG file (HD5 format)", type=['h5', 'hd5'])

    if uploaded_file is not None:
        with open("temp_ecg.h5", "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            model, output_tensormaps = load_ecg2af_model(MODEL_PATH)
            ecg_tensor = ecg_as_tensor("temp_ecg.h5")
            predictions = model.predict(np.expand_dims(ecg_tensor, axis=0))
            results = process_predictions(model, output_tensormaps, predictions)

            # Display results in organized sections
            st.markdown("---")
            
            # AF Risk Score Section
            st.markdown("<h2 style='text-align: center; color: #2c3e50;'>AF Risk Score</h2>", unsafe_allow_html=True)
            risk_score = results['survival_curve']['af_risk']
            risk_fig = create_risk_gauge(risk_score)
            st.plotly_chart(risk_fig, use_container_width=True)
            
            st.markdown("---")
            
            # Sex Prediction Section
            st.markdown("<h2 style='text-align: center; color: #2c3e50;'>Sex Prediction</h2>", unsafe_allow_html=True)
            sex_pred = results['TensorMap(sex_from_wide, (2,), categorical)']
            create_two_column_metric("Male", sex_pred[0], "Female", sex_pred[1])
            
            st.markdown("---")
            
            # Age Prediction Section
            st.markdown("<h2 style='text-align: center; color: #2c3e50;'>Predicted Age (normalized) </h2>", unsafe_allow_html=True)
            age_pred = results['TensorMap(age_from_wide_csv, (1,), continuous)']
            st.markdown(f"<h1 style='text-align: center;'>{age_pred[0]:.1f}</h1>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # AF Classification Section
            st.markdown("<h2 style='text-align: center; color: #2c3e50;'>Current AF Classification</h2>", unsafe_allow_html=True)
            af_pred = results['TensorMap(af_in_read, (2,), categorical)']
            create_two_column_metric("No AF", af_pred[0], "AF Present", af_pred[1])
            
            st.markdown("---")

            # Survival Curve Section
            st.markdown("<h2 style='text-align: center; color: #2c3e50;'>AF Survival Probability Over Time</h2>", unsafe_allow_html=True)
            
            survival_df = pd.DataFrame({
                'Days': results['survival_curve']['days'],
                'Survival Probability': results['survival_curve']['values']
            })
            
            fig = px.line(survival_df, 
                         x='Days', 
                         y='Survival Probability',
                         title='')
            
            fig.update_layout(
                xaxis_title="Days",
                yaxis_title="Survival Probability",
                yaxis_range=[0.7, 1.0],
                showlegend=False,
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
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
