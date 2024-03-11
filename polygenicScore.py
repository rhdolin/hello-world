import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid
import csv

st.set_page_config(
    page_title="Get Polygenic Score",
    page_icon="random",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("Get Polygenic Score")
st.markdown(" This proof-of-concept app demonstrates the computation of a polygenic score, \
    using [FHIR Genomics Operations](http://build.fhir.org/ig/HL7/genomics-reporting/operations.html) to access a person's entire genome. \
    Enter patient and polygenic score model in the sidebar and click 'Run'. Polygenic score is returned.")
st.markdown("Simplifications include: ")
st.markdown("\
    - We assume wildtype if no variant has been reported at a position within the studied region(s).\n\
    - Imputation / statistical approaches for missing data are deferred for now. We currently assume wildtype for polymorphisms outside the studied region(s).  \n\
    - All scores are the product of germline allele dose (absent=0; heterozygous=1; homozygous=2) x effect_weight. Overall polygenic score is the sum of scores.\n\
    - Proof-of-concept code is not optimized for performance.")

@st.cache
def findSubjectVariants(subject, range):  # use findSubjectSpecificVariants_alt instead if NCBI SPDI services are down
    url = 'https://fhir-gen-ops.herokuapp.com/subject-operations/genotype-operations/$find-subject-variants?subject='+subject+'&ranges='+range+'&includeVariants=true'
    headers = {'Accept': 'application/json'}
    return requests.get(url, headers=headers)

@st.cache
def findSubjectSpecificVariants_alt(subject, variant): # use instead of findSubjectSpecificVariants if NCBI SPDI services are down
    url = 'https://fhir-gen-ops-dev-ca42373833b6.herokuapp.com/subject-operations/genotype-operations/$find-subject-specific-variants?subject='+subject+'&variants='+variant+'&includeVariants=true'
    headers = {'Accept': 'application/json'}
    return requests.get(url, headers=headers)

@st.cache
def findSubjectSpecificVariants(subject, variant):
    url = 'https://fhir-gen-ops.herokuapp.com/subject-operations/genotype-operations/$find-subject-specific-variants?subject='+subject+'&variants='+variant+'&includeVariants=true'
    headers = {'Accept': 'application/json'}
    return requests.get(url, headers=headers)

@st.cache
def getPolygenicScoreMetadata(pgs_id):
    url = 'https://www.pgscatalog.org/rest/score/'+pgs_id
    headers = {'Accept': 'application/json'}
    return requests.get(url, headers=headers)

def populatePolygenicScoreModels():
    with open('data/polygenicScore.csv') as polygenicScoreFile:
        polygenicScores = csv.reader(polygenicScoreFile, delimiter=',', quotechar='"')
        pgs_id_list = []
        pgs_name_list = []
        GRCh37_SPDI_list = []
        effect_weight_list = []
        for item in polygenicScores:
            if item[0] != "pgs_id":
                pgs_id_list.append(item[0])
                pgs_name_list.append(item[1])
                GRCh37_SPDI_list.append(item[3])
                effect_weight_list.append(item[10])
    polygenicScoreModels = [pgs_id_list, pgs_name_list, GRCh37_SPDI_list, effect_weight_list]
    return polygenicScoreModels

polygenicScoreModels = populatePolygenicScoreModels()

with st.sidebar:
    subject = st.selectbox("Enter patient ID", ["HG00403","HG00406","HG02657","NA18498","NA18499","NA18870","NA18871","NA19190","NA19210","NA19238","NA19239","NA19240","HG00403","HG00406","HG02657","NA18498","NA18499","NA18870","NA18871","NA19190","NA19210","NA19238","NA19239","NA19240"])
    unique_pgs_id_list = []
    for item in polygenicScoreModels[0]:
        if item not in unique_pgs_id_list:
            unique_pgs_id_list.append(item)
    pgs_id = st.selectbox("Select polygenic score model", unique_pgs_id_list)
    showPolygenicScoreMetadata=st.checkbox("Show Polygenic Score Metadata")
    showPolygenicScoreModel=st.checkbox("Show Polygenic Score Model")

if st.sidebar.button("Run"):
    itemNumber = 0
    results_table = []
    total_score = 0
    for item in polygenicScoreModels[0]:
        GRCh37_SPDI = polygenicScoreModels[2][itemNumber]
        effect_weight = float(polygenicScoreModels[3][itemNumber])
        if item == pgs_id:
            if GRCh37_SPDI.split(":")[2]!=GRCh37_SPDI.split(":")[3]: # effect allele is not wildtype
                variant = findSubjectSpecificVariants(subject,GRCh37_SPDI) # returns an error if NCBI SPDI services are down
                # variant = findSubjectSpecificVariants_alt(subject,GRCh37_SPDI)
                # st.write(variant.json())
                if variant.json()["parameter"][0]["part"][1]["valueBoolean"]==False: 
                    dose=0
                    score=0
                    total_score = total_score + score
                    results_table.append({"allele":GRCh37_SPDI,"dose":dose,"effect_weight":effect_weight,"score":score})
                else:
                    for j in variant.json()["parameter"][0]["part"][2]["resource"]["component"]:
                        if j["code"]["coding"][0]["code"] == "53034-5":
                            allelicStateCode = j["valueCodeableConcept"]["coding"][0]["code"]                       
                            allelicStateDisplay = j["valueCodeableConcept"]["coding"][0]["display"]
                            if allelicStateCode == "LA6706-1":
                                dose=1
                                score=dose * effect_weight
                                results_table.append({"allele":GRCh37_SPDI,"dose":dose,"effect_weight":effect_weight,"score":score})
                                total_score = total_score + score
                            elif allelicStateCode == "LA6705-3":
                                dose=2
                                score=dose * effect_weight
                                results_table.append({"allele":GRCh37_SPDI,"dose":dose,"effect_weight":effect_weight,"score":score})
                                total_score = total_score + score
                            else:
                                dose="undefined"
                                score="undefined"
                                results_table.append({"allele":GRCh37_SPDI,"dose":"undefined","effect_weight":effect_weight,"score":"undefined"})
            else: # effect allele is wildtype
                refSeq = GRCh37_SPDI.split(":")[0]
                position = GRCh37_SPDI.split(":")[1]
                variant = findSubjectVariants(subject,refSeq+":"+position+"-"+position)
                if variant.json()["parameter"][0]["part"][1]["valueBoolean"]==False: # no variant found, thus homozygous wildtype
                    dose=2
                    score=dose * effect_weight
                    results_table.append({"allele":GRCh37_SPDI,"dose":dose,"effect_weight":effect_weight,"score":score})
                    total_score = total_score + score
                else:
                    for j in variant.json()["parameter"][0]["part"][2]["resource"]["component"]:
                        if j["code"]["coding"][0]["code"] == "53034-5":
                            allelicStateCode = j["valueCodeableConcept"]["coding"][0]["code"]                       
                            allelicStateDisplay = j["valueCodeableConcept"]["coding"][0]["display"]
                            if allelicStateCode == "LA6706-1":
                                dose=1
                                score=dose * effect_weight
                                results_table.append({"allele":GRCh37_SPDI,"dose":dose,"effect_weight":effect_weight,"score":score})
                                total_score = total_score + score
                            elif allelicStateCode == "LA6705-3":
                                dose=0
                                score=dose * effect_weight
                                results_table.append({"allele":GRCh37_SPDI,"dose":dose,"effect_weight":effect_weight,"score":score})
                                total_score = total_score + score
                            else:
                                dose="undefined"
                                score="undefined"
                                results_table.append({"allele":GRCh37_SPDI,"dose":"undefined","effect_weight":effect_weight,"score":"undefined"})
        itemNumber = itemNumber + 1

    st.table(data=results_table) 
    st.markdown(f"**Polygenic score**: {total_score:.6f}")

    if showPolygenicScoreMetadata:
        st.subheader("Polygenic Score Metadata")
        st.write(getPolygenicScoreMetadata(pgs_id).json())
   
    if showPolygenicScoreModel:
        polygenicModelFile = "data/" + pgs_id + ".txt"
        polygenicModel = open("data/"+ pgs_id + ".txt","r")
        fileContents=""
        for item in polygenicModel:
            fileContents=fileContents+item
        st.subheader("Polygenic Score Model")
        st.text(fileContents)