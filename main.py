from datetime import datetime
import random
import generator

random.seed(datetime.now().timestamp())

gen = generator.Generator("http://user:pass@ip:port")
if gen.createAccount():
    if gen.verifyPhoneNumber():
        if gen.Set2FA():
            print("Account Created")
            print(gen.recoveryCodes)
