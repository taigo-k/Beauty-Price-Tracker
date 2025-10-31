# 💰 競合価格自動追跡システム (Beauty Price Tracker)
概要: The Ordinaryの競合価格を監視し、変動をGmailで即時通知するPythonによる自律型データパイプライン構築プロジェクト。

## 🎯 課題とソリューション
課題: 競合価格の把握が手動であり、時間と人的リソースを浪費し、市場への迅速な対応が不可能だった。
解決策: Pythonスクリプトを構築し、Webスクレイピング、Pandas分析、外部通知までを一気通貫で自動化。これにより、価格戦略の洞察を即座に提供する。

## 🛠️ 技術スタックと実装のポイント
* 言語: Python 3.10+
* コアライブラリ: requests, BeautifulSoup4, pandas, smtplib

[実装のポイント]
1. アンチスクレイピング対策: HTTPヘッダーにUser-Agentを設定し、ボットと認識されることを回避。
2. 堅牢なデータ抽出: Webサイト固有のHTML属性 (content) から直接価格データを抽出し、抽出ロジックの安定性を確保。
3. データパイプライン: pandas.concat と pandas.merge を使用し、履歴の追記と最新データとの高速比較を実現。
4. セキュリティ連携: Gmail通知に際し、アプリパスワードとSMTP/SSL接続を採用し、認証情報の安全性を確保。

## 📊 アウトプットと実行
### 価格履歴の永続化 (price_history.csv)
実行履歴はCSVファイルに時系列で保存されます。これにより、価格推移のグラフ化や詳細分析が可能になります。
> 上記データでは、PROD003で設定閾値（$1.00）を超える値下げを検知するように調整されています。

### 自動通知イメージ(Gmail通知)
【Price Alerts】

### 実行環境
BeautyPriceTracker.py を使用し、OSのタスクスケジューラ（Windows Task Scheduler / macOS Cron/launchd）に登録することで、定期的な監視と自動実行を実現しています。



----- **English Version** -----
# 💰 Beauty Price Tracker (Automated Competitor Pricing System)
Overview: An autonomous Python data pipeline project designed to monitor competitor pricing on e-commerce sites (The Ordinary) and deliver instant notifications via Gmail upon detecting price changes.

## 🎯 Business Problem & Solution
Problem: Manual competitor price checks resulted in time consumption and delayed market response capabilities.
Solution: Developed a seamless pipeline encompassing scraping, Pandas analysis, and external notification, providing immediate insights into competitive pricing strategies.

## 🛠️ Key Technologies & Implementation
* Language: Python 3.10+
* Core Libraries: requests, BeautifulSoup4, pandas, smtplib

[Implementation Highlights]
1. Anti-Scraping Measures: Configured User-Agent headers within requests to mitigate bot detection.
2. Robust Data Extraction: Specifically targeted and extracted price data from HTML attributes (content) for stability across site updates.
3. Data Pipeline: Utilized pandas.concat for historical data appending and pandas.merge for efficient change detection.
4. Secure Integration: Employed Gmail App Passwords and SMTP/SSL for secure and verified external notification functionality.

## 📊 Output & Deployment
### Historical Data Persistence
Execution history is saved chronologically in a CSV file, enabling detailed analysis and visualization.
> The above data is configured to show a price decrease exceeding the $1.00 threshold for PROD003.

### Automated Notification Example(Gmail Notification)
【Price Alerts】

### Execution Environment
The system is registered with the OS's Task Scheduler (Windows/macOS) to achieve scheduled, autonomous monitoring.
