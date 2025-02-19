from PySide6.QtCore import QDateTime, QThread, Signal
import akshare as ak
import pandas as pd


class FundHoldDetailThread(QThread):
    progress_signal = Signal(str)  # 用于传递进度日志
    result_signal = Signal(str, pd.DataFrame)  # 用于传递任务完成后的结果
    error_signal = Signal(str)  # 用于传递错误信息

    def __init__(self, logger=None):
        super().__init__()
        self._fund_code = None
        self._log = logger

    def set_fund_code(self, fund_code: str):
        """设置 fund_code"""
        self._fund_code = fund_code

    def run(self):
        is_succ = True
        year = QDateTime.currentDateTime().toString("yyyy")

        try:
            self.progress_signal.emit(f"获取 {year} 年基金 {self._fund_code} 仓位占比中...")
            data = ak.fund_portfolio_hold_em(symbol=self._fund_code,
                                             date=year)
        except Exception as e:
            is_succ = False
            data = None
            error_message = f"获取 {year} 年基金 {self._fund_code} 仓位占比时发生错误: {str(e)}"
            self.progress_signal.emit(error_message)
            self.error_signal.emit(error_message)  # 发送错误信号

        last_report = None
        if not is_succ:
            try:
                is_succ = True
                year = int(year) - 1
                self.progress_signal.emit(f"获取 {year} 年基金 {self._fund_code} 仓位占比中...")
                data = ak.fund_portfolio_hold_em(symbol=self._fund_code,
                                                 date=str(year))
                last_report = data.iloc[-1, -1]  # 最后的报告时间如：2024年3季度股票投资明细
                data = data[data["季度"] == last_report]
                data = data[["股票代码", "股票名称", "占净值比例"]]

            except Exception as e:
                is_succ = False
                data = None
                error_message = f"获取 {year} 年基金 {self._fund_code} 仓位占比时发生错误: {str(e)}"
                self.progress_signal.emit(error_message)
                self.error_signal.emit(error_message)  # 发送错误信号

        self.progress_signal.emit(f"获取基金 {self._fund_code}： {last_report} 仓位占比完成")
        self._fund_code = None
        self.result_signal.emit(last_report, data)  # 发送结果到主线程
