import streamlit as st
import pandas as pd
import numpy as np
import requests
import json

st.title("Gene indirection")
st.write("Supply a gene symbol, and automatically call find-subject-variants")


@st.cache
def translateGene(geneSymbol):
	url='https://fhir-gen-ops.herokuapp.com/utilities/get-feature-coordinates?gene='+ geneSymbol
	headers={'Accept': 'application/json'}
	r=requests.get(url, headers=headers)
	return r.json()	


@st.cache
def findSubjectVariants(subject, region):
	url='https://fhir-gen-ops.herokuapp.com/subject-operations/genotype-operations/$find-subject-variants?subject='+subject+'&ranges='+region+'&includeVariants=false'
	headers={'Accept': 'application/json'}
	r=requests.get(url, headers=headers)
	return r.json()

gene=st.text_input("Enter valid gene symbol", value="EGFR")
subject=st.text_input("Enter subject",value="HG00403")

geneResponse=translateGene(gene)
region=geneResponse[0]["build38Coordinates"]

st.write(findSubjectVariants(subject,region))



# Variant NC_000007.14:55174771:GGAATTAAGAGAAGC: (is in CIViC)

#     "build37Coordinates": "NC_000007.13:55086709-55279321",
#     "build38Coordinates": "NC_000007.14:55019016-55211628",


# DATE_COLUMN = 'date/time'
# DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
#          'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

# @st.cache
# def load_data(nrows):
#     data = pd.read_csv(DATA_URL, nrows=nrows)
#     lowercase = lambda x: str(x).lower()
#     data.rename(lowercase, axis='columns', inplace=True)
#     data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
#     return data

# # Create a text element and let the reader know the data is loading.
# data_load_state = st.text('Loading data...')
# # Load 10,000 rows of data into the dataframe.
# data = load_data(10000)
# # Notify the reader that the data was successfully loaded.
# data_load_state.text("Done! (using st.cache)")

# if st.checkbox('Show raw data'):
#     st.subheader('Raw data')
#     st.write(data)

# st.subheader('Number of pickups by hour')
# hist_values = np.histogram(
#     data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
# st.bar_chart(hist_values)

# hour_to_filter = st.slider('hour', 0, 23, 17)  # min: 0h, max: 23h, default: 17h
# filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]
# st.subheader(f'Map of all pickups at {hour_to_filter}:00')
# st.map(filtered_data)
