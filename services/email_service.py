import random
from flask_mail import Message

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(mail, recipient_email, otp):
    msg = Message("Your OTP for Annaforces Registration",
                    recipients=[recipient_email])
    msg.body = f"Your One-Time Password (OTP) for Annaforces registration is: {otp}\n\nThis OTP is valid for 5 minutes. Do not share it with anyone."
    try:
        mail.send(msg)
        return True, None
    except Exception as e:
        return False, str(e)

def send_welcome_email(mail, recipient_email, name, username):
    msg = Message("Welcome to Annaforces!",
                    recipients=[recipient_email])
    msg.html = f"""
    <html>
        <body>
            <h2>Welcome to Annaforces, {name}!</h2>
            <p>Your account has been successfully created. We are thrilled to have you on board.</p>
            <p>Here are your account details:</p>
            <ul>
                <li><b>Name:</b> {name}</li>
                <li><b>Username:</b> {username}</li>
            </ul>
            <p>You can now log in to your account and start your competitive programming journey.</p>
            <p>Happy coding!</p>
            <br>
            <p>Best regards,</p>
            <p>The Annaforces Team</p>
        </body>
    </html>
    """
    try:
        mail.send(msg)
        return True, None
    except Exception as e:
        return False, str(e)

def send_userid_reminder_email(mail, recipient_email, name, username):
    msg = Message("Your Annaforces Username Reminder",
                    recipients=[recipient_email])
    msg.html = f"""
    <html>
        <body>
            <h2>Annaforces Account Information</h2>
            <p>Hello {name},</p>
            <p>You requested a reminder of your Username. Here is your account information:</p>
            <ul>
                <li><b>Username:</b> {username}</li>
            </ul>
            <p>You can use your Username to log in to your account.</p>
            <p>If you did not request this reminder, you can safely ignore this email.</p>
            <br>
            <p>Best regards,</p>
            <p>The Annaforces Team</p>
        </body>
    </html>
    """
    try:
        mail.send(msg)
        return True, None
    except Exception as e:
        return False, str(e)

def send_password_reset_email(mail, recipient_email, name, otp):
    msg = Message("Annaforces Password Reset OTP",
                    recipients=[recipient_email])
    msg.html = f"""
    <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hello {name},</p>
            <p>You have requested to reset your password for your Annaforces account.</p>
            <p>Your One-Time Password (OTP) for password reset is: <b>{otp}</b></p>
            <p>This OTP is valid for 5 minutes. Do not share it with anyone.</p>
            <p>If you did not request a password reset, please ignore this email.</p>
            <br>
            <p>Best regards,</p>
            <p>The Annaforces Team</p>
        </body>
    </html>
    """
    try:
        mail.send(msg)
        return True, None
    except Exception as e:
        return False, str(e)

def send_password_changed_confirmation_email(mail, recipient_email, name):
    msg = Message("Annaforces Password Changed Confirmation",
                    recipients=[recipient_email])
    msg.html = f"""
    <html>
        <body>
            <h2>Password Changed Successfully</h2>
            <p>Hello {name},</p>
            <p>Your password for your Annaforces account has been successfully changed.</p>
            <p>If you did not make this change, please contact support immediately.</p>
            <br>
            <p>Best regards,</p>
            <p>The Annaforces Team</p>
        </body>
    </html>
    """
    try:
        mail.send(msg)
        return True, None
    except Exception as e:
        return False, str(e)

