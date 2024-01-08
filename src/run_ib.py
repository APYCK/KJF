# flake8: noqa
from egopy.event import EventEngine

from egopy.trader.engine import MainEngine
from egopy.trader.ui import MainWindow, create_qapp

# from ego_ctp import CtpGateway
from ego_ib import IbGateway

from ego_paperaccount import PaperAccountApp
from ego_ctastrategy import CtaStrategyApp
from ego_ctabacktester import CtaBacktesterApp
from ego_datamanager import DataManagerApp
from ego_datarecorder import DataRecorderApp
from ego_chartwizard import ChartWizardApp
from ego_spreadtrading import SpreadTradingApp
from ego_riskmanager import RiskManagerApp
from ego_optionmaster import OptionMasterApp
from ego_algotrading import AlgoTradingApp
from ego_portfoliostrategy import PortfolioStrategyApp
from ego_portfoliomanager import PortfolioManagerApp


def main():
    """"""
    qapp = create_qapp()

    event_engine = EventEngine()

    main_engine = MainEngine(event_engine)

    # main_engine.add_gateway(CtpGateway)
    # main_engine.add_gateway(IbGateway)
    main_engine.add_app(PaperAccountApp)
    # main_engine.add_app(CtaBacktesterApp)

    main_engine.add_gateway(IbGateway)

    main_engine.add_app(CtaStrategyApp)
    main_engine.add_app(PortfolioStrategyApp)
    main_engine.add_app(SpreadTradingApp)
    main_engine.add_app(AlgoTradingApp)
    main_engine.add_app(OptionMasterApp)
    main_engine.add_app(RiskManagerApp)
    main_engine.add_app(PortfolioManagerApp)
    main_engine.add_app(ChartWizardApp)
    main_engine.add_app(DataManagerApp)
    main_engine.add_app(DataRecorderApp)

    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()

    qapp.exec()


if __name__ == "__main__":
    main()
