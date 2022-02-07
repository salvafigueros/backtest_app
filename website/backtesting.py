import queue 

class Backtesting():


    def __init__(self, ticker_list, events, bars, strategy, port, simulator):
        self.ticker_list = ticker_list
        self.events = events
        self.bars = bars
        self.strategy = strategy
        self.port = port
        self.simulator = simulator


    def execute_backtesting(self):
         while True:
                if self.bars.continue_backtest == True:
                    self.bars.update_bars()
                else: 
                    break

                while True:
                    try:
                        event = self.events.get(False)
                    except queue.Empty:
                        break
                    else:
                        if event is not None:
                            if event.type == 'MARKET':
                                self.strategy.calculate_signals(event)
                                self.port.update_timeindex(event)

                            elif event.type == 'SIGNAL':
                                self.port.update_signal(event)

                            elif event.type == 'ORDER':
                                self.simulator.execute_order(event)

                            elif event.type == 'FILL':
                                self.port.update_fill(event)

                            
    def output_results_backtesting(self):
        self.port.create_equity_curve_dataframe()
        return self.port.output_summary_stats()