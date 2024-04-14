# 交大兼任差勤及服務管理系統 - 自動簽到腳本
## Introduction
這支程式每天自動檢查月份，登入交大單一入口並前往兼任差勤及服務管理系統，將**"研究獎助生"->"實際參與研究計畫登錄"**中所有計畫掃一次，將可送審的紀錄全部勾選並送審，以防自己忘記上去簽到。  
每月超過10號才上去簽到的話就會被延至下個月造冊，也就是說你的薪水會晚一個月到。如果你是研究生，你待的整個Lab都會延到下個月才拿到薪水。  

因為學校麻煩的規定，所以浪費些時間寫了這東西，寫完才發現我只剩兩個月需要簽了，有點後悔== 所以希望它可以幫到更多喜歡忘記上去簽到的人或是懶人。這樣才可以發揮它的價值。  
有問題都可以mail我或發issue，我會盡量回覆。

## Environment
- Python 3.11

## Usage
1. 先準備一台不會關機的電腦，可以是實驗室電腦，裝好python3
2. 將這個repo clone到你的電腦
3. 開啟terminal，將路徑切到這個repo所在的目錄
   ```bash
   cd /path/to/repo
   ```
4. 執行下方指令下載所有需要的python package
   ```bash
   pip install -r requirements.txt
   ```
5. 輸入下方指令設定你的帳號密碼:
   ```bash
   export NYCU_ACCOUNT="你的學號"
   export NYCU_PASSWORD="你的密碼"
   ```
6. 執行下方指令開始自動簽到，如果不想要每天自動上去簽到可以將 `--run_schedule` 移除，如此就只會上去簽到這一次。
   ```bash
   python main.py --run_schedule
   ```