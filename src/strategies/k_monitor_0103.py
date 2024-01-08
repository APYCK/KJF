# encoding: UTF-8

import time
from egopy.trader.utility import round_to

from ego_ctastrategy.kjf import (
    CtaTemplate,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)

class KMonitorDemo(CtaTemplate):
    """MonitorDemo"""
    author = 'KJF'

    #变量映射表
    key = None
    #变量列表，保存了变量的名称
    variables = ['key',]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager(size=30)

        self.buySig = False
        self.sellSig = False
        self.k = {}
        self.last_tick = None

        self.write_log("egopy: 策略初始化 __init__")


    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("egopy: 策略初始化 on_init")
        self.load_bar(3)


    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.bg.update_tick(tick)
        self.last_tick = tick


        self.put_event()

    # ----------------------------------------------------------------------
    def get_indicator(self):
        """计算指标数据"""
        # k{}
        pricetick = self.get_pricetick()
        if not pricetick:
            return

        if not self.last_tick:
            return

        self.k['sma'] = round_to(self.am.sma(15), pricetick)
        self.k['pricetick'] = pricetick


    # ----------------------------------------------------------------------
    def get_signal(self, bar):
        """计算交易信号"""

        j = []
        k, d = self.am.stoch(9, 3, 1, 3, 1, True)
        #self.write_log("egopy: get_signal {}".format(k))
        for i in range(0,len(k)):
            j.append(round(3*k[i] - 2*d[i],2))

        j = j[-2:]

        if j[-2] < j[-1] < 38.2:
            self.buySig = True
            self.sellSig = False
            self.write_log("egopy: get_signal BUY")
        elif 61.8 < j[-1] < j[-2]:
            self.buySig = False
            self.sellSig = True
            self.write_log("egopy: get_signal SELL")
        else:
            self.buySig = False
            self.sellSig = False

        if not self.last_tick:
            return
        else:
            self.key = [self.k['pricetick'],self.k['sma'],j]


    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.am.update_bar(bar)
        if not self.am.inited:
            #self.write_log(u'am wrong : on_bar ? ')
            return

        if self.last_tick == None:
            #self.write_log(u'tick wrong : on_bar ? ')
            return
        tick = self.last_tick

        self.get_indicator()
        self.get_signal(bar)

        self.put_event()


    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("egopy: 策略启动 on_start")
        self.put_event()


    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("egopy: 策略停止 on_stop")
        self.put_event()

