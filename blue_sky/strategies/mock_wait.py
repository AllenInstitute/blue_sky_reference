from workflow_engine.strategies.wait_strategy \
    import WaitStrategy
from blue_sky.models import Observation


class MockWait(WaitStrategy):
    def must_wait(self, obs):
        # Use this to check if the reference set is available
        # return true if the state is correc

        if Observation.STATE.OBSERVATION_DONE != obs.object_state:
            return True

        return False
