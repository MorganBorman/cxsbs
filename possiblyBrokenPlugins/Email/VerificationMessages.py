create_verification_subject = "Verify account creation"
create_verification_body = """
You are receiving this email because this email was used to register a new account on the ${serverClusterName} servers.
Issued the #register command on ${serverName} at ${initiatedTime}

To confirm this action issue the following command on any of the ${serverClusterName} servers.
#validate ${userName} ${verificationCode}

If you didn't request this action, then this email may be safely ignored. The verification will timeout at ${expirationTime}.
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
Has successfully changed the login auth key on ${serverName} at ${initiatedTime}.

You can now login on any ${serverClusterName} server by placing the following .
#validate ${userName} ${verificationCode}



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