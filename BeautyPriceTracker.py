#!/usr/bin/env python
# coding: utf-8

# In[3]:


# --- 必要なライブラリのインポート ---
import requests                      #サイトへアクセス
from bs4 import BeautifulSoup        #HTMLの解析
import pandas as pd                  #データ処理
from datetime import datetime        #日時記録
import time                          #待機時間設定
import smtplib                       #メール送信
from email.mime.text import MIMEText #文字化け防止
from email.header import Header      #文字化け防止

print("必要なライブラリのインポートが完了しました。")


# In[4]:


# --- 1. 監視対象の商品リスト定義 ---
product_list = [
    {
        'id': 'PROD001', 
        'name': 'Hyaluronic Acid 2% + B5 (with Ceramides)', 
        'url': 'https://theordinary.com/en-ca/hyaluronic-acid-2-b5-serum-with-ceramides-100637.html'
    },
    {
        'id': 'PROD002', 
        'name': 'Niacinamide 10% + Zinc 1%', 
        'url': 'https://theordinary.com/en-ca/niacinamide-10-zinc-1-serum-100436.html'
    },
    {
        'id': 'PROD003', 
        'name': 'The Balance Set', 
        'url': 'https://theordinary.com/en-ca/the-balance-set-100447.html'
    }
]

# --- 2. ファイル名と価格変動の閾値 ---
CSV_FILENAME = 'price_history.csv'
PRICE_CHANGE_THRESHOLD = 1.00 #1.00 CAD以上の変動を検知

# --- 3. Gmail通知設定 (※GitHub公開時はダミー値に戻すこと) ---
GMAIL_SENDER_EMAIL = "3131tigo@gmail.com"    #送信元
GMAIL_APP_PASSWORD = "ntkq ppll ywdd hhgi"   #アプリパスワード
GMAIL_RECIPIENT_EMAIL = "3131tigo@gmail.com" #送信先

print("設定情報と商品リストの定義が完了しました。")


# In[5]:


# --- 1. Webサイトから価格を抽出する関数 (scrape_price) ---
def scrape_price(url, product_id):
    
    #User-Agentを設定し、ブラウザからのアクセスに見せかける
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        #1. URLにアクセス
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() #ステータスコードを確認
        
        #2. HTMLを解析
        soup = BeautifulSoup(response.text, 'html.parser') #(文字列データ, 解析ルール)
        
        #3. 価格情報が含まれる要素を抽出
        price_element = soup.find('span', class_='value') #HTML<span class="value" content="XX.XX">
        
        if price_element and 'content' in price_element.attrs:
            #content属性の値を取得
            price_text = price_element['content']
            
            #数値に変換できない可能性を考慮したエラーハンドリング
            try:
                #整数部のみを取得（小数点以下は切り捨て）
                price_value = float(price_text)
                return price_value
            except ValueError:
                return "Parsing Error" #数値変換エラー
        else:
            return "Not Found" #要素が見つからないエラー
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Webアクセスエラー (ID: {product_id}): {e}") 
        return "Error"

# --- 2. 価格変動をチェックし、アラートメッセージを作成する関数 (check_price_change) ---
def check_price_change(csv_filename, price_change_threshold):
    """最新の価格データと前回の価格データを比較し、変動があればアラートメッセージを作成する"""
    
    try:
        df_all = pd.read_csv(csv_filename)
    except FileNotFoundError:
        return [] #履歴ファイルがない場合は空リストを返す

    #データ整形と準備
    df_all['scrape_date'] = pd.to_datetime(df_all['scrape_date'])
    #数値に変換できない値はNaNとし、fillna(0.0)で欠損値を0に置き換えて計算を可能にする
    df_all['current_price'] = pd.to_numeric(df_all['current_price'], errors='coerce').fillna(0.0)
    df_all = df_all.sort_values(by='scrape_date', ascending=False)
    
    #比較可能なデータが存在するかチェック
    if len(df_all) < len(product_list) * 2:
        return [] 

    latest_date = df_all['scrape_date'].iloc[0]
    previous_data = df_all[df_all['scrape_date'] < latest_date]
    
    if previous_data.empty:
        return []

    previous_date = previous_data['scrape_date'].iloc[0]
    df_latest = df_all[df_all['scrape_date'] == latest_date]
    df_previous = previous_data[previous_data['scrape_date'] == previous_date]

    alert_messages = []

    #商品IDをキーに最新価格と前回価格を結合
    df_compare = pd.merge(
        df_latest[['product_id', 'product_name', 'current_price']],
        df_previous[['product_id', 'current_price']],
        on='product_id',
        suffixes=('_latest', '_previous')
    )

    df_compare['price_diff'] = df_compare['current_price_latest'] - df_compare['current_price_previous']

    for index, row in df_compare.iterrows():
        diff = row['price_diff']
        
        #変動額が閾値を超えているかチェック
        if abs(diff) >= price_change_threshold:
            direction = "Price decrease" if diff < 0 else "Price increase"
            
            message = (
                f"Price Alerts: {direction} detected for {row['product_name']}\n"
                f"  - Previous price: ${row['current_price_previous']:.2f}\n"
                f"  - Latest Price: ${row['current_price_latest']:.2f}\n"
                f"  - Variable amount: {diff:.2f} CAD"
            )
            alert_messages.append(message)

    return alert_messages

