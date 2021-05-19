from appdaemontestframework import automation_fixture

from apps.simple_for_testing import SimpleForTesting


@automation_fixture(SimpleForTesting)
def simple_thing():
    pass


# noinspection PyShadowingNames
def test_simple_thing(given_that, simple_thing, assert_that):
    given_that.state_of('this_id').is_set_to('off')

    simple_thing.do_thing({})

    assert_that('this_id').was.turned_off()
