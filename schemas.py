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
    pass


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_file: str | None
    image_path: str




# <----------Schema for Post (Base, Responses, creations)-------------->

class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)

# The best practice is to use another class that inherits from the base model.
# this helps for more flexibility
class PostCreate(PostBase):
    user_id: int # Temporary

# this helps to return a post response with more data as id and date
class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date_posted: datetime
    author: UserResponse  