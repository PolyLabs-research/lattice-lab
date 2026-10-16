"""lattice-lab: a law-discovery loop over LatticeLife experiments and Kepler fits.

    from lattice_lab.question import Question
    from lattice_lab.experiment import LatticeExperimenter
    from lattice_lab.ledger import Ledger
    from lattice_lab.loop import ask

    question = Question.from_toml("questions/settling-time-hexagon-B2S34.toml")
    outcome = ask(question, LatticeExperimenter(question, "lab/records/q.jsonl"),
                  Ledger("lab/ledger.jsonl"), records_file="records/q.jsonl")

See `loop` for the steps, `analysis` for the statistics, `ledger` for the record and its order
check, and docs/design.md for the architecture.
"""

__version__ = "0.1.0"
