

class FormattingUtils(object):
    @staticmethod
    def format_currency(value):
        return "$%s.%02d" % ("{:,}".format(value // 100), value % 100)

    @staticmethod
    def format_percentage(numerator, denominator):
        return "%.1f%%" % (float(numerator) / denominator * 100)

