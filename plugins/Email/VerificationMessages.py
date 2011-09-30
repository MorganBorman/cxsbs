create_verification_subject = "Verify account creation"
create_verification_body = """
You are receiving this email because this email was used to register a new account on the ${serverClusterName} servers.
Issued the #register command on serverName at ${initiatedTime}.

To confirm this action issue the following command on any of the ${serverClusterName} servers.
#verify ${userName} ${verificationCode}

If you didn't request this action, then this email may be safely ignored. The verification will timeout at expirationTime.
However, you probably should track down who is using your email to register for stuff.

Welcome to the ${serverClusterName} servers.

We will never sell, trade or otherwise distribute your information without prior consent.
Contact ${administrativeEmail} with questions or concerns.
"""

change_verification_subject = "Verify account key change"
change_verification_body = """
You are receiving this email because you or someone logged in as you.
Issued the #changekey command on ${serverName} at ${initiatedTime}

To confirm this action issue the following command on any ${serverClusterName} server.
#validate ${userName} ${verificationCode}
	
If you didn't request this action, then this email may be safely ignored. The verification will timeout at ${expirationTime}.
However, you probably should track down how your account was compromised.

Please let us know how we can improve the ${serverClusterName} servers.

We will never sell, trade or otherwise distribute your information without prior consent.
Contact ${administrativeEmail} with questions or concerns.
"""

login_instructions_subject = "Login Instructions"
login_instructions_body = """
You are receiving this email because you or someone logged in as you.
Has successfully changed the login auth key to the account tied to this email at ${initiatedTime}.

You will be automatically logged in on any ${serverClusterName} server if you place the following in your auth.cfg file;
authkey ${userName} ${privateKey} ${domain}
And place the following in your autoexec.cfg file;
autoauth 1

Your public auth key is below and should be kept for your records.
${publicKey}

We will never sell, trade or otherwise distribute your information without prior consent.
Contact ${administrativeEmail} with questions or concerns.
"""

delete_verification_subject = "Verify account deletion"
delete_verification_body = """
You are receiving this email because you or someone logged in as you.
Issued the #unregister command on ${serverName} at ${initiatedTime}

To confirm this action issue the following command on any ${serverClusterName} server.
#validate ${userName} ${verificationCode}

If you didn't request this action, then this email may be safely ignored. The verification will timeout at ${expirationTime}.
However, you probably should track down how your account was compromised.

Please let us know how we could have improved the ${serverClusterName} servers.

We will never sell, trade or otherwise distribute your information without prior consent.
Contact ${administrativeEmail} with questions or concerns.
"""

verificationMessages = {
					'create_verification_subject': ('Create verification subject', create_verification_subject, 'Subject of create account verification email.'),
					'create_verification_body': ('Create verification body', create_verification_body, 'Body of create account verification email.'),
					'change_verification_subject': ('Change verification subject', change_verification_subject, 'Subject of key change verification email.'),
					'change_verification_body': ('Change verification body', change_verification_body, 'Body of key change verification email.'),
					'login_instructions_subject': ('Login instructions subject', login_instructions_subject, 'Subject of login instructions email.'),
					'login_instructions_body': ('Login instructions body', login_instructions_body, 'Body of login instructions email.'),
					'delete_verification_subject': ('Delete verification subject', delete_verification_subject, 'Subject of delete account verification email.'),
					'delete_verification_body': ('Delete verification body', delete_verification_body, 'Body of delete account verification email.'),
					}