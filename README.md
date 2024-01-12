<p align="center">
    <img src ="https://img.shields.io/badge/platform-linux-yellow.svg"/>
    <img src ="https://img.shields.io/badge/python-3.10-blue.svg" />
</p>

## K J F

* The native software plugins for EGOPY platform
* Imporve your EGOPY with the smart strategies

## EGOPY = EGO + PYthon

* Define your trading style.

<p align="left">
EGOPY Global Trader 始于开源系统和交易框架，致力于研发更高效的智能投顾&量化投资交易系统。
</p>


## 简单说明
* 此策略系统的代码开源，目前锁定<code>python 3.10.x </code>的版本。
* 兼容多种主流策略写法。兼容常见股票/期货软件的内置指标，兼容开源框架vn的策略写法。
* 默认使用者有简单的linux和python基础。
* 以实战为目标，专注于更好的策略研发以及更稳定的框架。
* 请参考DEMO类策略文件，自行调试使用。
* 此策略系统含框架程序，以学习交流和投资研究为主要诉求。
* 手持倚天剑的未必战无不胜，但好的软件工具一定会让工作如虎添翼。
* 市场有风险，投资需谨慎。多作研究测试，可以少走弯路。

## 环境准备
* 支持的操作系统版本：  <code>openSUSE Leap 15</code> 或 <code>Kubuntu 20.04</code> 以上，需要安装图形界面
* 支持的Python版本：64位的 <code>Python 3.10.x</code> （**注意必须是Python 64位版本**）

## 安装运行
* 预先下载此仓库的 <code>requirements.txt</code> 文件到本地，然后通过 <code>pip install -r requirements.txt</code> 进行安装。
* 如果在中国境内，可以通过命令 <code>pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt</code> 快速安装。
* 也可以通过 <code>pip install kjf</code> 方式直接安装。如有缺失的文件依赖，通过pip或conda方式安装补齐即可。
* 尝试运行如下代码启动程序：
* <code>python -m kjf.demo</code> 启动策略测试运行。
* 实盘操作请直接通过 <code>EGOPY</code> 进行。
* 以上操作会自动安装 <code>EGOPY</code> 框架。（可以参考EGOPY项目说明。）

## Copyright
* BSD 3-Clause License
