# PEP 660 metadata parity

The core distribution metadata of a PEP 660 editable wheel should match the regular wheel except additional dependencies essential for the editable mechanism; the wheel compatibility tags may differ. Editable wheels must not be cached or distributed. This CLI uses only local archives and compares Requires-Dist textually; validate runtime imports separately.

https://peps.python.org/pep-0660/
