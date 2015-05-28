Orgdoc 0.1.0
============

0. OBJECTIVE

	0. Sign organization documents.

	0. Verify if everybody signed organization documents.

0. INSTALLING

	0. Install python setuptools.

		>  # apt-get install python-setuptools

	0. Install orgdoc using setuptools.

		>  # python setup.py install

	0. Create a directory named pubkeys on repository root (if you don't have a documents directory, create one).

		> $ cd PATH_TO_DOCUMENTS_DIRECTORY
		> $ mkdir pubkeys

0. USING

	0. To sign a document, run odsign.

		> $ odsign document.txt
	
		0. If you don't have a keys pair, it will be created in the pubkeys directory.
	
		0. A signature will be created in the signatures directory.
	
	0. To verify if everibody signed the repository documents, run odverify.

		> $ odverify