# --- 3. Gmail通知関数 (send_gmail_notification) ---
def send_gmail_notification(alert_messages, sender_email, app_password, recipient_email):
    """価格変動アラートメッセージをGmail経由で送信する関数"""
    
    if not alert_messages:
        return
        
    alert_subject = "【Price Alerts】"
    alert_body = "Price fluctuations have been detected for the following products:\n\n"
    alert_body += "\n---\n".join(alert_messages)
    alert_body += "\n\n---"

    #日本語を正しくエンコードし、メールの構造を作成
    message = MIMEText(alert_body, 'plain', 'utf-8')
    message['Subject'] = Header(alert_subject, 'utf-8')
    message['From'] = sender_email
    message['To'] = recipient_email

    try:
        #GmailのSMTPサーバーにSSL接続（セキュリティを確保）
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465) 
        server.login(sender_email, app_password)
        
        #メール送信
        server.sendmail(sender_email, recipient_email, message.as_string())
        server.quit() 
        
        print(f"\n✅ Gmail通知成功: {len(alert_messages)}件のアラートを送信しました。")
        
    except Exception as e:
        print(f"\n❌ Gmail通知失敗: メール送信中にエラーが発生しました。エラー詳細: {e}")

print("コア機能関数の定義が完了しました。")


# In[6]:


# --- トラッカーのメイン実行関数 ---
def main_tracker_run():
    """トラッカーの全処理（スクレイピング、履歴保存、変動検知、通知）を実行する"""
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_data = []
    
    print(f"\n=============================================")
    print(f"⏰ 自動価格トラッカー実行開始: {current_time}")
    print(f"=============================================")

    #1. すべての商品を巡回し、価格を取得 (スクレイピング)
    for product in product_list:
        product_id = product['id']
        url = product['url']
        
        #scrape_price関数を呼び出し
        price = scrape_price(url, product_id)
        
        new_data.append({
            'product_id': product_id,
            'product_name': product['name'],
            'scrape_date': current_time,
            'current_price': price
        })
        
        #サイトへの負荷軽減のため待機
        time.sleep(1.5) 
    
    df_new = pd.DataFrame(new_data)
    
    #2. 履歴CSVファイルの更新 (履歴保存)
    try:
        #既存の履歴を読み込み
        df_history = pd.read_csv(CSV_FILENAME)
        #新しいデータを結合（追記）
        df_updated = pd.concat([df_history, df_new], ignore_index=True)
    except FileNotFoundError:
        #初回実行時
        df_updated = df_new
        
    df_updated.to_csv(CSV_FILENAME, index=False)
    print(f"✅ データ収集と履歴保存完了: {len(df_new)}件のデータを追記。")

    #3. 価格変動のチェック (アラート検知)
    alert_list = check_price_change(CSV_FILENAME, PRICE_CHANGE_THRESHOLD)

    #4. アラートがあれば通知
    if alert_list:
        print("\n--- 🔔 価格変動アラート発報 (コンソール) 🔔 ---")
        for alert in alert_list:
            print(alert)
        print("---------------------------------")
        
        #Gmail通知実行
        send_gmail_notification(alert_list, GMAIL_SENDER_EMAIL, GMAIL_APP_PASSWORD, GMAIL_RECIPIENT_EMAIL)
    else:
        print("\n✅ 価格変動は検知されませんでした。")

    print(f"\n=============================================")
    print(f"🏁 自動価格トラッカー実行終了")
    print(f"=============================================")

# --- メイン関数の実行 ---
main_tracker_run() #トラッカーを起動トリガー


# In[ ]:




