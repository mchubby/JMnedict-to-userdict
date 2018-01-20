# JMnedict-to-userdict

Place `JMnedict.xml` in the current working directory, then run `JMnedict-to-userdict.py`. 

Optional arguments are:

`-o, --output`    OUTPUT kuromoji-compatible CSV userdict target file. Default: `JMnedict.csv`

`-i, --include`   Comma-separated list of JMnedict entry types to include (DTD entities).
                  Example: `surname,masc,fem,given`
                  Default: do not filter out any entry

