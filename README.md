---
CXSBS: Canonical eXtensible SauerBraten Server
---
By: Morgan Borman

CXSBS is a total restructuring of the python side of the XSBS project.

XSBS is a great project and I salute Greg Haynes (https://github.com/greghaynes) for the tremendous amount of work he and the others involved in the XSBS project spent to get it to where it is.

That said, design is an iterative process and in working on XSBS I have seen many things which will benefit greatly from this restructuring.

The goals of this restructuring process are as follows:

* Completely modularize the plug-in architecture, turning everything into a plug-in which have version dependencies on each other.
* Canonicalize the plug-in structure to better support advanced operations like reloading server configurations.
* Promote a better documented and more maintainable Sauerbraten server mod.
* Provide a feature complete server for single and multiple instance applications.