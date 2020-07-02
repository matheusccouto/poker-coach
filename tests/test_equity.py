import timeit

import numpy as np

from poker_coach import equity


class TestDescrToHands:
    def test_prepare_descr(self):
        """ Check inputting bad descriptions and test if they are cleaned. """
        descr_list = [
            {"input": "AK", "output": "AKo"},
            {"input": "AKs", "output": "AKs"},
            {"input": "Qj", "output": "QJo"},
            {"input": "t9O", "output": "T9o"},
        ]
        for descr_dict in descr_list:
            output = equity.prepare_descr(descr_dict["input"])
            assert output == descr_dict["output"]

    def test_off_suited_hand(self):
        """ Test using a off-suited hand. """
        results_generator = equity.descr_to_hands("AKo")
        assert "AhKh" not in list(results_generator)

    def test_suited_hand(self):
        """ Test using a suited hand. """
        results_generator = equity.descr_to_hands("AKs")
        assert "AhKs" not in list(results_generator)

    def test_pair(self):
        """ Test using a pair. """
        results_generator = equity.descr_to_hands("AAo")
        assert "AsAh" in list(results_generator)

    def test_descr_to_hands_len(self):
        """ Check if expected cards are in the return of descr_to_hands."""
        results_list = list(equity.descr_to_hands("KKo"))
        assert 6 == len(results_list)


class TestDescrToRange:
    def test_off_suited_hand(self):
        """ Test using a off-suited hand. """
        results_list = equity.descr_to_range("A9o")
        assert len(list(results_list)) == 5

    def test_suited_hand(self):
        """ Test using a suited hand. """
        results_list = equity.descr_to_range("K9s")
        assert len(list(results_list)) == 9

    def test_pair(self):
        """ Test using a pair. """
        results_list = equity.descr_to_range("33o")
        assert len(list(results_list)) == 12


class TestRangeToHands:
    def test_pair(self):
        """ Test generating a range of pairs. """
        results_generator = equity.range_to_hands(["AAo", "KKo"])
        assert 12 == len(list(results_generator))

    def test_off_suited(self):
        """ Test generating off suited hands. """
        results_generator = equity.range_to_hands(["AKo", "AQo"])
        assert 24 == len(list(results_generator))

    def test_suited(self):
        """ Test generating off suited hands. """
        results_generator = equity.range_to_hands(["AKs", "AQs"])
        assert 8 == len(list(results_generator))


class TestDescrToHigherOrEqualHands:
    def test_pair(self):
        """ Test generating a  pairs. """
        results_generator = equity.descr_to_higher_or_equal_hands("KK")
        assert 12 == len(list(results_generator))

    def test_off_suited(self):
        """ Test generating off suited hands. """
        results_generator = equity.descr_to_higher_or_equal_hands("AQo")
        assert 24 == len(list(results_generator))

    def test_suited(self):
        """ Test generating off suited hands. """
        results_generator = equity.descr_to_higher_or_equal_hands("AQs")
        assert 8 == len(list(results_generator))


class TestGetAllHands:
    def test_single(self):
        """ Test generating a  pairs. """
        results_generator = equity.get_all_hands("KK")
        assert 12 == len(list(results_generator))

    def test_range(self):
        """ Test generating a  two cards. """
        results_generator = equity.get_all_hands("KK AKs")
        assert 16 == len(list(results_generator))

    def test_wider_range(self):
        """ Test generating a wider range. """
        results_generator = equity.get_all_hands("KQs")
        assert 12 == len(list(results_generator))


class TestHandToDescr:
    def test_hand_to_descr(self):
        answers = {"6dQd": "Q6s", "AdAs": "AA"}
        for key, val in answers.items():
            assert equity.hand_to_descr(key) == val


class TestPercentage:
    def test_hand_percentage(self):
        for row in equity.hand_ranking.itertuples():
            assert equity.descr_to_percentage(row.hand) == row.value

    def test_percentage_hand(self):
        for row in equity.hand_ranking.itertuples():
            assert equity.descr_to_percentage(row.hand) == row.value


class TestFlopTurnRiver:
    def test_get_cards(self):
        flop_turn_river = equity.flop_turn_river("AsAh")
        assert len(flop_turn_river) == 5

    def test_not_in(self):
        several = [equity.flop_turn_river("As") for _ in range(1000)]
        has_as = ["As" in board for board in several]
        assert not any(has_as)


class TestEquity:
    @staticmethod
    def test_single():
        result = equity.eval_single([["QsQh"], ["AsKs"]])
        assert result.size == 2

    @staticmethod
    def test_single_speed():
        setup = "from poker_coach.equity import eval_single"
        time = timeit.timeit(
            "eval_single([['QsQh'], ['AsKs']], False)", setup=setup, number=10000
        )
        assert time < 10

    @staticmethod
    def test_equity_from_range_descr():
        answer_list = [
            {"range": ["AA", "55 AT A8s"], "equity": [0.844, 0.156]},
            {"range": ["AsAh", "55 AT A8s"], "equity": [0.844, 0.156]},
        ]
        rounding = 1
        for answer in answer_list:
            equity_list = equity.equity_from_range_descr(answer["range"], times=1000)
            np.testing.assert_almost_equal(
                np.round(equity_list, rounding), np.round(answer["equity"], rounding)
            )

    @staticmethod
    def test_equity():
        answer_list = [
            {"range": [0.5, 10], "equity": [0.844, 0.156]},
            {"range": ["AsAh", "55 AT A8s"], "equity": [0.844, 0.156]},
        ]
        rounding = 1
        for answer in answer_list:
            equity_list = equity.equity(answer["range"], times=1000)
            np.testing.assert_almost_equal(
                np.round(equity_list, rounding), np.round(answer["equity"], rounding)
            )
