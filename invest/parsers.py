from datetime import datetime, timedelta, date as create_date


class FromToDateParser:
    def __init__(self, default_from=None, default_to=None):
        self.default_from = default_from
        self.default_to = default_to

    @staticmethod
    def next_day():
        return (datetime.now() + timedelta(days=1)).date()

    def parse_date(self, date):
        date = date.replace('.', '-')
        parts = date.split('-')
        if len(parts) == 1:
            date += '-01-01'
            year = int(parts[0])
            self.default_to = create_date(year + 1, 1, 1)
        elif len(parts) == 2:
            date += '-01'
            year = int(parts[0])
            month = int(parts[1])
            self.default_to = create_date(year + month // 12, month % 12 + 1, 1)
        return datetime.strptime(date, "%Y-%m-%d").date()

    def get_default_to(self):
        return self.default_to
