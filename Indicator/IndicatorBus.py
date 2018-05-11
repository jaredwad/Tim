from pandas import DataFrame


class IndicatorBus:
    def __init__(self):
        self.indicators = dict()

    def add_indicator(self, indicator_function, params):

        indicator = Indicator(indicator_function, params)

        self.indicators[indicator.get_name()] = indicator

    def handle_ticks(self, data: DataFrame):
        for key in self.indicators.keys():
            data = self.indicators[key].call_ind_function(data)
        return data


class Indicator:
    def __init__(self, indicator_function, parameters):
        self.indicator_function = indicator_function
        self.parameters = parameters
        self.name = self.create_name()

    def create_name(self):
        param_str = ''
        for param in self.parameters:
            param_str += str(param) + '_'

        name = self.indicator_function.__name__ + '_' + param_str
        return name

    def get_name(self):
        return self.name

    def call_ind_function(self, df: DataFrame):
        return self.indicator_function(df, *self.parameters)
