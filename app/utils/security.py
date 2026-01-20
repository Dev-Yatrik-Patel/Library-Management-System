from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt 
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY","secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password,hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) )
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


##########################################################################################################################################
# to understand the flow for the jwt tokens 

# data = { "sub" : "1" }
# data.update({"exp":datetime.now() + (None or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) )})

# token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# print(token)

# final_dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

# print('*'*30)
# print(final_dict)

# print(pwd_context.verify("test1234","$2b$12$kIVsVg78Su98CQn41An5KOdazXgL2JO283il7fXZOayX44VmH.PPO"))

##########################################################################################################################################