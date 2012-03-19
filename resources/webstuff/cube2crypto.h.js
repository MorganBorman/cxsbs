
Module.hashstring = function(pwd, hashlen)
{
	var pPwd = Module.allocate(Module.intArrayFromString(pwd), 'i8', Module.ALLOC_STACK);
	var hashlen = hashlen;

	return Module.Pointer_stringify(Module._cube2crypto_hashstring(pPwd, hashlen));
}

Module.hashpassword = function(cn, sessionid, pwd)
{
	var cn = cn;
	var sessionid = sessionid;
	var pPwd = Module.allocate(Module.intArrayFromString(pwd), 'i8', Module.ALLOC_STACK);

	return Module.Pointer_stringify(Module._cube2crypto_hashpassword(cn, sessionid, pPwd));
}

Module.genkeypair = function(seed)
{
	var pSeed = Module.allocate(Module.intArrayFromString(seed), 'i8', Module.ALLOC_STACK);

	var pPrivkey = Module._cube2crypto_genkeypair(pSeed);
	var pPubkey = pPrivkey + 50;

	var key_pair = [Module.Pointer_stringify(pPrivkey), Module.Pointer_stringify(pPubkey)];

	return key_pair;
}

Module.getpubkey = function(privkey)
{
	var pPrivkey = Module.allocate(Module.intArrayFromString(privkey), 'i8', Module.ALLOC_STACK);

	return Module.Pointer_stringify(Module._cube2crypto_getpubkey(pPrivkey));
}

Module.genchallenge = function(pubkey, seed)
{
	var pPubkey = Module.allocate(Module.intArrayFromString(pubkey), 'i8', Module.ALLOC_STACK);
	var pSeed = Module.allocate(Module.intArrayFromString(seed), 'i8', Module.ALLOC_STACK);

	var pChallenge = Module._cube2crypto_genchallenge(pPubkey, pSeed);
	var pAnswer = pChallenge + 51;

	var validation_pair = [Module.Pointer_stringify(pChallenge), Module.Pointer_stringify(pAnswer)];

	return validation_pair;
}

Module.answerchallenge = function(privkey, challenge)
{
	var pPrivkey = Module.allocate(Module.intArrayFromString(privkey), 'i8', Module.ALLOC_STACK);
	var pChallenge = Module.allocate(Module.intArrayFromString(challenge), 'i8', Module.ALLOC_STACK);

	return Module.Pointer_stringify(Module._cube2crypto_answerchallenge(pPrivkey, pChallenge));
}
