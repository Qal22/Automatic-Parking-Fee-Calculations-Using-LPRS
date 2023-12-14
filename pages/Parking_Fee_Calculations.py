import streamlit as st
import database as db
from datetime import datetime
import requests
from billplz.client import Billplz
import webbrowser

st.set_page_config(page_title="Parking Fee Calculations", page_icon="🧮")

url = "https://www.billplz-sandbox.com/flj4cy9s7"

currentTime = datetime.now().strftime('%H:%M:%S')
hourly_rate = 5

button_disabled = True
fee = 0

st.title("Parking Fee Calculations")

st.sidebar.success("Select a page above")

def clear_text():
    st.session_state["textInput"] = ""

with st.form(key="myform"):
    st.header("Parking Rate: RM" + str(hourly_rate) + " per hour")

    licensePlate_number = st.text_input("Enter your license plate number (without space)", key = "textInput")

    col1, col2, col3 = st.columns([1,1,6])
    with col1:
        enter_button = st.form_submit_button("Enter")
    with col2:
        clear_button = st.form_submit_button("Clear", on_click=clear_text)

if clear_button:
    enter_button = False

if enter_button:
    with st.container():
        st.write("---")
        time = db.get_lpn(licensePlate_number)

        st.text_input("Time in", value=time["time"], disabled=True)
        st.text_input("Time out", value=currentTime, disabled=True)

        start_time = datetime.strptime(time["time"], "%H:%M:%S")
        end_time = datetime.strptime(currentTime, "%H:%M:%S")
        time_difference = end_time - start_time
        duration_seconds = int(time_difference.total_seconds())
        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        seconds = duration_seconds % 60
        duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        st.text_input("Duration", value=duration, disabled=True)

        hours, minutes, seconds = map(int, duration.split(':'))
        total_minutes = hours * 60 + minutes
        fee = total_minutes // 60 * hourly_rate
        if total_minutes % 60 > 0:
            fee += hourly_rate

        st.text_input("Parking Fee", value="RM {:.2f}".format(fee), disabled=True)

        st.write(f'<a href="{url}" target="_self"><button>Pay</button></a>', unsafe_allow_html=True)