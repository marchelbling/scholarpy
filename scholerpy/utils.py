import time


def wait(delay):
    def decorator(method):
        def clocked(self, *args, **kwargs):
            if self.clock:
                elapsed = time.time() - self.clock
                if elapsed < delay:
                    time.sleep(delay - elapsed)
            result = method(self, *args, **kwargs)
            self.clock = time.time()
            return result
        return clocked
    return decorator
