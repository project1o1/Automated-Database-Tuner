# CREATE TABLE users (
#     user_id INT PRIMARY KEY,
#     username VARCHAR(50) NOT NULL,
#     email VARCHAR(100) UNIQUE,
#     password VARCHAR(100) NOT NULL,
#     first_name VARCHAR(50),
#     last_name VARCHAR(50),
#     age INT
#    

# );


import random
with open("text.txt", "w") as file:
    alphas = ["user_id", "username", "email", "password", "first_name", "last_name", "age"]
    print("Writing")
    for i in range(1_000_00):
        s=set()
        j=0
        v=random.randint(1, 6)
        while j<v:
            c=random.choice(alphas)
            if c not in s:
                s.add(c)
                file.write(c)
                if j!=v-1:
                    file.write("-")
                j+=1
            else:
                continue
        file.write(" ")
    print("Done")