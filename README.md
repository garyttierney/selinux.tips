# selinux.tips

selinux.tips is a book built using Sphinx
(http://www.sphinx-doc.org/en/stable/).  It is hosted at https://selinux.tips/
and will be available as a PDF when it reaches a stable state.

## Requirements

Building the documentation depends on some Python packages.  These can be
installed by running `pip install -r requirements.txt`.

## Building

To generate the documentation run `make html` from the root directory.  This
will output the HTML documentation to build/html/.  It is also useful to
rebuild the documentation as you are making changes to it.  A `watch.sh` script
is included that takes a single argument to pass as a make target.

To rebuild the HTML documentaiton every time a source file is changed run
`./watch.sh html`.

### PDF

In addition to the HTML documentation a PDF can also be generated.  This uses LaTeX
and depends on several texlive packages.  On Fedora you can install:

```
dnf install texlive-framed texlive-wrapfig texlive-titlesec texlive-threeparttable texlive-upquote texlive-eqparbox texlive-multirow texlive-capt-of
```

And use the `latexpdf` make target to build a PDF under build/latexpdf/.
