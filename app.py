import streamlit as st
import numpy as np
import plotly.graph_objects as go
import base64

st.set_page_config(layout="wide")

# ✅ Your background image path
file_path = "/home/arc/Desktop/background.webp"  

def set_background(file_path):
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    bg_style = f"""
        <style>
        .stApp {{
            background: url("data:image/webp;base64,{encoded_string}") no-repeat center center fixed;
            background-size: cover;
        }}
        </style>
    """
    st.markdown(bg_style, unsafe_allow_html=True)

# Apply the background
set_background(file_path)

if "page" not in st.session_state:
    st.session_state.page = "start"

if st.session_state.page == "start":
    # Create empty columns to push content to the right
    col1, col2 = st.columns([2, 1])  # Adjust ratio to shift more

    with col2:  # Place the title and button in the right column
        st.title("Welcome to Transformer Losses Analyzer")
        if st.button("Let's Start Analyzing"):
            st.session_state.page = "analyze"
            st.rerun()


elif st.session_state.page == "analyze":
    st.title("Transformer Losses Analyzer & Efficiency Calculator")

    col1, col2 = st.columns(2)

    with col1:
        st.header("Input Parameters")
        primary_voltage = st.number_input("Enter Primary Voltage (V)", min_value=1.0, step=1.0)
        secondary_voltage = st.number_input("Enter Secondary Voltage (V)", min_value=1.0, step=1.0)
        power = st.number_input("Enter Rated Power (kVA)", min_value=1.0, step=1.0)
        frequency = st.number_input("Enter Frequency (Hz)", min_value=1.0, step=1.0)
        resistance = st.number_input("Enter Winding Resistance (Ω)", min_value=0.1, step=0.1)
        core_type = st.selectbox("Select Core Type", ["CRGO", "Ferrite", "Amorphous", "Nano-crystalline"])
        core_size = st.number_input("Enter Core Size (cm²)", min_value=1.0, step=0.1)
        temperature = st.number_input("Enter Operating Temperature (°C)", min_value=-50.0, max_value=200.0, step=1.0)
        load_levels = st.slider("Select Load Levels (%)", min_value=0, max_value=100, step=5)

    with col2:
        st.header("Output Visualization")
        chart_placeholder = st.empty()

    if st.button("Calculate & Plot"):
        if primary_voltage > 0 and secondary_voltage > 0 and power > 0 and frequency > 0 and resistance > 0:
            x_data = np.linspace(0, power, 50)
            iron_loss = (0.01 * x_data**1.2) + (0.005 * primary_voltage) + (0.002 * frequency) + (0.0001 * core_size)
            copper_loss = (resistance * (x_data / power)**2) * power
            stray_loss = (0.0005 * x_data * core_size) + (0.0002 * temperature)
            dielectric_loss = (0.0001 * x_data * frequency) + (0.00005 * temperature)
            total_loss = iron_loss + copper_loss + stray_loss + dielectric_loss
            efficiency = (x_data / (x_data + total_loss)) * 100

            y_max = max(max(total_loss), max(efficiency)) * 1.2
            x_max = power * 1.2

            fig = go.Figure()

            fig.add_trace(go.Scatter(x=[], y=[], mode="lines", name="Iron Loss", 
                                     line=dict(color="orangered", width=5)))
            fig.add_trace(go.Scatter(x=[], y=[], mode="lines", name="Copper Loss", 
                                     line=dict(color="dodgerblue", width=5)))
            fig.add_trace(go.Scatter(x=[], y=[], mode="lines", name="Stray Loss", 
                                     line=dict(color="purple", width=5)))
            fig.add_trace(go.Scatter(x=[], y=[], mode="lines", name="Dielectric Loss", 
                                     line=dict(color="cyan", width=5)))
            fig.add_trace(go.Scatter(x=[], y=[], mode="lines", name="Efficiency (%)", 
                                     line=dict(color="limegreen", width=5)))

            frames = []
            step_size = max(1, len(x_data) // 30)

            for i in range(1, len(x_data) + 1, step_size):
                frames.append(
                    go.Frame(
                        data=[
                            go.Scatter(x=x_data[:i], y=iron_loss[:i], mode="lines", name="Iron Loss", 
                                       line=dict(color="orangered", width=5)),
                            go.Scatter(x=x_data[:i], y=copper_loss[:i], mode="lines", name="Copper Loss", 
                                       line=dict(color="dodgerblue", width=5)),
                            go.Scatter(x=x_data[:i], y=stray_loss[:i], mode="lines", name="Stray Loss", 
                                       line=dict(color="purple", width=5)),
                            go.Scatter(x=x_data[:i], y=dielectric_loss[:i], mode="lines", name="Dielectric Loss", 
                                       line=dict(color="cyan", width=5)),
                            go.Scatter(x=x_data[:i], y=efficiency[:i], mode="lines", name="Efficiency (%)", 
                                       line=dict(color="limegreen", width=5))
                        ]
                    )
                )

            fig.frames = frames if frames else [go.Frame(data=[])]

            fig.update_layout(
                title=dict(
                    text="Transformer Losses & Efficiency",
                    font=dict(color="white", size=18)
                ),
                xaxis=dict(
                    title="Load (kVA)",
                    title_font=dict(color="white", size=14),
                    tickfont=dict(color="white", size=12),
                    showgrid=True, gridcolor="lightgray",
                    range=[0, x_max]
                ),
                yaxis=dict(
                    title="Losses (W) / Efficiency (%)",
                    title_font=dict(color="white", size=14),
                    tickfont=dict(color="white", size=12),
                    showgrid=True, gridcolor="lightgray",
                    range=[0, y_max]
                ),
                plot_bgcolor="dark gray",
                paper_bgcolor="dark gray",
                font=dict(color="white"),
                width=950,
                height=600,
                legend=dict(
                    font=dict(color="white", size=12),
                    bgcolor="dark gray",
                    bordercolor="white",
                    borderwidth=1
                ),
                updatemenus=[{
                    "buttons": [
                        {
                            "args": [None, {"frame": {"duration": 20, "redraw": True}, "fromcurrent": True}],
                            "label": "Play",
                            "method": "animate"
                        },
                        {
                            "args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
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

            chart_placeholder.plotly_chart(fig, use_container_width=True)

        else:
            st.error("Please enter valid input values.")
