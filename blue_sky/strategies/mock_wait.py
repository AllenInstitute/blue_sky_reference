from workflow_engine.strategies.wait_strategy \
    import WaitStrategy


class MockWait(WaitStrategy):
    def must_wait(self, obs):
        # Use this to check if the reference set is available
        # return true if the state is correc

        if 'DONE' != obs.proc_state:
            return True

        return False
