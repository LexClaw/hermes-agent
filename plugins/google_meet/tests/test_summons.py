"""Tests for plugins.google_meet.summons."""
from __future__ import annotations

import pytest

from plugins.google_meet.summons import (
    is_summons,
    match_summons,
    is_summons_batch,
)


class TestEmptyAndEdgeCases:
    def test_empty_string(self):
        assert not is_summons("")

    def test_whitespace_only(self):
        assert not is_summons("   \n  \t  ")

    def test_none(self):
        assert not is_summons(None)  # type: ignore - explicit edge case

    def test_ambient_conversation(self):
        assert not is_summons("Let's circle back on the Q3 metrics tomorrow")

    def test_name_mention_only(self):
        # Saying "Lex" without an action verb should not trigger
        assert not is_summons("I think Lex would agree with this approach")
        # Ambient conversation mentioning a name without summons context
        assert not is_summons("Ask Alex about the metrics")

    def test_lex_mention_in_middle(self):
        # "Lex" embedded in other words should not trigger
        assert not is_summons("The most flexible solution is...")


class TestDirectAddress:
    def test_lex_file(self):
        assert is_summons("Lex, file that action item")

    def test_lex_create_card(self):
        assert is_summons("Lex, create a card for the budget review")

    def test_lex_capture(self):
        assert is_summons("Lex, capture this point about the timeline")

    def test_lex_remind(self):
        assert is_summons("Lex, remind me to follow up with Sarah")

    def test_lex_note(self):
        assert is_summons("Lex, note that we need to update the API key by Friday")

    def test_case_insensitive(self):
        assert is_summons("LEX, please file this")
        assert is_summons("lex, file this real quick")

    def test_alex_variant(self):
        # ALEX as alternative trigger
        assert is_summons("Alex, file this for me")

    def test_lex_save(self):
        assert is_summons("Lex, save this for later review")

    def test_lex_log(self):
        assert is_summons("Lex, log this decision about the vendor")


class TestImperativeWithLexAtEnd:
    def test_file_it_lex(self):
        assert is_summons("Please file this, Lex")

    def test_create_that_lex(self):
        assert is_summons("Can you create a card for that, Lex?")


class TestHeyLex:
    def test_hey_lex_please(self):
        assert is_summons("Hey Lex, please add a task for the demo")

    def test_ok_lex(self):
        assert is_summons("OK Lex, go ahead and email that summary")

    def test_okay_lex(self):
        assert is_summons("Okay Lex, capture the main points from this call")


class TestDirectImperative:
    def test_lex_do_it(self):
        assert is_summons("Lex, do it. File the card now")

    def test_lex_yes(self):
        assert is_summons("Lex: yes, go ahead and file that card")

    def test_lex_yes_comma(self):
        assert is_summons("Lex, yes file it")


class TestMatchSummons:
    def test_returns_matches(self):
        matches = match_summons("Lex, file the Q3 report")
        assert len(matches) >= 1
        assert "file" in matches[0][1].lower()

    def test_no_match_returns_empty(self):
        matches = match_summons("The weather is nice today")
        assert matches == []

    def test_multiple_matches(self):
        # A line with two distinct summon patterns should match multiple
        matches = match_summons("Hey Lex please file this and Alex create a card too")
        # At least 2: HEY_NAME_ACTION for "Hey Lex please" and NAME+ACTION for both
        assert len(matches) >= 2


class TestIsSummonsBatch:
    def test_empty_list(self):
        assert is_summons_batch([]) == []

    def test_mixed_lines(self):
        lines = [
            "Hey, how's everyone?",
            "Lex, file this action item",
            "Moving on to the next topic",
            "Alex, create a card for the budget",
        ]
        results = is_summons_batch(lines)
        # Line 0 "Hey, how's everyone?" - "Hey" alone does NOT trigger HEY_NAME_ACTION
        # since it needs "Lex" after "Hey". So this should NOT match.
        # Line 1 "Lex, file this action item" - NAME+ACTION match
        # Line 3 "Alex, create a card for the budget" - NAME+ACTION match
        assert len(results) == 2
        assert results[0][0] == 1  # line index
        assert results[1][0] == 3  # line index

    def test_all_ambient(self):
        lines = [
            "The revenue looks good this quarter",
            "Let's revisit next week",
            "I'll send the deck by Friday",
        ]
        assert is_summons_batch(lines) == []
