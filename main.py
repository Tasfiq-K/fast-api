from fastapi import FastAPI, Path, HTTPException, Query 
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

app = FastAPI()



class Patient(BaseModel):
    
    id: Annotated[str, Field(..., description='ID of the Patient', examples=['P001'])]
    name: Annotated[str, Field(..., description='Name of the patient')]
    city: Annotated[str, Field(..., description="Patient's living city")]
    age: Annotated[int, Field(..., gt=0, lt=120, descriptions="Age of the patient")]
    gender: Annotated[Literal['Male', 'Female', 'others'],
                    Field(..., descriptions="Gender of the patient")]
    height: Annotated[float, Field(...,  gt=0, description="Height of the patient in (M)")]
    weight: Annotated[float, Field(..., gt=0, descriptions="Weight of the patient (Kg)")]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight / (self.height ** 2), 2)
        return bmi
    
    @computed_field
    @property
    def verditc(self) -> str:
        
        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Normal'
        else:
            return 'Obese'

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['Male', 'Female']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]

def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)

    return data

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)

@app.get("/")
def hello():
    return {'message': 'Patient management system API'}

@app.get('/about')
def about():
    return {
        'message': "A fully functional API to manage your patient records" 
    }

@app.get("/view")
def view():
    data = load_data()

    return data

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(..., description='Id of the patient in DB', example='P001')):
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    
    # return {'error': 'Patient Not Found'}
    raise HTTPException(status_code=404, detail='Patient Not Found')

@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description='Sort on the basis on height, weight or BMI'),
                   order: str = Query('asc', description='sort in asc or desc order')):
    valid_fields = ['height', 'weight', 'bmi']
    
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400,
                             detail=f'invalid field selected from {valid_fields}')

    if order not in ['asc', 'desc']:
        raise HTTPException(
            status_code=400,
            detail=f'invalide order selection between asc and desc'
        )

    data = load_data()
    sort_order = True if order == 'desc' else False
    sorted_data = sorted(
        data.values(),
        key=lambda x: x.get(sort_by, 0),
        reverse=sort_order
    )

    return sorted_data

@app.post('/create')
def create_patient(patient: Patient):

    # load existing data
    data = load_data()

    # check if patient already exists
    if patient.id in data:
        raise HTTPException(
            status_code=400,
            detail='Patient already exists'
        )
    data[patient.id] = patient.model_dump(
        exclude=['id']
    )

    return JSONResponse(
       status_code=201,
       content={'message': 'Patient created successfully'}
   ) 
@app.put('/update/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):
    data = load_data()
    
    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    existing_patient_info = data[patient_id]

    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value
    
    existing_patient_info['id'] = patient_id
    patient_pyd_obj = Patient(**existing_patient_info)
    patient_pyd_obj.model_dump(exclude='id')

    data[patient_id] = existing_patient_info

    # save data into json file
    save_data(data)

    return JSONResponse(
        status_code=200,
        content={'message': 'Patient Updated'}
    )

@app.delete('delete/{patient_id}')
def delete_patient(patient_id: str):
    # load data
    data = load_data()

    if patient_id not in data:
        raise HTTPException(
            status_code=404,
            detail='Patient not found'
        )
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(
        status_code=200,
        content={'message': "Patient Deleted"}
    )