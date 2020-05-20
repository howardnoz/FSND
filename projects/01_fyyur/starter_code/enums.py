# enums.py
from enum import Enum, auto

class Genre(Enum):
  Alternative = 1
  Blues = 2
  Classical = 3
  Country = 4
  Electronic = 5 
  Folk = 6
  Funk = 7
  Hip_Hop = 8
  Heavy_Metal = 9
  Instrumental = 10
  Jazz = 11
  Musical_Theatre = 12
  Pop = 13
  Punk = 14
  R_AND_B = 15
  Reggae = 16
  Rock_n_Roll = 17
  Soul = 18
  Other = 19
  
  @classmethod
  def choices(cls):
    return [ (choice.name, choice.name) for choice in cls ]
