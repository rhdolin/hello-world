import streamlit as st
import pandas as pd
import requests
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

@st.cache
def findPopulationDxImplications(conditionCode):
	url='https://fhir-gen-ops.herokuapp.com/population-operations/phenotype-operations/$find-population-dx-implications?conditions='+conditionCode+'&includePatientList=true'
	headers={'Accept': 'application/json'}
	r=requests.get(url, headers=headers)
	return r.json()

@st.cache
def findSubjectDxImplications(subject, conditionCode):
	url='https://fhir-gen-ops.herokuapp.com/subject-operations/phenotype-operations/$find-subject-dx-implications?subject='+subject+'&conditions='+conditionCode
	headers={'Accept': 'application/json'}
	r=requests.get(url, headers=headers)
	return r.json()

resultList=[]
patientList=[]
conditionList=[]
clinSigList=[]
evidenceList=[]
variantList=[]

st.title("Genetic Screening")

condition=st.selectbox("This application screens a poplulation for selected condition.",(    	
		'Familial hypercholesterolemia',
		'Hereditary Breast and Ovarian Cancer Syndrome',
		'Hereditary Paraganglioma-Pheochromocytoma Syndrome',
		'Hypertrophic cardiomyopathy',
		'Lynch syndrome',
		'Multiple endocrine neoplasia',
		'Peutz-Jeghers syndrome'))

if condition=="Familial hypercholesterolemia": conditionCode="https://www.ncbi.nlm.nih.gov/medgen|C0020445"
elif condition=="Hereditary Breast and Ovarian Cancer Syndrome": conditionCode="https://www.ncbi.nlm.nih.gov/medgen|C0677776"
elif condition=="Hereditary Paraganglioma-Pheochromocytoma Syndrome": conditionCode="https://www.ncbi.nlm.nih.gov/medgen|C1708353"
elif condition=="Hypertrophic cardiomyopathy": conditionCode="https://www.ncbi.nlm.nih.gov/medgen|C0878544"
elif condition=="Lynch syndrome": conditionCode="https://www.ncbi.nlm.nih.gov/medgen|C4552100"
elif condition=="Multiple endocrine neoplasia": conditionCode="https://www.ncbi.nlm.nih.gov/medgen|C0027662"
elif condition=="Peutz-Jeghers syndrome": conditionCode="https://www.ncbi.nlm.nih.gov/medgen|C0031269"

# Hemochromatosis
# https://www.ncbi.nlm.nih.gov/medgen|C3469186

for i in findPopulationDxImplications(conditionCode)["parameter"][0]["part"]:
	if i["name"]=="subject":
		resultList.append(i["valueString"])

for i in resultList:
	dxImplications=findSubjectDxImplications(i, conditionCode)
	for j in dxImplications["parameter"]:
		patientList.append(i)
		for k in j["part"]:
			if k["name"] == "implication":
				# extract condition, clinical significance, evidence
				for l in k["resource"]["component"]:
					if l["code"]["coding"][0]["code"]=="53037-8":
						try: 
							clinSigList.append(l["valueCodeableConcept"]["coding"][0]["display"])
						except KeyError: 
							clinSigList.append(l["valueCodeableConcept"]["text"])
					elif l["code"]["coding"][0]["code"]=="81259-4":
						conditionList.append(l["valueCodeableConcept"]["coding"][0]["display"])
					elif l["code"]["coding"][0]["code"]=="93044-6":
						evidenceList.append(l["valueCodeableConcept"]["text"])					
			elif k["name"] == "variant":
				# extract variant
				for l in k["resource"]["component"]:
					if l["code"]["coding"][0]["code"]=="81252-9":
						variantList.append(l["valueCodeableConcept"]["coding"][0]["display"])

AgGrid(pd.DataFrame({
    'Patient': patientList,
    'Condition': conditionList,
    'Variant': variantList,
    'Clinical Significance': clinSigList,
    'Evidence': evidenceList}))

