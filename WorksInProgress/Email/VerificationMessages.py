createAccount_subject = "Verify account creation"
createAccount_body = """
You are receiving this email because this email was used to register a new account.
${newline}
To confirm this action issue the following command on the server in-game.
#verify ${userEmail} ${verificationCode}
${newline}
If you didn't request this action, then this email may be safely ignored.
However, you probably should track down who is using your email to register for stuff.
${newline}
We will never sell, trade or otherwise distribute your information without prior consent.
Contact ${administrativeEmail} with questions or concerns.
"""

changeAccountKey_subject = "Verify account key change"
changeAccountKey_body = """
You are receiving this email because you or someone logged in as you issued the #changekey command.
${newline}
To confirm this action issue the following command on the server in-game.
#verify ${userEmail} ${verificationCode}
${newline}
If you didn't request this action, then this email may be safely ignored.
However, you probably should track down how your server account was compromised.
${newline}
We will never sell, trade or otherwise distribute your information without prior consent.
Contact ${administrativeEmail} with questions or concerns.
"""

deleteAccount_subject = "Verify account deletion"
deleteAccount_body = """
You are receiving this email because you or someone logged in as you.
Issued the #unregister command.
${newline}
To confirm this action issue the following command on the server in-game.
#verify ${userEmail} ${verificationCode}
${newline}
If you didn't request this action, then this email may be safely ignored.
However, you probably should track down how your account was compromised.
${newline}
Please let us know how we could have improved the servers.
${newline}
We will never sell, trade or otherwise distribute your information without prior consent.
Contact ${administrativeEmail} with questions or concerns.
"""

createAccount_feedback_subject = "Account created - Login Instructions"
createAccount_feedback_body = """
You have successfully created an account.
${newline}
Add the following to your auth.cfg file
authkey ${userEmail} ${privateKey} ${domain}
${newline}
And add this to your autoexec.cfg file
autoauth 1
${newline}
Your public auth key is below and should be kept for your records.
${publicKey}
${newline}
We will never sell, trade or otherwise distribute your information without prior consent.
Contact ${administrativeEmail} with questions or concerns.
"""

changeAccountKey_feedback_subject = "Key changed - Login Instructions"
changeAccountKey_feedback_body = """
You have successfully changed your auth login key.
${newline}
Add the following to your auth.cfg file
authkey ${userEmail} ${privateKey} ${domain}
${newline}
And add this to your autoexec.cfg file
autoauth 1
${newline}
Your public auth key is below and should be kept for your records.
${publicKey}
${newline}
We will never sell, trade or otherwise distribute your information without prior consent.
Contact ${administrativeEmail} with questions or concerns.
"""

deleteAccount_feedback_subject = "Account deleted"
deleteAccount_feedback_body = """
You have successfully deleted your account.
${newline}
We will never sell, trade or otherwise distribute your information without prior consent.
Contact ${administrativeEmail} with questions or concerns.
"""

AccountMessages = {
					'createAccount_subject': ('Create verification subject', createAccount_subject, 'Subject of create account verification email.'),
					'createAccount_body': ('Create verification body', createAccount_body, 'Body of create account verification email.'),
					'changeAccountKey_subject': ('Change verification subject', changeAccountKey_subject, 'Subject of key change verification email.'),
					'changeAccountKey_body': ('Change verification body', changeAccountKey_body, 'Body of key change verification email.'),
					'deleteAccount_subject': ('Delete verification subject', deleteAccount_subject, 'Subject of delete account verification email.'),
					'deleteAccount_body': ('Delete verification body', deleteAccount_body, 'Body of delete account verification email.'),
					
					'createAccount_feedback_subject': ('Login instructions subject', createAccount_feedback_subject, 'Subject of create account feedback email.'),
					'createAccount_feedback_body': ('Login instructions body', createAccount_feedback_body, 'Body of create account feedback email.'),
					'changeAccountKey_feedback_subject': ('Login instructions subject', changeAccountKey_feedback_subject, 'Subject of change account key feedback email.'),
					'changeAccountKey_feedback_body': ('Login instructions body', changeAccountKey_feedback_body, 'Body of change account key feedback email.'),
					'deleteAccount_feedback_subject': ('Login instructions subject', deleteAccount_feedback_subject, 'Subject of delete account feedback email.'),
					'deleteAccount_feedback_body': ('Login instructions body', deleteAccount_feedback_body, 'Body of delete account feedback email.'),
					}