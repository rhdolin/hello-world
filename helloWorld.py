import streamlit as st
import numpy as np
import pandas as pd
import requests
import random
from st_aggrid import JsCode, GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

df=pd.read_csv('data/product.csv')

gb=GridOptionsBuilder.from_dataframe(df)


gb.configure_default_column(
	resizable=True,
	filterable=True,
	sorteable=True,
	editable=True)

gb.configure_pagination(
	enabled=True
	)

gb.configure_column("ING",
	header_name="ING",
	cellRenderer=JsCode(""" 
		function (params) 
		{return '<a target="_blank" href="https://api.pharmgkb.org/v1/infobutton?mainSearchCriteria.v.c='+params.value+'">'+params.value+'</a>'}
		""").js_code,
	)
go=gb.build()

AgGrid(df, gridOptions=go, allow_unsafe_jscode=True)
