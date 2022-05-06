import streamlit as st
import pandas as pd
import requests


st.title("Title","title")

st.code('st.title("Title","title")',"python")

st.latex(r'''
     a + ar + a r^2 + a r^3 + \cdots + a r^{n-1} =
     \sum_{k=0}^{n-1} ar^k =
     a \left(\frac{1-r^{n}}{1-r}\right)
     ''')

clicked = st.button("click there")
st.write(clicked)