# Code implementation for the presentation

import streamlit as st

# Sample data
data = [1, 2, 3, 4, 5]

# Simple layout without background_gradient
st.title('Presentation Demo')
st.write('This is a simple presentation demo with basic formatting.')

st.line_chart(data)  
