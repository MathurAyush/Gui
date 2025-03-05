import streamlit as st
import numpy as np
import plotly.graph_objects as go
import base64

st.set_page_config(layout="wide")

# ✅ Use a relative path
file_path = "background.jpg"  # Since the image is inside the same folder as app.py

def set_background(file_path):
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    bg_style = f"""
    <style>
    .stApp {{
        background: url("data:image/jpg;base64,{encoded_string}") no-repeat center center fixed;
        background-size: cover;
    }}
    </style>
    """
    st.markdown(bg_style, unsafe_allow_html=True)

# Apply the background
set_background(file_path)

if "page" not in st.session_state:
    st.session_state.page = "welcome"

if st.session_state.page == "welcome":
    st.title("Welcome to Transformers GUI")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Let's Start"):
            st.session_state.page = "input_graph"
            st.rerun()
    
    with col2:
        if st.button("Developed by"):
            st.info("Developed by: Ayush, Rudra, Prashant, and Dinesh")
else:
    if "graph_index" not in st.session_state:
        st.session_state.graph_index = 0
    if "show_graph" not in st.session_state:
        st.session_state.show_graph = False

    graphs = [
        "Iron Core Loss vs Voltage/Frequency", 
        "Copper Loss vs Load", 
        "Stray & Dielectric Loss vs Temperature", 
        "Efficiency vs Load"]

    st.title("Transformer Losses Analysis")

    # User Inputs
    st.sidebar.header("Input Parameters")
    primary_voltage = st.sidebar.number_input("Primary Voltage (V)", min_value=1.0, step=1.0)
    secondary_voltage = st.sidebar.number_input("Secondary Voltage (V)", min_value=1.0, step=1.0)
    power = st.sidebar.number_input("Rated Power (kVA)", min_value=1.0, step=1.0)
    frequency = st.sidebar.number_input("Frequency (Hz)", min_value=1.0, step=1.0)
    core_type = st.sidebar.selectbox("Core Type", ["CRGO", "Ferrite", "Amorphous", "Nano-crystalline"])
    winding_resistance = st.sidebar.number_input("Winding Resistance (Ω)", min_value=0.1, step=0.1)
    load_levels = st.sidebar.slider("Load Levels (%)", min_value=0, max_value=100, step=5)
    temperature = st.sidebar.slider("Operating Temperature (°C)", min_value=-50, max_value=200, step=5)

    if st.sidebar.button("Generate Graphs"):
        st.session_state.show_graph = True
        st.rerun()

    if st.session_state.show_graph:
        st.header(graphs[st.session_state.graph_index])

        fig = go.Figure()
        x_values = np.linspace(0, 100, 50)

        if st.session_state.graph_index == 0:
            y_values = (0.05 * x_values**1.5) + (0.01 * primary_voltage) + (0.005 * frequency)
            y_values = -((0.01 * x_values**1.2) + (0.005 * primary_voltage) + (0.002 * frequency))
            fig.add_trace(go.Scatter(x=x_values, y=y_values, mode="lines", name="Iron Core Loss", line=dict(color="orangered")))
            fig.update_layout(title="Iron Core Loss vs Voltage/Frequency", xaxis_title="Voltage (V) / Frequency (Hz)", yaxis_title="Iron Loss (W)")

        elif st.session_state.graph_index == 1:
            y_values = (winding_resistance * (x_values / 100)**2.5) * power
            y_values = (winding_resistance * (x_values / 100)**2) * power + 5 * np.sin(x_values / 10)
            fig.add_trace(go.Scatter(x=x_values, y=y_values, mode="lines", name="Copper Loss", line=dict(color="dodgerblue")))
            fig.update_layout(title="Copper Loss vs Load", xaxis_title="Load (%)", yaxis_title="Copper Loss (W)")

        elif st.session_state.graph_index == 2:
            y_stray_loss = (0.001 * x_values**1.2 * power) + (0.0003 * frequency) + 2 * np.cos(x_values / 15)
            y_dielectric_loss = (0.0002 * x_values**1.5 * frequency) + (0.0001 * power) - 1.5 * np.sin(x_values / 20)
            fig.add_trace(go.Scatter(x=x_values, y=y_stray_loss, mode="lines", name="Stray Loss", line=dict(color="purple")))
            fig.add_trace(go.Scatter(x=x_values, y=y_dielectric_loss, mode="lines", name="Dielectric Loss", line=dict(color="cyan")))
            fig.update_layout(title="Stray & Dielectric Loss vs Temperature", xaxis_title="Temperature (°C)", yaxis_title="Loss (W)")
            y_values = [y_stray_loss, y_dielectric_loss]  # For multiple traces
        
        elif st.session_state.graph_index == 3:
            core_efficiency_factor = {"CRGO": 0.98, "Ferrite": 0.95, "Amorphous": 0.99, "Nano-crystalline": 0.995}
            efficiency_factor = core_efficiency_factor.get(core_type, 0.97)
            total_loss = (0.01 * x_values**1.2) + (winding_resistance * (x_values / 100)**2) * power + (0.0005 * x_values * power) + (0.0002 * frequency)
            y_values = (efficiency_factor * x_values / (x_values + total_loss)) * 100 + 3 * np.cos(x_values / 10)
            y_values = (efficiency_factor * x_values / (x_values + total_loss)) * 100 - 0.05 * x_values**1.3
            fig.add_trace(go.Scatter(x=x_values, y=y_values, mode="lines", name=f"Efficiency ({core_type})", line=dict(color="limegreen")))
            fig.update_layout(title=f"Efficiency vs Load ({core_type})", xaxis_title="Load (%)", yaxis_title="Efficiency (%)")

        # Create frames for animation
        frames = []
        if st.session_state.graph_index == 2:  # For graphs with multiple traces
            for i in range(1, len(x_values)):
                frames.append(go.Frame(
                    data=[
                        go.Scatter(x=x_values[:i], y=y_stray_loss[:i], mode="lines", name="Stray Loss"),
                        go.Scatter(x=x_values[:i], y=y_dielectric_loss[:i], mode="lines", name="Dielectric Loss")
                    ]
                ))
        else:  # For graphs with a single trace
            for i in range(1, len(x_values)):
                frames.append(go.Frame(
                    data=[go.Scatter(x=x_values[:i], y=y_values[:i], mode="lines")]
                ))

        fig.frames = frames

        # Add animation controls
        fig.update_layout(
            updatemenus=[{
                "type": "buttons",
                "buttons": [
                    {
                        "args": [None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}],
                        "label": "Play",
                        "method": "animate"
                    },
                    {
                        "args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                        "label": "Pause",
                        "method": "animate"
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }]
        )

        st.plotly_chart(fig, use_container_width=True)

        col1, col2, col3 = st.columns([1, 1, 1])

        with col2:
            if st.button("Next Graph"):
                st.session_state.graph_index = (st.session_state.graph_index + 1) % len(graphs)
                st.rerun()
