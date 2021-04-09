class EventFactory:
    def __init__(self, guards, channels, symbols, signals):
        self.guards = guards
        self.channels = channels
        self.symbols = symbols
        self.signals = signals

    def set_guards(self, guards):
        self.guards = guards

    def set_channels(self, channels):
        self.channels = channels

    def set_symbols(self, symbols):
        self.symbols = symbols

    def set_signals(self, signals):
        self.signals = signals

    def get_guards(self):
        return self.guards

    def get_channels(self):
        return self.channels

    def get_symbols(self):
        return self.symbols

    def get_signals(self):
        return self.signals
