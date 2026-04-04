import json 
import random
import string
from pathlib import Path

class Bank:

    def createaccount(self):
        pass
user = Bank()
print("1 for creating an account")
print("2 for for depositing money in the bank")
print("3  for for withdrawing the mone")
print("4  for details")
print("5 for updating the details")
print("6 for deleting the account")


check = int(input("enter your response: "))

if check == 1:
    user.Createaccount()