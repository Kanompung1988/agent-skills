# Evidence, rule semantics and boundaries

## What is checked
Normalized names (PEP 503 style), strict list values, valid PEP 508 requirements using PyPA packaging, include-group object shape, normalized target lookup and acyclic include graphs.

## What is not checked
Does not install packages, resolve versions, inspect package registries, install from requirements files, or compare lockfiles. Invalid input values are not echoed, since dependency URLs can contain credentials. A clean report does not establish compatible dependencies.

A static finding is a request for human review, not automatically a defect.

## Primary documentation
1. https://packaging.python.org/en/latest/specifications/dependency-groups/
2. https://peps.python.org/pep-0735/
3. https://packaging.pypa.io/en/stable/requirements.html
