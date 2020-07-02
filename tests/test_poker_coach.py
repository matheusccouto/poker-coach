import poker_coach


class TestScenario:
    """ Test general scenario class. """

    @staticmethod
    def test_n_seats():
        assert poker_coach.Scenario(3).n_seats == 3

    @staticmethod
    def test_hero_has_hand():
        assert len(poker_coach.Scenario().hero_hand) == 4

    @staticmethod
    def test_villain_range_len():
        assert len(poker_coach.Scenario(9).villains_range) == 8

    @staticmethod
    def test_villain_range_values():
        scene = poker_coach.Scenario()
        for villain_range in scene.villains_range:
            assert 1 <= villain_range <= 100

    @staticmethod
    def test_hero_chips():
        scene = poker_coach.Scenario()
        assert scene.MIN_BB <= scene.hero_chips <= scene.MAX_BB

    @staticmethod
    def test_hero_position():
        for _ in range(1000):
            assert -9 <= poker_coach.Scenario(9).hero_index <= -1

    @staticmethod
    def test_villain_chips():
        scene = poker_coach.Scenario(9)
        for villain_chips in scene.villains_chips:
            assert scene.MIN_BB <= villain_chips <= scene.MAX_BB

    @staticmethod
    def test_villains_before_and_after_range_sum():
        scene = poker_coach.Scenario(10)
        assert len(scene.villains_after_range) + len(scene.villains_before_range) == 9

    @staticmethod
    def test_villains_after_range_not_null():
        scene = poker_coach.Scenario(10)
        assert len(scene.villains_after_range) != 0

    @staticmethod
    def test_villains_before_and_after_chips_sum():
        scene = poker_coach.Scenario(10)
        assert len(scene.villains_after_chips) + len(scene.villains_before_chips) == 9

    @staticmethod
    def test_villains_after_chips_not_null():
        scene = poker_coach.Scenario(10)
        assert len(scene.villains_after_chips) != 0

    @staticmethod
    def test_villains_after_position():
        scene = poker_coach.Scenario(9)
        assert "BB" in scene.villains_after_position

    @staticmethod
    def test_villains_after_position_not_null():
        scene = poker_coach.Scenario(10)
        assert len(scene.villains_after_position) != 0

    @staticmethod
    def test_ante():
        assert poker_coach.Scenario(ante=10).ante == 10

    @staticmethod
    def test_pot():
        assert poker_coach.Scenario(n_seats=10, ante=10).pot == 1.5 + 10 * 10 / 100

    @staticmethod
    def test_eval_ranges_len():
        scene = poker_coach.Scenario(2)
        eqs = scene.eval_ranges(
            hero_hand=scene.hero_hand,
            villains_range=scene.villains_range,
            times=100,
        )
        assert len(eqs) == 1

    @staticmethod
    def test_eval_ranges_values():
        scene = poker_coach.Scenario(2)
        eqs = scene.eval_ranges(
            hero_hand=scene.hero_hand,
            villains_range=scene.villains_range,
            times=100,
        )
        for eq in eqs:
            assert 0 < eq < 1

    @staticmethod
    def test_expected_value():
        assert poker_coach.Scenario.expected_value(0.25, 26000, 6400) == 1700

    @staticmethod
    def test_strategies_expected_value_len():
        scene = poker_coach.Scenario(2)
        evs = scene.strategies_expected_value(
            chances=0.5,
            win_action=1,
            lose_action=-1,
            no_action=0,
        )
        assert len(evs) == 2  # Push and fold EV.

    @staticmethod
    def test_strategies_expected_value_values():
        scene = poker_coach.Scenario(2)
        evs = scene.strategies_expected_value(
            chances=0.5,
            win_action=1,
            lose_action=-1,
            no_action=0,
        )
        assert evs[0] > 0 and evs[1] == 0
