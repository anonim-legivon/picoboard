from rest_framework.throttling import ScopedRateThrottle


class CustomScopedRateThrottle(ScopedRateThrottle):
    def parse_rate(self, rate):
        if rate is None:
            return None, None

        if isinstance(rate, int):
            num_requests = 1
            duration = rate
            return num_requests, duration

        num, period = rate.split('/')
        num_requests = int(num)

        time_factor, period = period.split(' ')
        if period is None:
            period = time_factor
            time_factor = 1
        else:
            time_factor = int(time_factor)

        duration = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[period[0]]
        duration *= time_factor
        return num_requests, duration