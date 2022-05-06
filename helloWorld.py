import streamlit as st
import pandas as pd
import requests
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

@st.cache
def findPopulationDxImplications():
	url='https://fhir-gen-ops.herokuapp.com/population-operations/phenotype-operations/$find-population-dx-implications?conditions=https://www.ncbi.nlm.nih.gov/medgen|C0677776,https://www.ncbi.nlm.nih.gov/medgen|C4552100,https://www.ncbi.nlm.nih.gov/medgen|C0020445&includePatientList=true'
	headers={'Accept': 'application/json'}
	r=requests.get(url, headers=headers)
	return r.json()

@st.cache
def findSubjectDxImplications(subject):
	url='https://fhir-gen-ops.herokuapp.com/subject-operations/phenotype-operations/$find-subject-dx-implications?subject='+subject+'&conditions=https://www.ncbi.nlm.nih.gov/medgen|C0677776,https://www.ncbi.nlm.nih.gov/medgen|C4552100,https://www.ncbi.nlm.nih.gov/medgen|C0020445'
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
st.write("This application screens a population for CDC Tier 1 conditions.")

for i in findPopulationDxImplications()["parameter"][0]["part"]:
	if i["name"]=="subject":
		resultList.append(i["valueString"])

for i in resultList:
	dxImplications=findSubjectDxImplications(i)
	for j in dxImplications["parameter"]:
		patientList.append(i)
		for k in j["part"]:
			if k["name"] == "implication":
				# parse condition, clinical significance, evidence
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
				# parse variant
				for l in k["resource"]["component"]:
					if l["code"]["coding"][0]["code"]=="81252-9":
						variantList.append(l["valueCodeableConcept"]["coding"][0]["display"])

outputTable=pd.DataFrame({
    'Patient': patientList,
    'Condition': conditionList,
    'Variant': variantList,
    'Clinical Significance': clinSigList,
    'Evidence': evidenceList})
AgGrid(outputTable)

