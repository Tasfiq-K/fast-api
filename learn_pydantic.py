from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator, computed_field
from typing import List, Dict, Optional, Annotated

class Patient(BaseModel):
    # name: str = Field(max_length=50) # maximum character length should be 50
    name: Annotated[str,
                     Field(max_length=50,
                        title='Name of the patient',
                        description='Name should be within 50 charas'
                    )
                ]
    age: int = Field(gt=0, lt=120) # age should be in between 0 and 120
    email: EmailStr
    weight: float = Field(gt=0) # constraining the weight, should be greater than 0
    height: float = Field(gt=0)
    married: bool = False
    allergies: Annotated[Optional[List[str]], Field(default=None, max_length=5)]
    contact_details: Dict[str, str]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight / (self.height ** 2), 2)
        return bmi

    # field validation
    @field_validator('email')
    @classmethod
    def email_validator(cls, value):
        valid_domains = ['nasir.com', 'syntax.com']
        domain_name = value.split('@')[-1]
        
        if domain_name not in valid_domains:
            raise ValueError('Not a valid domain')
        
        return value
    
    # transformation
    # suppose we want the user name in all CAPS

    @field_validator('name')
    @classmethod
    def transform_name(cls, value):
        return value.upper()

    # model validator works on the whole 
    # pydantic model
    @model_validator(mode='after')
    def validate_emergency_contacts(cls, model):
        if model.age > 60 and 'emergency' not in model.contact_details:
            raise ValueError(f'Patients older than age of 60 must have an emergency number')
        return model

def update_patient_data(patient: Patient):
    print(patient.name)
    print(patient.age)
    print(patient.email)
    print(patient.weight)
    print(patient.bmi)
    print(patient.allergies)
    print(patient.married)

patient_info = {
    'name': "Nanika",
    'age': '70',
    'email': 'nanika@nasir.com',
    'allergies': ['Dust', 'Duck'],
    'weight': 10,
    'height': .9,
    'married': False,
    'contact_details': {'email': "nanika#hxh.com", "phone": "000x00", 'emergency': '123321'} 
}
patient1 = Patient(**patient_info)
update_patient_data(patient1)
