# encoding: UTF-8

from datetime import datetime, time
from time import sleep


from egopy.trader.utility import round_to

from ego_ctastrategy.kjf import (
    CtaTemplate,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
    TickArrayManager,
)


########################################################################
class LaserIB24X6(CtaTemplate,TickArrayManager):
    """基于Tick的高频策略"""
    author = 'KJF with AiFund.Tech'

    # 策略参数
    ambush : int = 1
    direction = 'buy' #or 'sell'
    offset  = 'open' #or 'close'
    x_space : int = 1
    x_ruler : int = 1
    reference : float = 0.0

    # 参数映射表
    paramMap = {
        'ambush': '埋伏下单手数',
        'direction': '买卖方向',
        #'offset': '开平',
        'x_space': '委托笔数',
        'x_ruler': '多空参数',
        'reference': '参考价格',
    }
    #参数列表，保存了参数的名称
    parameters = list(paramMap.keys())

    # 策略变量
    ruler  = 0.01
    laser = True
    go_ready = 'Waiting'

    #变量列表，保存了变量的名称
    variables = ['go_ready','laser']


    # ----------------------------------------------------------------------
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """Constructor"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        #创建Array队列
        self.tickArray = TickArrayManager(size=60)

        self.buySig = False
        self.sellSig = False
        self.k = {}
        self.spacing : float = 1.0

        self.reference_price = None
        self.grid_ready = False

        self.buy_open_price = None
        self.sell_open_price = None

        self.last_tick = None
        self.orderID = None
        self.last_order = None

        self.wait_ticks = 0

        self.write_log("egopy: 策略初始化 __init__")

    # ----------------------------------------------------------------------
    def on_init(self):
        """初始化策略（必须由用户继承实现）"""
        self.write_log("egopy: 策略初始化 on_init")
        #tick级别交易，不需要过往历史数据

        self.put_event()

    # ----------------------------------------------------------------------
    def on_start(self):
        """启动策略（必须由用户继承实现）"""
        self.write_log("egopy: 策略启动 on_start")
        self.trading = True

        #self.vol = self.ambush
        if self.x_space >= 1:
            self.vol = self.ambush // self.x_space
        else:
            self.vol = self.ambush // 2
        self.write_log("egopy: vol: {}".format(self.vol))

        #if self.reference > 0:
            #self.reference_price = self.reference
            #self.write_log("egopy reference: {}".format(self.reference_price))

        self.grid_ready = True
        self.go_ready = 'Waiting'

        self.put_event()

    # ----------------------------------------------------------------------
    def on_stop(self):
        """停止策略（必须由用户继承实现）"""
        self.write_log("egopy: 策略停止 on_stop")
        self.trading = False
        self.grid_ready = False
        self.go_ready = 'Waiting'
        self.put_event()

    # ----------------------------------------------------------------------
    def on_tick(self, tick: TickData):
        if not self.trading:
            return
        else:
            xpr = datetime(2024,5,1,0,0,0)
            dt = tick.datetime
            dt = dt.replace(tzinfo=None)
            #self.write_log("Warning: dt tick - {}".format(dt))
            if dt > xpr:
                self.write_log("Warning: Expired! Expired! Expired!")
                #from time import sleep
                sleep(5)
                return

        self.last_tick = tick
        self.get_signal(tick)

        if self.grid_ready == True and self.buySig == True and self.direction == 'buy':
            self.price_start = self.last_tick.last_price
            self.write_log(u'egopy: LaserGun 初始化 on_tick buy')
            self.write_log(u'egopy: price_start: {}'.format(self.price_start))

            if self.offset == 'open':
                self.buy_open_price = self.price_start
                if self.direction == 'buy' and self.x_space == 0:
                    self.orderID = self.buy(self.price_start, self.vol)
                elif self.direction == 'sell' and self.x_space == 0:
                    self.orderID = self.short(self.price_start, self.vol)
                elif self.direction == 'buy' and self.x_space != 0:
                    for i in range(0,self.x_space):
                        self.orderID = self.buy(self.price_start - i * self.spacing, self.vol)
                elif self.direction == 'sell' and self.x_space != 0:
                    for i in range(0,self.x_space):
                        self.orderID = self.short(self.price_start + i * self.spacing, self.vol)
            elif self.offset == 'close':
                if self.direction == 'buy' and self.x_space == 0:
                    self.orderID = self.cover(self.price_start, self.vol)
                elif self.direction == 'sell' and self.x_space == 0:
                    self.orderID = self.sell(self.price_start, self.vol)
                elif self.direction == 'buy' and self.x_space != 0:
                    for i in range(0, self.x_space):
                        self.orderID = self.cover(self.price_start - i * self.spacing, self.vol)
                elif self.direction == 'sell' and self.x_space != 0:
                    for i in range(0, self.x_space):
                        self.orderID = self.sell(self.price_start + i * self.spacing, self.vol)
            self.grid_ready = False
            self.go_ready = 'Done'
            self.write_log('egopy: Grid初始化完成')
            #self.write_log("当前vol %s" % (self.vol))

        elif self.grid_ready == True and self.sellSig == True and self.direction == 'sell':
            self.price_start = self.last_tick.last_price
            self.write_log(u'egopy: LaserGun 初始化 on_tick sell')
            self.write_log(u'egopy: price_start: {}'.format(self.price_start))

            if self.offset == 'open':
                self.sell_open_price = self.price_start
                if self.direction == 'buy' and self.x_space == 0:
                    self.orderID = self.buy(self.price_start, self.vol)
                elif self.direction == 'sell' and self.x_space == 0:
                    self.orderID = self.short(self.price_start, self.vol)
                elif self.direction == 'buy' and self.x_space != 0:
                    for i in range(0,self.x_space):
                        self.orderID = self.buy(self.price_start - i * self.spacing, self.vol)
                elif self.direction == 'sell' and self.x_space != 0:
                    for i in range(0,self.x_space):
                        self.orderID = self.short(self.price_start + i * self.spacing, self.vol)
            elif self.offset == 'close':
                if self.direction == 'buy' and self.x_space == 0:
                    self.orderID = self.cover(self.price_start, self.vol)
                elif self.direction == 'sell' and self.x_space == 0:
                    self.orderID = self.sell(self.price_start, self.vol)
                elif self.direction == 'buy' and self.x_space != 0:
                    for i in range(0, self.x_space):
                        self.orderID = self.cover(self.price_start - i * self.spacing, self.vol)
                elif self.direction == 'sell' and self.x_space != 0:
                    for i in range(0, self.x_space):
                        self.orderID = self.sell(self.price_start + i * self.spacing, self.vol)
            self.grid_ready = False
            self.go_ready = 'Done'
            self.write_log('egopy: Grid初始化完成')
            #self.write_log("当前vol %s" % (self.vol))

        self.put_event()


    # ----------------------------------------------------------------------
    def get_signal(self, tick: TickData):
        """计算交易信号"""
        pricetick = self.get_pricetick()
        self.tam = self.tickArray
        self.tam.updateTick(tick)

        if not self.tam.inited:
            return
        else:
            self.k['atr'] = round_to(self.tam.atr(21), pricetick)
            #self.write_log("egopy: get_signal {}".format(self.k['atr']))

            self.k['ruler'] = round_to(self.x_ruler * self.k['atr'], pricetick)
            if self.k['ruler'] > 0:
                self.ruler = self.k['ruler']

            self.spacing = round_to(1.618 * self.ruler, pricetick)

            j = []
            k, d = self.tam.stoch(8, 3, 1, 3, 1, True)
            #self.write_log("egopy: get_signal {}".format(k))
            for i in range(0,len(k)):
                j.append(round(3*k[i] - 2*d[i],2))
            j = j[-2:]

            #hhv = self.tam.hhv(100)
            #llv = self.tam.llv(100)

            hhv, llv = self.tam.keltner(21,2)

        if self.reference_price == None:
            if self.reference > 0:
                self.reference_price = self.reference
                self.write_log("egopy reference: {}".format(self.reference_price))

        if self.buy_open_price and self.buy_open_price + self.ruler < llv:
            self.write_log("egopy: buy_open_price < {}".format(llv))
            self.buy_open_price = None
            self.go_ready = 'Waiting'
            self.cancel_all()
            self.write_log(u'取消订单: {} '.format(self.orderID))
            self.wait_ticks += 1
            while self.wait_ticks >= 20:
                self.grid_ready = True
                if self.reference > 0:
                    self.reference_price = self.reference
                self.wait_ticks = 0
                #self.write_log(u'重置等待结束')
        elif self.sell_open_price and self.sell_open_price - self.ruler > hhv:
            self.write_log("egopy: sell_open_price > {}".format(hhv))
            self.sell_open_price = None
            self.go_ready = 'Waiting'
            self.cancel_all()
            self.write_log(u'取消订单: {} '.format(self.orderID))
            self.wait_ticks += 1
            while self.wait_ticks >= 20:
                self.grid_ready = True
                if self.reference > 0:
                    self.reference_price = self.reference
                self.wait_ticks = 0
                #self.write_log(u'重置等待结束')
        elif not (self.buy_open_price and self.sell_open_price):
            if self.go_ready == 'Waiting':
                self.wait_ticks += 1
                while self.wait_ticks >= 20:
                    self.grid_ready = True
                    if self.reference > 0:
                        self.reference_price = self.reference
                    self.wait_ticks = 0
                    #self.write_log(u'重置等待结束')


        if self.grid_ready == True:
            if self.reference_price == None:
                if j[-2] < j[-1] < 30:
                    self.buySig = True
                    self.sellSig = False
                    self.write_log("egopy: buySig is True without reference")
                elif 70 < j[-1] < j[-2]:
                    self.buySig = False
                    self.sellSig = True
                    self.write_log("egopy: sellSig is True without reference")
            else:
                if j[-2] < j[-1] < 30:
                    if self.last_tick.last_price <= self.reference_price:
                        self.buySig = True
                        self.sellSig = False
                        #self.write_log("egopy: buySig < {}".format(self.reference_price))
                elif 70 < j[-1] < j[-2]:
                    if self.last_tick.last_price >= self.reference_price:
                        self.buySig = False
                        self.sellSig = True
                        #self.write_log("egopy: sellSig > {}".format(self.reference_price))

            if not (self.buySig and self.sellSig):
                self.wait_ticks += 1
                while self.wait_ticks >= 100:
                    self.wait_ticks = 0
                    #self.write_log(u'等待信号')
                    #self.write_log("egopy: get_signal {}".format(j))
                    #self.write_log("egopy reference: {}".format(self.reference_price))

        self.put_event()


    # ----------------------------------------------------------------------
    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        self.last_order = order
        if order.status.value == "全部成交":
            #self.write_log(u'订单: {} 全部成交'.format(self.last_order.orderid))
            pass

    # ----------------------------------------------------------------------
    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        self.last_trade = trade

        # IB style only, not for CTP in China
        trade = self.last_trade
        if trade.direction.value == '多':
            self.orderID = self.sell(trade.price + self.ruler, trade.volume)
            self.buy_open_price = None
        #elif trade.direction.value == '空' and trade.offset.value == '开':
            #self.orderID = self.cover(trade.price - self.ruler, trade.volume)
            #self.sell_open_price = None
        elif trade.direction.value == '空':
            self.orderID = self.buy(trade.price - self.ruler, trade.volume)
            self.buy_open_price = trade.price
        #elif trade.direction.value == '多' and trade.offset.value == '平':
            #self.orderID = self.short(trade.price + self.ruler, trade.volume)
            #self.sell_open_price = trade.price
        self.write_log("订单信息 %s " % (self.orderID))
        self.put_event()
