"""Question files."""

import pytest

from lattice_lab.question import Question, QuestionError, size_of

BASE = {
    "id": "q1",
    "rule": "B2/S34",
    "shape": "hexagon",
    "fit_sizes": [8, 10, 12, 16],
    "heldout_pool": [24, 32],
}


def test_from_toml(tmp_path):
    path = tmp_path / "q.toml"
    path.write_text(
        'id = "q1"\nrule = "B2/S34"\nshape = "hexagon"\nfit_sizes = [16, 8, "10x12", 12]\n'
        'heldout_pool = [24]\nseeds = 5\nnote = "x"\nfuture_key = 3\n'
    )
    q = Question.from_toml(path)
    assert q.fit_sizes == (8, "10x12", 12, 16)  # sorted by cells
    assert q.seeds == 5 and q.extra == {"future_key": 3}
    assert q.rule_text == "B2/S34" and "hexagon" in q.title()
    assert Question.from_dict(q.to_dict()) == q


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"fit_sizes": [8, 9, 10, 12]}, "even width"),
        ({"heldout_pool": [8]}, "both fitted and held out"),
        ({"laws": ["cubic"]}, "unknown laws"),
        ({"rule": "B9/S9x"}, "rule"),
        ({"shape": "triangle", "fit_sizes": [8, 10, 12, 16]}, "triangle_mode"),
        ({"fit_sizes": [8, 10]}, "min_points"),
        ({"id": "has space"}, "id"),
        ({"cap": 100, "max_cap": 50}, "max_cap"),
        ({"space": "loglog"}, "space"),
    ],
)
def test_bad_questions_are_refused(change, message):
    with pytest.raises(QuestionError, match=message):
        Question.from_dict({**BASE, **change})


def test_missing_fields_and_bad_files(tmp_path):
    with pytest.raises(QuestionError, match="missing"):
        Question.from_dict({"id": "q"})
    bad = tmp_path / "bad.toml"
    bad.write_text("id = ")
    with pytest.raises(QuestionError):
        Question.from_toml(bad)


def test_size_of_rectangles():
    assert size_of(16) == 16.0 and size_of("8x18") == 12.0
