# Multi-Domain Intelligence Platform

Student Name: Harry Beckwith

Student ID: M01022216

Course: CST1510: Programming for Data Communication and Networks -CW2

## Project Description
The Multi-Domain Intelligence Platform is a platform constructed with Python with the propose to help the user collect, process, and analyse the data of their selected domains through the usage of graphs, tables and an onboard API (Application Programming Interface). The domains available to the user are cybersecurity, data science and IT operations.

## Installation
- To get the onboard API to work you need to navigate to the .streamlit folder (file path:     CW2_M01022216_CST1510\my_app\.streamlit). Inside the folder open the secrets.toml file paste your Gemini API key between the double quote marks. You can then save the changes and close the file.
- To run the platform, open the project in your code editor program (eg. PyCharm or Visual Studio Code) open the terminal inside the program and type: streamlit run Home.py

  IF THAT DOES NOT WORK!
  Type: python.exe -m steamlit run my_app/Home.py

## Usage
When the program is running on streamlit.
1. The user will start of in the Home page there the user must ever login or register.
   - If the user selects to register. They must choose a unique username and then make a password and confirm their password.
   - If the user select to login. They must enter the correct information to login.
     
2. The user will then be taken to the Dashboard page where they must choose one of the three available domains.
   
3. After selecting a domain, the use can then view its content and can edit the data in the database of the selected domain.
    - If the user decides to add a new entry. They must fill in the required fields to insert the new entry.
    - If the user decides to update the status of an entry (only available in the cybersecurity and IT operations domains). They must select a pre-existing entry and change its status.
    - If the user decides to delete an entry. They must select a pre-existing entry and then delete it.

4. The user can then decide to switch to the Gemini API page where they can select a domain and discuss it with the API.

5. The user can choose to erase the chat history resetting the memory of the API.

6. The use can choose to logout.


