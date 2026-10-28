"""The factory's tests run against an installed engine (oto-kg) and this repository's own pack: the
engine finds the factory-run ontology, with its code, under ontology/ here, as it would under an
installed plugin, and the tests import that code the way the engine will put it on the path."""
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["OTO_ONTOLOGIES"] = os.path.join(HERE, "ontology")
CODE = os.path.join(HERE, "ontology", "factory-run", "code")
if CODE not in sys.path:
    sys.path.insert(0, CODE)
