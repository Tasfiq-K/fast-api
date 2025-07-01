from pydantic import BaseModel

class Address(BaseModel):
    city: str
    Area: str
    pin: str

class Patient(BaseModel):
    
    name: str
    gender: str
    age: int
    address: Address
    
address_dict = {
    'city': 'Dhaka',
    'Area': 'Mirpur',
    'pin': '1216'
}

address_1 = Address(**address_dict)
patient_dict = {
    'name': 'Nanika',
    'gender': 'F',
    'age': 12, 
    'address': address_1
}

patient_1 = Patient(**patient_dict)

# print(patient_1)


temp = patient_1.model_dump()
print(temp)
print(type(temp))