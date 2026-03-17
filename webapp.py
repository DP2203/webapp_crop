import streamlit as st
import re
import sqlite3
import pickle
import bz2
import pandas as pd
import os

# Page config
st.set_page_config(page_title="Crop Recommendation", page_icon="fevicon.png", layout="centered")

# Check if model exists
if os.path.exists("model.pkl"):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    # DB Functions
    def create_usertable():
        c.execute('''CREATE TABLE IF NOT EXISTS userstable (
            FirstName TEXT, LastName TEXT, Mobile TEXT, City TEXT, Email TEXT UNIQUE, 
            password TEXT, Cpassword TEXT)''')

    def add_userdata(FirstName, LastName, Mobile, City, Email, password, Cpassword):
        c.execute('INSERT INTO userstable (FirstName, LastName, Mobile, City, Email, password, Cpassword) VALUES (?, ?, ?, ?, ?, ?, ?)',
                  (FirstName, LastName, Mobile, City, Email, password, Cpassword))
        conn.commit()

    def email_exists(Email):
        c.execute("SELECT * FROM userstable WHERE Email = ?", (Email,))
        return c.fetchone() is not None

    def login_user(Email, password):
        c.execute('SELECT * FROM userstable WHERE Email =? AND password = ?', (Email, password))
        return c.fetchall()

    def view_all_users():
        c.execute('SELECT * FROM userstable')
        return c.fetchall()

    def delete_user(Email):
        c.execute("DELETE FROM userstable WHERE Email = ?", (Email,))
        conn.commit()

    # Sidebar menu
    menu = ["Home", "Login", "SignUp"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.markdown(
            """
            <h2 style="color:black">Welcome to Crop-Recommendation</h2>
            <p align="justify">
            <b style="color:black">
            Indian economy is contributed heavily by agriculture. Most of the Indian farmers rely on their instincts to decide the crop to be sown at a particular time of year. They do not realize that the crop output is circumstantial, and depended heavily on the present-day weather and soil conditions. A single uninformed decision by the farmer can have undesirable consequences on the economic conditions of the region and also mental and financial impacts on the farmer himself. Applying systematic Machine Learning models will effectively help to alleviate this issue. The dataset used in the project is built by adding up the datasets of India's rainfall, climate, and Soil. Machine learning models will be used on the dataset to get the highest accuracy model to recommend a crop for the farm's location. This recommendation will help the farmers in India to make learned decisions about the crops. The recommendation will take into account the parameters like the farm's location, sowing season, soil properties, and climate.
            </b></p>
            """, unsafe_allow_html=True)

    elif choice == "Login":
        Email = st.sidebar.text_input("Email")
        Password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.checkbox("Login"):
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if re.fullmatch(regex, Email):
                create_usertable()
                if Email == 'a@a.com' and Password == '123':
                    st.success("Logged In as Admin")
                    user_result = view_all_users()
                    if st.button("Show All Users"):
                        st.dataframe(pd.DataFrame(user_result, columns=["FirstName", "LastName", "Mobile", "City", "Email", "Password", "Cpassword"]))
                    del_email = st.text_input("Delete Email")
                    if st.button('Delete'):
                        delete_user(del_email)
                        st.success("Deleted Successfully")
                else:
                    result = login_user(Email, Password)
                    if result:
                        st.success(f"Logged In as {Email}")
                        choic = st.selectbox("Select Parameters", ["Soil", "Weather", "All"])
                        st.text("ML is VotingClassifier")

                        # Reset logic
                        if "reset_triggered" not in st.session_state:
                            st.session_state.reset_triggered = False

                        if st.session_state.reset_triggered:
                            keys = ["N", "P", "K", "temp", "Hum", "Ph", "Rain"]
                            for k in keys:
                                st.session_state[k] = 0.0
                            st.session_state.reset_triggered = False
                            st.rerun()

                        # Sliders
                        if choic == "Soil":
                            N = st.slider('Nitrogen Value', 0.0, 140.0, st.session_state.get("N", 60.0), key="N")
                            P = st.slider('Phosphorus Value', 5.0, 145.0, st.session_state.get("P", 50.0), key="P")
                            K = st.slider('Potassium Value', 5.0, 205.0, st.session_state.get("K", 40.0), key="K")
                            tdata = [N, P, K]
                            model_file = 'modelS.pkl'

                        elif choic == "Weather":
                            temp = st.slider('Temperature', 8.0, 44.0, st.session_state.get("temp", 25.0), key="temp")
                            Hum = st.slider('Humidity', 14.0, 100.0, st.session_state.get("Hum", 60.0), key="Hum")
                            Ph = st.slider('pH', 3.5, 10.0, st.session_state.get("Ph", 6.5), key="Ph")
                            Rain = st.slider('Rainfall', 20.0, 299.0, st.session_state.get("Rain", 100.0), key="Rain")
                            tdata = [temp, Hum, Ph, Rain]
                            model_file = 'modelW.pkl'

                        else:
                            N = st.slider('Nitrogen Value', 0.0, 140.0, st.session_state.get("N", 60.0), key="N")
                            P = st.slider('Phosphorus Value', 5.0, 145.0, st.session_state.get("P", 50.0), key="P")
                            K = st.slider('Potassium Value', 5.0, 205.0, st.session_state.get("K", 40.0), key="K")
                            temp = st.slider('Temperature', 8.0, 44.0, st.session_state.get("temp", 25.0), key="temp")
                            Hum = st.slider('Humidity', 14.0, 100.0, st.session_state.get("Hum", 60.0), key="Hum")
                            Ph = st.slider('pH', 3.5, 10.0, st.session_state.get("Ph", 6.5), key="Ph")
                            Rain = st.slider('Rainfall', 20.0, 299.0, st.session_state.get("Rain", 100.0), key="Rain")
                            tdata = [N, P, K, temp, Hum, Ph, Rain]
                            model_file = 'model.pkl'

                        # Load model
                        sfile = bz2.BZ2File(model_file, 'rb')
                        model = pickle.load(sfile)

                        # Predict
                        if st.button("Recommend"):
                            prediction = model[6].predict([tdata])[0]
                            st.success(f"Recommended Crop: {prediction}")

                        # Reset button
                        if st.button("Reset"):
                            st.session_state.reset_triggered = True
                            st.rerun()

                    else:
                        st.warning("Incorrect Email/Password")
            else:
                st.warning("Invalid Email Format")

    elif choice == "SignUp":
        Fname = st.text_input("First Name")
        Lname = st.text_input("Last Name")
        Mname = st.text_input("Mobile Number")
        Email = st.text_input("Email")
        City = st.text_input("City")
        Password = st.text_input("Password", type="password")
        CPassword = st.text_input("Confirm Password", type="password")

        if st.button("SignUp"):
            pattern = re.compile("(0|91)?[7-9][0-9]{9}")
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if Password != CPassword:
                st.warning("Passwords do not match")
            elif not pattern.match(Mname):
                st.warning("Invalid Mobile Number")
            elif not re.fullmatch(regex, Email):
                st.warning("Invalid Email")
            elif email_exists(Email):
                st.warning("Email already exists")
            else:
                create_usertable()
                add_userdata(Fname, Lname, Mname, City, Email, Password, CPassword)
                st.success("Signup Successful. Please login.")

else:
    st.error("Model file not found. Please train your models and generate model.pkl files.")
