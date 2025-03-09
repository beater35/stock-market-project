# from flask_mail import Message
# from itsdangerous import URLSafeTimedSerializer
# from flask import url_for
# from . import mail, app  

# s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# def send_reset_email(user):
#     token = s.dumps(user.email, salt='password-reset-salt')
#     reset_link = url_for('reset_password', token=token, _external=True)
    
#     msg = Message('Password Reset Request', recipients=[user.email])
#     msg.body = f'''To reset your password, click the following link:
# {reset_link}
# If you did not request this, ignore this email.
# '''
#     mail.send(msg)
