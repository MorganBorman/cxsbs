#include "cube.h"

#include <iostream>

void help()
{
	std::cout << "Usage: keygen <password>\n";
}

int main(int argc, char **argv)
{
	if(argc != 2 || !argv[1])
	{
		help();
		return EXIT_FAILURE;
	}
	vector<char> pubkey, privkey;
	genprivkey(argv[1], privkey, pubkey);
	std::cout << "private key:\t" << privkey.getbuf() << "\n";
	std::cout << "public key:\t " << pubkey.getbuf() << "\n";
	return EXIT_SUCCESS;
}

