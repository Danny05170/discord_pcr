# pcrjjc2 for Discord

本repo是根據[pcrjjc2](https://github.com/cc004/pcrjjc2)的discord機器人, 僅用於tw服，再進行優化的

[bind uid server] 綁定競技場排名變動推送，默認雙場均啟用，僅排名降低時推送
[query uid1 server1 uid2 server2 ...] 查詢競技場簡要信息
[watch 11/33 on/off] 打開或者關閉11或者33的推送
[private on/off] 啟用或關閉私聊推送
server: 1 2 3 4(台一~台四)
============下面用不太到===========
[delete] 刪除競技場排名變動推送綁定
[delete id1 server1 id2 server2 ...] 刪除指定競技場排名變動推送綁定
[querystatus] 查看排名變動推送綁定狀態
============新增功能===========
#11 返回與你同區競技場的戰友的排名  >>方便搞電梯，建議在各自的指揮室用
#33 返回與你同區公主競技場的戰友的排名  >>方便搞電梯，建議在各自的指揮室用
#check_group 返回你兩個p場的group number
#enemy enemyid 4 >>設立你的仇家list 我限定每人只可有set兩個仇家
#e  >>返回你仇家現在兩個p 場的位置 方便你在裡面卡秒時 跟蹤仇家
#delete_enemy enemyid 
#set enemyid >>把enemy id 跟頻道綁定
#unset enemyid >>把enemy id 跟頻道解綁


支持綁定一個用戶綁定多個PCR賬號以及擊劍自動提醒.

**本項目基於AGPL v3協議開源，由於項目特殊性，禁止基於本項目的任何商業行為**

## 用法說明
1. 首先獲得一個discord API的token
2. 覆制一份 /data/data/tw.sonet.princessconnect/sharedprefs/tw.sonet.princessconnect.v2.playerprefs.xml   **一般需要root**
    + 切換賬號會導致xml失效, 取出playerpref後,刪除再引繼:
        1. /data/data/tw.sonet.princessconnect/sharedprefs/tw.sonet.princessconnect.v2.playerprefs.xml
        2. /data/data/tw.sonet.princessconnect/files/savedData 文件夾

