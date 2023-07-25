from flask import Flask, request, jsonify
import imaplib, email, re, os, pythoncom, win32com.client

# Must install hMailServer & Use cloudflare. change domain nameservers to cloudflare's. Add an A record with your VPS IP. Add MX record for email server.

app = Flask(__name__)

hMailPassword = "1234" # Password used when oppening hMailServer for the first time
domain = "example.com"

@app.route("/")
def index():
    return "Working!"

@app.route("/get_verification", methods=["POST"])
def get_verification():
    try:
        try:
            sender_email = request.form["sender"]
            verification_location = request.form["verification_location"]
            imap = request.form["imap"]
            # verification_type = request.form["verification_type"] # Code | Link # Todo
            imap_obj = imaplib.IMAP4(imap, 143)
            imap_obj.login(request.form["email"], request.form["password"])
        except Exception as err:
            err = str(err)
            if "Invalid user name or password." in err:
                return jsonify({"success": False, "message": "Invalid username or password"})
            elif "socket error: EOF" in err:
                return jsonify({"success": False, "message": "Socket error: EOF"})
            else:
                return jsonify({"success": False, "message": "Unexpected error"})

        imap_obj.select("INBOX")
        if sender_email == "ALL":
            search_criteria = "ALL"
        else:
            search_criteria = f'(FROM "{sender_email}")'
        status, msg_ids = imap_obj.search(None, search_criteria)
        msg_ids = msg_ids[0].decode("utf-8").split()
        msg_ids = [int(msg_id) for msg_id in msg_ids]
        if len(msg_ids) == 0:
            return jsonify({"success": False, "message": "Message not found"})
        last_msg_id = msg_ids[-1]
        status, msg_data = imap_obj.fetch(str(last_msg_id), "(BODY.PEEK[])")
        email_msg = email.message_from_bytes(msg_data[0][1])
        if verification_location == "body":
            if email_msg.is_multipart():
                for part in email_msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        respp = part.get_payload(decode=True).decode()
                        break
            else:
                respp = email_msg.get_payload(decode=True).decode()
        elif verification_location == "subject": respp = email_msg["Subject"]
        else: imap_obj.logout(); return jsonify({"success": False, "error": "invalid option at 'verification_location'"})
        imap_obj.logout()
        return jsonify({"success": True, "response": respp})
    except Exception as err:
        print("Error: " + str(err))
        pass

@app.route("/create_email", methods=["POST"])
def create_email():
    try:
        hmailserver = win32com.client.Dispatch("hMailServer.Application", pythoncom.CoInitialize())
        hmailserver.Authenticate("Administrator", hMailPassword)
        hmailserver.Connect()
        account = hmailserver.Domains.ItemByName(domain).Accounts.Add()
        username = request.form["username"]
        account.Address = username
        account.Password = request.form["password"]
        account.Active = True
        account.Save()
        return jsonify({"success": False, "message": "Account Created", "account": username})
    except Exception as err:
        if "same name already exists" in str(err): return jsonify({"success": False, "message": "Same name already exists"})
        else: print(str(err)); return jsonify({"success": False, "message": "Error"})


if __name__ == "__main__":
    app.run(port=3333)
