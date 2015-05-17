# scholarpy

A scholarly literature crawler. Let’s fetch some free scholar data!

## arXiv

This handles [arXiv](http://arxiv.org) (meta)data crawling in a 'play nice' way.

From [OAI help](http://arxiv.org/help/oa/index)

> Metadata for arXiv articles may be reused in non-commercial and commercial systems.

The purpose of crawling this data could be to allow easier use of the API by:

* allowing finer grained requests
* no drastic throttling
* json response


### Official arXiv documentation

* http://arxiv.org/help/bulk_data_s3 for data stored on AWS S3 (need specific s3cmd version to pass the 'requester as payer' flag)
* http://indico.cern.ch/event/a01193/session/3/contribution/s4t5/material/1/2.pdf useful to have an overview of OAI for arXiv
* http://arxiv.org/help/api/examples/python_arXiv_parsing_example.txt for python sample code


## Other useful links for scholar material

* list of journals:
    * ftp://ftp.ncbi.nih.gov/pubmed/J_Entrez.txt
    * http://ip-science.thomsonreuters.com/cgi-bin/jrnlst/jlresults.cgi
* list of publishers:
    * (open access) http://scholarlyoa.com/publishers/
    * (closed access) http://wokinfo.com/mbl/publishers/
* crossref (for reference 'bibentry' search) https://github.com/CrossRef/rest-api-doc/blob/master/rest_api.md
* sherpa: http://www.sherpa.ac.uk/romeo/faq.php?la=en&fIDnum=|&mode=simple#reuse (list journals licenses and publishers)
