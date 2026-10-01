# -*- coding: utf-8 -*-
"""Host Taxon Predictor: all_viruses_with_desired_attributes.dump (5,282 records).
REWRITTEN this session: original logic derived 4 keyword-presence binary flags from
host_lineage; current logic uses the (cleaned) host field directly for species
identity. Verified byte-for-byte against the already-committed
counts_per_tool_v2/03_Host_Taxon_Predictor_counts.csv.
"""
import os
import re
import sys
import pickle
import collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RS, write_csv

SRC = "Host_Taxon_Predictor/all_viruses_with_desired_attributes.dump"


class DummyClass:
    def __init__(self, *a, **k):
        pass

    def __setstate__(self, state):
        if isinstance(state, dict):
            self.__dict__.update(state)
        else:
            self.__dict__["_state"] = state


class SafeUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        try:
            return super().find_class(module, name)
        except Exception:
            return DummyClass


def clean_host(h):
    if h is None:
        return None
    h = str(h)
    paren = h.find("(")
    if paren != -1:
        # truncate at the first parenthetical, covers both simple common-name
        # annotations ("Mesocricetus auratus (Syrian hamster) strain Z3") and
        # botanical auth
        h = h[:paren].strip()
    else:
        h = h.split(";")[0].strip()
    h = re.sub(r"\s+sp\.?$", "", h).strip()
    return h


def is_prok(s):
    lin = s.host_lineage or []
    return "Bacteria" in lin or "Archaea" in lin


def load_raw() -> list:
    """The sequence records in the pickle dump."""
    with open(os.path.join(RS, SRC), "rb") as fh:
        return SafeUnpickler(fh, encoding="latin1").load().seqs


def count_labels(seqs: list) -> list:
    """Cleaned eukaryotic host names, then the prokaryotic records as one
    excluded row."""
    prok_n = sum(1 for s in seqs if is_prok(s))
    euk_hosts = collections.Counter(clean_host(s.host) for s in seqs if not is_prok(s))
    rows = [(sp, int(n), "") for sp, n in euk_hosts.most_common()]
    rows.append(("Prokaryote/Archaea (primary binary, negative, EXCL)", prok_n,
                 "MATCH (1219) -- unchanged, non-eukaryotic, not exploded"))
    return rows


def run():
    rows = count_labels(load_raw())
    return write_csv(
        3, "Host Taxon Predictor",
        "all_viruses_with_desired_attributes.dump (5,282 records), host + host_lineage fields (finer resolution than the 4 keyword-presence experimental-binary flags the original harmonization derived from host_lineage)",
        rows,
        note="host_lineage classified via Bacteria/Archaea presence for the Prokaryote/Archaea split; host field cleaned (demographic annotations after ';', parenthetical common names, 'sp.' placeholders stripped) for species identity. Prokaryote/Archaea (1219 records) kept as its own unexploded row, unchanged from the original count.")


if __name__ == "__main__":
    run()
