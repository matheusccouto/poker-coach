import poker
import poker_coach


class TestScenario:

    def test_n_seats(self):
        assert poker_coach.Scenario(3).n_seats == 3

    def test_hero_seat_0(self):
        assert poker_coach.Scenario().seats[0].name == "Hero"

    def test_hero_has_hand(self):
        assert isinstance(poker_coach.Scenario().hero_hand, poker.Hand)

    def test_hero_hand_descr(self):
        assert isinstance(poker_coach.Scenario().hero_hand_descr, str)

    def test_chips(self):
        scene = poker_coach.Scenario(9)
        for player in scene.seats:
            assert poker_coach.MIN_BB <= player.chips <= poker_coach.MAX_BB

    def test_ranges(self):
        scene = poker_coach.Scenario(9)
        for rng in scene.villain_range.values():
            assert 0 <= rng <= 100
