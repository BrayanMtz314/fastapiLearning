from pydantic import BaseModel, ConfigDict, Field, EmailStr
from datetime import datetime

# BaseModel is the base that all out pydantic model and error from
# Field Lets us to add constrain like minimun and maximun link
#  ConficDict is the modern  way to configure models



# <------User schemas for User (Base, For responses and creations)------>
class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    image_file: str | None
    image_path: str

class UserPrivate(UserPublic):
    email: EmailStr


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)
    image_file: str | None = Field(default=None, min_length=1, max_length=200)

class Token(BaseModel):
    access_token: str
    token_type: str


# <----------Schema for Post (Base, Responses, creations)-------------->
 
class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)

# The best practice is to use another class that inherits from the base model.
# this helps for more flexibility
class PostCreate(PostBase):
    user_id: int # Temporary


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, min_length=1)

# this helps to return a post response with more data as id and date
class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date_posted: datetime
    author: UserPublic  


