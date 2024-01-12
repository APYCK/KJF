# encoding: UTF-8

import time

from ego_ctastrategy.kjf import (
    CtaTemplate,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
    # TickArrayManager,
)

# 根据需要预先加载常用技术指标，注意指标字母大写
from ego_ctastrategy.kjf import (
    CROSS, RD, EMA, MACD, KDJ, BOLL,
)
"""
原生支持主流技术指标的简洁写法及快速调用，用C语言内置在主程序中。
诸如EMA，HHV，BOLL，KDJ，MACD，CROSS等常见指标都可以直接调用。

部分代码冗余是为了方便示例或检测.具体使用请根据需要删减或增加内容.
"""

class KMinuteIBDemo(CtaTemplate):
    """Minute IB DEMO"""
    author = 'KJF'

    # 策略参数
    vol : int = 1 # 订单持仓数量设置
    direction = 'buy' #or 'sell'
    offset  = 'open' #or 'close'
    # 自定义指标参数设置
    GT1 = 3
    GT2 = 5
    GTM : int = 10

    # 参数映射表
    paramMap = {
        'vol': '下单手数',
        'direction': '买卖方向',
        'offset': '开平',
        'GT1': '自定义指标参数1',
        'GT2': '自定义指标参数2',
        'GTM': '自定义指标参数M',
    }
    #参数列表，保存了参数的名称
    parameters = list(paramMap.keys())

    #变量映射表
    demo = 'Any Thing You Want Here'
    go_ready = 'Waiting'
    key = None
    #变量列表，保存了变量的名称
    variables = ['go_ready','key','demo']

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar)
        # 根据需要预加载数据量，此处默认10个周期（分钟），方便测试。
        if self.GTM <= 5:
            self.GTM = 5

        self.am = ArrayManager(size=self.GTM)
        # self.tam = TickArrayManager(size=60) # 调用tick数据，适合日内中高频。

        self.buySig = False
        self.sellSig = False
        self.k = {}
        self.last_tick = None
        self.orderID = None
        self.last_order = None

        self.grid_ready = False

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
        if not self.trading:
            return
        self.bg.update_tick(tick)
        self.last_tick = tick


    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.am.update_bar(bar)
        if not self.am.inited:
            return

        if self.last_tick == None:
            return

        tick = self.last_tick

        self.get_indicator()
        self.get_signal(bar)

        # 根据信号,下单逻辑
        if self.grid_ready == True and self.buySig == True:
            self.price_start = self.last_tick.last_price
            # self.write_log(u'egopy: Demo on_tick buy')
            self.write_log(u'egopy: price_start: {}'.format(self.price_start))

            if self.direction == 'buy':
                self.orderID = self.buy(self.price_start, self.vol)

            elif self.direction == 'sell':
                self.orderID = self.cover(self.price_start, self.vol)

            self.write_log('egopy: buy order OK')

        elif self.grid_ready == True and self.sellSig == True:
            self.price_start = self.last_tick.last_price
            # self.write_log(u'egopy: Demo on_tick sell')
            self.write_log(u'egopy: price_start: {}'.format(self.price_start))

            if self.direction == 'sell':
                self.orderID = self.short(self.price_start, self.vol)

            elif self.direction == 'buy':
                self.orderID = self.sell(self.price_start, self.vol)

            self.write_log('egopy: sell order OK')

        self.put_event()

    # ----------------------------------------------------------------------
    def get_indicator(self):
        """计算指标数据"""
        pricetick = self.get_pricetick()
        if not pricetick:
            return

        if not self.last_tick:
            return

        # 指定数据源
        S = self.am.close

        self.k['pricetick'] = pricetick
        self.k['ema'] = RD(EMA(S,5), D=len(str(pricetick))).tolist()
        # self.write_log(self.k['ema'] )

        # 输出数据内容到图形界面的KEY变量,示范
        self.key = [self.k['pricetick'],self.k['ema']]

        # 指定参与计算的数据源及指标
        """
        支持EMA，HHV，BOLL，KDJ，MACD，CROSS等常见指标的灵活调用
        """
        self.S1 = EMA(S,self.GT1) # 此处代表3个周期的EMA指标数值
        self.S2 = EMA(S,self.GT2) # 此处代表5个周期的EMA指标数值

    # ----------------------------------------------------------------------
    def get_signal(self, bar):
        """计算交易信号"""

        pricetick = self.get_pricetick()
        if not pricetick:
            return

        if not self.last_tick:
            return

        # 参与计算的数据源及指标,来自get_indicator部分
        # S = self.am.close
        S1 = self.S1 # 此处对应get_indicator部分
        S2 = self.S2 # 此处对应get_indicator部分

        if CROSS(S1,S2)[-1] == True:
            cond = 0
        elif CROSS(S2,S1)[-1] == True:
            cond = 1
        else:
            cond = 2

        if cond == 0:
            self.buySig = True
            self.sellSig = False
            self.write_log("egopy: get_signal BUY")
        elif cond == 1:
            self.buySig = False
            self.sellSig = True
            self.write_log("egopy: get_signal SELL")
        else:
            self.buySig = False
            self.sellSig = False
            # self.write_log("egopy: get_signal None")

    # ----------------------------------------------------------------------
    def on_trade(self, trade: TradeData):
        """此处为模板示范内容,根据需要增加或者删除!"""

        # print(str(trade.direction.value))
        # self.write_log("trade.direction.value状态 %s " % (trade.direction.value))
        if self.direction == 'buy':
            if trade.direction.value == '多':
                self.offset = 'close' # 更改预期状态
            elif trade.direction.value == '空':
                self.offset = 'open' # 更改预期状态
        elif self.direction == 'sell':
            if trade.direction.value == '多':
                self.offset = 'open' # 更改预期状态
            elif trade.direction.value == '空':
                self.offset = 'close' # 更改预期状态

        # self.write_log("预期下个信号状态 %s " % (self.offset))
        self.put_event()

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("egopy: 策略启动 on_start")
        self.trading = True
        self.grid_ready = True
        self.go_ready = 'Done'

        self.put_event()

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("egopy: 策略停止 on_stop")
        self.trading = False
        self.grid_ready = False
        self.go_ready = 'Waiting'
        self.put_event()

