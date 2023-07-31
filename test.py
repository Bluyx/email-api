import httpx

# change 'http://127.0.0.1:3333' to your API URL once you have set it up

def createEmail(email, password): # you better keep the passwords of all the accounts here same to access them later easily
    # email: the email you want to create
    # password: the password for the email
    return httpx.post("http://mail.qwmail.xyz/create_email", data={"email": email, "password": password}).json()

def getVerification(email, password, sender, verification_location, imap):
    # email: the email used in createEmail
    # password: the password used in createEmail
    # sender: the email that sent the verification message, for example "noreply@email.kick.com" (you can set it to "ALL")
    # verification_location: the location of the verification ["subject", "body"]
    # imap: your imap domain, for example "mail.example.com"
    return httpx.post("http://mail.qwmail.xyz/get_verification", data = {
        "email": email,
        "password": password,
        "sender": sender,
        "verification_location": verification_location,
        "imap": imap
    }).json()



print(createEmail("user@example.com", "myPassword"))

print(getVerification(email="user@example.com", password="myPassword", sender="ALL", verification_location="subject", imap="mail.example.com"))