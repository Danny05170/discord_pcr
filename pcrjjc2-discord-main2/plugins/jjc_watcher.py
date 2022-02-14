from utils.pcrclient import pcrclient, ApiException
from asyncio import Lock
from copy import deepcopy
from traceback import format_exc
from utils.playerpref import decryptxml
from utils.sender import *
from discord.ext import tasks
from bot import bot
from datetime import datetime , timedelta
import pandas as pd 
import aiocron
import os
import json
import time 
import discord
from collections import defaultdict

_config = None
_binds = None
enemy_chanel = None
_cache = None
qlck = Lock()
lck = Lock()
_clients = {}

async def query(id: str, client):
    async with qlck:
        while client.shouldLogin:
            await client.login()
        res = (await client.callapi('/profile/get_profile', {
            'target_viewer_id': int(id)
        }))
        return res['user_info']


def initialize(config):
    global _config, _binds, _cache, _clients  ,enemy_chanel , role_dict_11, role_dict_33,super_user
    super_user= ['714144621978189924','436178879497895936','380898248652750849','296860596349960192','344206501243781121']
    role_dict_11 ={ "1" : "1v1 (１)" , 
    "2" : "1v1 (２)" , 
    "3" : "1v1 (３)" , 
    "4" : "1v1 (４)" , 
    "5" : "1v1 (５)" ,
    "6" : "1v1 (６)" ,
    "7" : "1v1 (７)" ,
    "8" : "1v1 (８)" ,
    "9" : "1v1 (９)" ,
    "10" : "1v1 (１０)" ,
    "11": "1v1 (１１)", 
    "12": "1v1 (１２)", 
    "13": "1v1 (１３)", 
    "14": "1v1 (１４)", 
    "15": "1v1 (１５)", 
    "16": "1v1 (１６)", 
    "17": "1v1 (１７)", 
    "18": "1v1 (１８)", 
    "19": "1v1 (１９)", 
    "20": "1v1 (２０)", 
    }
    role_dict_33 ={ "1" : "3v3 (１)" , 
    "2" : "3v3 (２)" , 
    "3" : "3v3 (３)" , 
    "4" : "3v3 (４)" , 
    "5" : "3v3 (５)" ,
    "6" : "3v3 (６)" ,
    "7" : "3v3 (７)" ,
    "8" : "3v3 (８)" ,
    "9" : "3v3 (９)" ,
    "10" : "3v3 (１０)" ,
    "11": "3v3 (１１)", 
    "12": "3v3 (１２)", 
    "13": "3v3 (１３)", 
    "14": "3v3 (１４)", 
    "15": "3v3 (１５)", 
    "16": "3v3 (１６)", 
    "17": "3v3 (１７)", 
    "18": "3v3 (１８)", 
    "19": "3v3 (１９)", 
    "20": "3v3 (２０)", 
    }
    _config = config
    if not os.path.exists(_config['binds_file']):
        with open(config['binds_file'], 'w') as f:
            json.dump({}, f)
    if not os.path.exists(_config['enemy_chanel']):
        with open(config['enemy_chanel'], 'w') as f:
            json.dump({}, f)        
    with open(config['binds_file'], 'r') as f:
        _binds = json.load(f)
    with open(config['enemy_chanel'], 'r') as f:
        enemy_chanel = json.load(f)     
    _cache = {}
    for server in config['playerprefs']:
        acinfo = decryptxml(config['playerprefs'][server])
        _clients[server] = pcrclient(acinfo['UDID'],
                                     acinfo['SHORT_UDID'],
                                     acinfo['VIEWER_ID'],
                                     acinfo['DL_BDL_VER'].decode(),
                                     '' if acinfo['TW_SERVER_ID'] == '1' else acinfo['TW_SERVER_ID'],
                                     _config['proxy'])
      #  print('TW-{} client started'.format(server))


bot.remove_command('help')


@bot.command(name='help')
async def _jjc_help(ctx):
    _sv_help = '''[bind uid server] 綁定競技場排名變動推送，默認雙場均啟用，僅排名降低時推送
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
#e  >>返回你仇家現在兩個p 場的位置 方便你在裡面卡秒時 跟踪仇家
#delete_enemy enemyid 
#set enemyid >>把enemy id 跟頻道綁定
#unset enemyid >>把enemy id 跟頻道解綁'''
    await ctx.send(_sv_help)

#@aiocron.crontab('0 5 * * *') ###inital climb-up time
#async def cornjob1():  
  #  for set_id in enemy_chanel.keys():
      #  print( enemy_chanel[set_id]   )
     #   enemy_chanel[set_id]['11_time'] = 0
     #   enemy_chanel[set_id]['33_time'] = 0
   # save_enemy_chanel()    

@bot.command(name='here')
async def get_enemy_channel_infol(ctx, *args):
    try :
        here_channel_id = [k for k,v in enemy_chanel.items() if v['gid'] == ctx.channel.id]
        here_channel_id= here_channel_id[0]
        now = datetime.now()
        time = now.strftime("%H:%M:%S")
        res = await query(here_channel_id, _clients['4'])
        last_login = res['last_login_time']
        last_login = datetime.fromtimestamp(last_login).strftime("%B %d, %Y %H:%M:%S")
    #    msg.append(  f'''{res['user_name']}:\n競技場排名：{res["arena_rank"]}\n公主競技場排名：{res["grand_arena_rank"]} \n最後上線時間：{last_login}\n━━━━━━━━━━━━━━━'''  )
        await ctx.send(f'''{res['user_name']}\nID :{here_channel_id}\nTime:{time}\n競技場排名：{res["arena_rank"]}\n公主競技場排名：{res["grand_arena_rank"]} \n最後上線時間：{last_login}\n━━━━━━━━━━━━━━━''')
    except:
        await ctx.send(str('搜尋不到這頻道相應的玩家')  )  

@bot.command(name='set')
async def get_channel(ctx, *args):
    async with lck:
        uid = str(ctx.author.id)
        expire =  _binds[uid].get('expire', "1999-01-04")  
        expire  = datetime.strptime(str(expire),'%Y-%m-%d')
        if datetime.now() > expire :
            return await ctx.send('該為付費內容 請聯絡Bot管理員')
        set_id = args[0]
    try:
        res = await query(set_id, _clients['4'])
        channel = bot.get_channel(ctx.channel.id)
        if set_id in enemy_chanel :
            await ctx.send(str('該id已跟某channel鎖定')  )
        else:    
            enemy_chanel[set_id] = {
                'name': res["user_name"],
                'gid': ctx.channel.id,
                "33": 0,
            }
            save_enemy_chanel()
            now_name  =res["user_name"]
            now_name = f"{now_name} 0"
            await channel.edit(name=now_name)
            msg = f'{res["user_name"]} 與頻道綁定成功'
            await ctx.send(str(msg)  )
    except :
        await ctx.send(str('沒有這玩家')  )        
   # for channel in ctx.guild.channels:
     #   if channel.name == given_name:
      #      wanted_channel_id = channel.id

  #  await ctx.send(channel.id) # this is just to check \

@bot.command(name='unset')
async def unset_channel(ctx, *args):
    async with lck:
        set_id = args[0]
        enemy_chanel.pop(set_id, None)
        save_enemy_chanel()
        msg = f'成功解除綁定'
        await ctx.send(str(msg)  )

#@tasks.loop(seconds=1)  #1823

@tasks.loop(seconds=110)
async def check_name():
    bind_enemy = {}
    async with lck:
        bind_enemy = deepcopy(enemy_chanel)
    for set_id in bind_enemy.keys():
        old_split_length= 0
        res = await query(set_id, _clients['4'])
        now_11 =res["arena_rank"] 
        now_33 =res["grand_arena_rank"]
        now_name  =res["user_name"]
        now_name = f"{now_name} {now_33}"
        try:
            channel = await bot.fetch_channel(enemy_chanel[set_id]['gid'])
         #  channel = bot.get_channel(int(bind_enemy[set_id]['gid']))
            old_name = str(channel)
         #   print( 'old_name',  old_name  )
            now_split_length = len( now_name.split(" ")[-1])    +1
          #  print( 'now_split_length', now_split_length   )
           # old_split_length = len(old_name.split("-")[-1]) + len( old_name.split("-")[-2]   ) +1  #-1 is 33 , -2 is 11 rank
            old_split_length = len(old_name.split("-")[-1]) +1
         #   print(  'old_split_length', old_split_length   )
            now_name_split = now_name[:len(now_name)- now_split_length]
          #  print(  now_name_split  )
            old_name_split =  old_name[:len(old_name)- old_split_length]
      #      print( now_name_split   )
       #     print( old_name_split   )
         #   print(  old_name_split  )
          #  old11 =  int(old_name.split("-")[-2] )
            old33 =  int(old_name.split("-")[-1] )
            if now_name.lower() != old_name.lower() :
                await channel.edit(name=now_name)
                if now_name_split.lower().replace(u'\u3000',u'').strip() != old_name_split.lower().replace("-", "".strip() ) :
                #    print(  'now_name_split.lower()', now_name_split.lower().replace(u'\u3000',u' ').strip()  )
                #    print(  'old_name_split.lower()', old_name_split.lower().replace("-", "".strip()   )  )
                    msg = f'{ old_name_split } 已改名至 {now_name_split}, channel名同時更新'
                    await channel.send(str(msg)  )
           # if now_11 != old11 :
             #   msg = f'11排名發生變化 {old11}>>{now_11},變動了{old11- now_11}名'
              #  await channel.send(str(msg)  )
            if now_33 != old33 :  
                msg = f'33排名發生變化 {old33}>>{now_33},變動了{old33- now_33}名'
                await channel.send(str(msg)  )      
        except:
            print(f'查詢出錯，{now_name}')

check_name.start()

@check_name.before_loop
async def before_myfunctionname():
    await bot.wait_until_ready()

@bot.command(name='bind')
async def on_arena_bind(ctx, dc_id : str, pcr_id: str, expire: int):
    """
        ctx: discord context
        pcr_id : 
    """
    super_uid = str(ctx.author.id)
    if super_uid in super_user:
        expire = datetime.now() + timedelta(days=expire*30)
        expire = expire.strftime("%Y-%m-%d")
        server = "4"
        uid = dc_id.replace('<@!','').replace('>','').replace('<@','')
        print(uid)
        try:
            res = await query(pcr_id, _clients[server])
        except:
            return await ctx.send("未查詢到九碼,綁定失敗!")
        async with lck:
            last = _binds[uid] if uid in _binds else None   
            expire_date = expire
            if uid not in  _binds :
                enemy= []
            else:    
                enemy =  _binds[uid].get('enemy',[])  
            if last is None: #1st buy and no uid in database
                next_data = [(server, pcr_id)]
            elif [server, pcr_id] in last['data']:  ###續費 or 1st buy but already have uid in database
                next_data = last['data']
            else:
                next_data = last['data'] + [(server, pcr_id)] ###add new sub-account
                expire_date = _binds[uid]['expire'] 
            if uid in  _binds :   ### add more account 
                _binds[uid] = {
                    'uid': uid,
                    'gid': ctx.channel.id,
                    'expire': expire_date ,
                    '11': True,
                    '33': True,
                    'data': next_data,
                    'enemy': enemy,
                    'is_private': last is not None and last['is_private'],
                    '11_group' :   _binds[uid]['11_group']   ,
                    '33_group' :   _binds[uid]['33_group'] 
                }
                save_binds()
            else: ### first bind 
                _binds[uid] = {
                    'uid': uid,
                    'gid': ctx.channel.id,
                    'expire':expire  ,
                    '11': True,
                    '33': True,
                    'data': next_data,
                    'is_private': last is not None and last['is_private'],
                    '11_group' :   res["arena_group"]   ,
                    '33_group' :   res["grand_arena_group"]
                }
                save_binds()   
            print_expire = _binds[uid]['expire']    
        await ctx.send(f'競技場綁定成功,到期日為{print_expire}')


@bot.command(name='enemy')
async def add_enemy(ctx, pcr_id: str, server: str):
    """
        ctx: discord context
        pcr_id : 
    """
    uid = str(ctx.author.id)
    expire =  _binds[uid].get('expire', "1999-01-04")  
    expire  = datetime.strptime(str(expire),'%Y-%m-%d')
    if datetime.now() > expire :
        return await ctx.send('該為付費內容 請聯絡Bot管理員')
    if server not in _clients:
        return await ctx.send("不支持查詢該服務器")
    try:
        res = await query(pcr_id, _clients[server])
    except:
        return await ctx.send("未查詢到九碼,綁定失敗!")
    if   _binds[uid].get('enemy') :
        enemy_len = len (    _binds[uid]['enemy']    )
        if enemy_len > 5:
            return await ctx.send("綁定敵人數已經有5個 請先刪除")
        if pcr_id in  _binds[uid]['enemy']  :
            return await ctx.send("你已經綁定了此人 你還想綁 !? 真的哪麼恨??")    
        _binds[uid]['enemy'].append(  pcr_id  )
        save_binds()
    if not  _binds[uid].get('enemy') :
        enemy_list = []
        enemy_list.append(  pcr_id  ) 
        _binds[uid]['enemy'] = enemy_list
        save_binds()
    await ctx.send('敵人競技場綁定成功')    

@bot.command(name='11')
async def check_11(ctx, *args):
    uid = str(ctx.author.id)
    expire =  _binds[uid].get('expire', "1999-01-04")  
    expire  = datetime.strptime(str(expire),'%Y-%m-%d')
    if datetime.now() > expire :
        return await ctx.send('該為付費內容 請聯絡Bot管理員')
    if len(args)==1:
        if "@" in str(args[0]) :
            uid = str(args[0]).replace('<@','').replace('>','').replace('!','') 
          #  print('uid',uid)
    else:
        uid = str(ctx.author.id)
    group_11 = _binds[uid]['11_group']
    msg= []    
    await ctx.send('loading...' )  
    dataframe_11 = pd.DataFrame(_binds.values()) 
    dataframe_11 = dataframe_11[dataframe_11['11_group']==group_11]
    for index, row in dataframe_11.iterrows():
       try:
           peace_11 = row['11_peace']
       except:
           peace_11 = False
       check_uid=  list(row['data']) 
       if check_uid :
           usder_id = check_uid[0][1]
           res = await query(usder_id, _clients['4'])
       else:
           continue 
       try :
        member = await ctx.guild.fetch_member(str(row['uid'].replace("fake","")))
        member_name = member.nick
        if member_name is None :
            member = await bot.fetch_user(str(row['uid'].replace("fake","")))
            member_name= member.display_name
       except :
           member_name = ""
       if peace_11 ==True: 
            msg.append( (int(res["arena_rank"]),f'~~{res["user_name"]}~~' , "【" + str(member_name) + "】" ))     
       else:    
           msg.append( (int(res["arena_rank"]),f'{res["user_name"]}' , "【" + str(member_name) + "】" ))     
    msg = sorted(msg, key=lambda x: x[0])
    msg = [ str(x) for x in msg  ]
    joined_string = "\n".join(msg)
  #  print( str(joined_string)  )
    await ctx.send(str(joined_string)  )   

   
@bot.command(name='33')
async def check_33(ctx, *args):
    uid = str(ctx.author.id)
    expire =  _binds[uid].get('expire', "1999-01-04")  
    expire  = datetime.strptime(str(expire),'%Y-%m-%d')
    if datetime.now() > expire :
        return await ctx.send('該為付費內容 請聯絡Bot管理員')
    if len(args)==1:
        print( args   )
        if "@" in str(args[0]) :
            uid = str(args[0]).replace('<@','').replace('>','').replace('!','') 
    else:
        uid = str(ctx.author.id)
    group_33 = _binds[uid]['33_group']
    msg= []    
    await ctx.send('loading...' )  
    dataframe_33 = pd.DataFrame(_binds.values()) 
    dataframe_33 = dataframe_33[dataframe_33['33_group']==group_33]
    for index, row in dataframe_33.iterrows():
       check_uid=  list(row['data']) 
       if check_uid :
           usder_id = check_uid[0][1]
           res = await query(usder_id, _clients['4'])
       else:
           continue  
       try:
        member = await ctx.guild.fetch_member(str(row['uid'].replace("fake","")))
        member_name = member.nick
        if member_name is None :
            member = await bot.fetch_user(str(row['uid'].replace("fake","")))
            member_name= member.display_name
       except:
           member_name = ""
       msg.append( (int(res["grand_arena_rank"]),f'{res["user_name"]}' , "【" + str(member_name) + "】" ))       
    msg = sorted(msg, key=lambda x: x[0])
    msg = [ str(x) for x in msg  ]
    joined_string = "\n".join(msg)
  #  print( str(joined_string)  )
    await ctx.send(str(joined_string)  )  


@bot.command(name='farm')
async def check_farm(ctx, *args):
    uid = str(ctx.author.id)
    if uid in super_user :
        farm_id = pd.read_excel('princess.xlsx')
        farm_id = farm_id[farm_id['FARM']==int(args[0])    ]      
        msg = [] 
        for index, row in farm_id.iterrows() :
         #   print(row)
            res = await query(row['ID'], _clients['4'])
            last_login = res['last_login_time']
            last_login = datetime.fromtimestamp(last_login).strftime("%B %d, %Y %H:%M:%S")
            msg.append( str(row['ID']) + " | " + row['LV'] + " | " + last_login    )
        msg = sorted(msg, key=lambda  x: x.split(' | ')[2] )
        msg = [ str(x) for x in msg  ]
        joined_string = "\n".join(msg)
    #  print( str(joined_string)  )
        await ctx.send(str(joined_string)  )  
    else:
        await ctx.send('你沒有農場')   

@bot.command(name='test')
async def enemy_check(ctx, *args):
    print(  'ctx.guild', ctx.guild  )
    member = await ctx.guild.fetch_member(742397309362503690)
    print(member.nick)
    for guild in bot.guilds:
        print(guild)
        print(guild.id)
  #  print(   ctx.author.name)

@bot.command(name='e')
async def enemy_check(ctx, *args):
    uid = str(ctx.author.id)
    expire =  _binds[uid].get('expire', "1999-01-04")  
    expire  = datetime.strptime(str(expire),'%Y-%m-%d')
    if datetime.now() > expire :
        return await ctx.send('該為付費內容 請聯絡Bot管理員')
    else:
        if _binds[uid].get('enemy') :
            enemys = _binds[uid]['enemy']     
        else:
            await ctx.send('您還未綁定enemy')
        msg = []    
        for enemy in enemys:
            res = await query(enemy, _clients['4'])
            last_login = res['last_login_time']
            last_login = datetime.fromtimestamp(last_login).strftime("%B %d, %Y %H:%M:%S")
            msg.append(  f'''{res['user_name']}:\nID:{enemy}\n競技場排名：{res["arena_rank"]}\n公主競技場排名：{res["grand_arena_rank"]} \n最後上線時間：{last_login}\n━━━━━━━━━━━━━━━'''  )
        await ctx.send('\n'.join(msg))


@bot.command(name='peace')
async def register(ctx, *args):
    peace_where = str(args[0]) 
    on_or_off = str(args[1]) 
    if "on" in on_or_off:
        peace_status = True
    else:
       peace_status = False  ###stop the off function first
    if peace_where =="11":
        uid = str(ctx.author.id)
        expire =  _binds[uid].get('expire', "1999-01-04")  
        expire  = datetime.strptime(str(expire),'%Y-%m-%d')
        if datetime.now() > expire :
            return await ctx.send('該為付費內容 請聯絡Bot管理員')
        else:
            pcr_id  = _binds[uid]['data'][0][1]
          #  res = await query(pcr_id, _clients['4'])
            group_11 = _binds[uid]['11_group']
            print(  'group_11' ,group_11   )
            if "enemy" in _binds[uid] :
                enemy = _binds[uid]['enemy']
            else:
                enemy = []
            _binds[uid] = {
                    'uid': uid,
                    'gid': ctx.channel.id,
                    "expire": _binds[uid]['expire'] ,
                    '11':  True ,
                    '33': True ,
                    'data': _binds[uid]['data'] ,
                    'is_private': False ,
                    '11_group' :   _binds[uid]['11_group']   ,
                    '33_group' :  _binds[uid]['33_group'] ,
                    'enemy' : enemy,
                    "11_peace" :True ###stop the off function first
                }
            save_binds()
            member = await ctx.guild.fetch_member(str(uid))
            member_name = member.nick
            tag_group = role_dict_11[str(group_11)] 
            role = discord.utils.get(member.guild.roles, name=tag_group) #Bot get guild(server) roles
            if member_name is None :
                member = await bot.fetch_user(uid)
                member_name= member.display_name  
            if peace_status ==True :   
                await ctx.send(f'<@&{str(role.id)}> \n【{member_name}】在此跟同區1vs1-{group_11}區大佬訂下互不打恊議 \n當你打指令#11時會看到我遊戲名字劃線 \n代表每日15點排名結算前夕，除了前3名的自己人外 \n本人絕對不會刺其他非前3名的自已人 \n故結算前夕本人不在前3名時也請各位大佬不要刺我\n違者將通報記點，感謝高抬貴手(跪')
            else:
                await ctx.send(f'請向bot管理員申請')    
                  #  await ctx.send(f'<@&{str(role.id)}> \n{member_name}跟同區1vs1-{group_11}區大佬除消互不打恊議 \n當你打指令#11時會看到我遊戲名字沒有劃線 \n根據各1vs1區的規則互打')    
                



@bot.command(name='query')
async def on_query_arena(ctx, *args):
    uid = str(ctx.author.id).replace("fake","")
    expire =  _binds[uid].get('expire', "1999-01-04")  
    expire  = datetime.strptime(str(expire),'%Y-%m-%d')
    if datetime.now() > expire :
        return await ctx.send('該為付費內容 請聯絡Bot管理員')
    else:
        delta = expire-datetime.now()
        await ctx.send(f"<@{uid}>" +" "+ f'到期日為{expire} 還有{delta.days}天') 
    if len(args)==1 and "@"  in str(args[0]) :
        uid = str(args[0]).replace('<@','').replace('>','').replace('!','') 
    else:
        uid = str(ctx.author.id) 
    data = _binds[uid]['data']     
    async with lck:
        if len(args) ==1 :
            args = args + ('4',)   
      #  expire =  _binds[uid].get('expire', "1999-01-04")  
      #  expire  = datetime.strptime(str(expire),'%Y-%m-%d')
     #   if datetime.now() > expire :
      #      return await ctx.send('該為付費內容 請聯絡Bot管理員')
     #   else:
       #     delta = expire-datetime.now()
         #   await ctx.send(f'到期日為{expire} 還有{delta.days}天')
       #     data = _binds[uid]['data']
    #   else:
        if len(args)>0 :
            if "@" not in  str(args[0]) :
                data = [(args[2 * i + 1], args[2 * i])
                for i in range(len(args) // 2)]         
    #  print(  data  )                         
        for (server, pcr_id) in data:
            if server not in _clients:
                continue
            try:
                now = datetime.now()
                time = now.strftime("%H:%M:%S")
                res = await query(pcr_id, _clients[server])
            #    print(res)
                last_login = res['last_login_time']
                last_login = datetime.fromtimestamp(last_login).strftime("%B %d, %Y %H:%M:%S")
            #    msg.append(  f'''{res['user_name']}:\n競技場排名：{res["arena_rank"]}\n公主競技場排名：{res["grand_arena_rank"]} \n最後上線時間：{last_login}\n━━━━━━━━━━━━━━━'''  )
                await ctx.send(f'''{res['user_name']}\nID :{pcr_id}\nTime:{time}\n競技場排名：{res["arena_rank"]}\n公主競技場排名：{res["grand_arena_rank"]} \n最後上線時間：{last_login}\n━━━━━━━━━━━━━━━''')
            except ApiException as e:
                await ctx.send(f'查詢出錯，{e}')

@bot.command(name='delete')
async def delete_arena_sub(ctx, *args):
    uid = str(ctx.author.id)
    expire =  _binds[uid].get('expire', "1999-01-04")  
    expire  = datetime.strptime(str(expire),'%Y-%m-%d')
    if datetime.now() > expire :
        return await ctx.send('該為付費內容 請聯絡Bot管理員')
    if "@" in str(args[0]) :
        uid = str(args[0]).replace('<@','').replace('>','').replace('!','') 
    else:
        uid = str(ctx.author.id)
    if len(args) == 1:
        async with lck:
            _binds.pop(uid)
            save_binds()
        return await ctx.send('刪除競技場訂閱成功')
 #   if len(args) % 2 != 0:
     #   return await ctx.send('格式輸入錯誤,請參考幫助')
    data = [(args[2 * i + 2], args[2 * i+1])
            for i in range(len(args) // 2)]     
    async with lck:
        for t in data:
            try:
                _binds[uid]['data'].remove(t)
            except:    
                _binds[uid]['data'].remove(list(t))
        save_binds()
    return await ctx.send('刪除競技場訂閱成功')


@bot.command(name='delete_enemy')
async def delete_enemy(ctx, pcr_id: str):
    uid = str(ctx.author.id)
    expire =  _binds[uid].get('expire', "1999-01-04")  
    expire  = datetime.strptime(str(expire),'%Y-%m-%d')
    if datetime.now() > expire :
        return await ctx.send('該為付費內容 請聯絡Bot管理員')
    if not _binds[uid].get('enemy') :
        await ctx.send('您還未綁定enemy')    
    if pcr_id in  _binds[uid]['enemy']:   
        _binds[uid]['enemy'].remove(pcr_id)
        save_binds()
        return await ctx.send('刪除enemy成功')
    else:
        return await ctx.send('沒有這個enemy')


@bot.command(name='querystatus')
async def send_arena_sub_status(ctx):
    uid = str(ctx.author.id)
    expire =  _binds[uid].get('expire', "1999-01-04")  
    expire  = datetime.strptime(str(expire),'%Y-%m-%d')
    if datetime.now() > expire :
        return await ctx.send('該為付費內容 請聯絡Bot管理員')
    else:
        info = _binds[uid]
        await ctx.send(f'''
    當前競技場綁定ID：{info['data']}
競技場訂閱：{'開啟' if info['11'] else '關閉'}
公主競技場訂閱：{'開啟' if info['33'] else '關閉'}
推送渠道: {'私聊' if info['is_private'] else '頻道'}''')


@tasks.loop(seconds=70)
async def on_arena_schedule():
    bind_cache = {}
    async with lck:
        bind_cache = deepcopy(_binds)

    for user in bind_cache:
        user_id = user
        bot.wait_until_ready()
        guild = bot.get_guild(729256891385118760) 
        print( 'guild', guild    )
        info = bind_cache[user]
        ### concate info and enemy list to one, then loop
        for (server, pcr_id) in info['data']:
            try:
                if info['11'] or  info['33'] :
                 #   print( "total time = " ,end_time -  beginning_time   )
                    res = await query(pcr_id, _clients[server])
                    name = res['user_name']
                    res = (res['arena_rank'], res['grand_arena_rank'],res['user_name'])
                    now = datetime.now()
                    if user not in _cache or pcr_id not in _cache[user]:
                        if user not in _cache:
                            _cache[user] = {}
                        _cache[user][pcr_id] = res
                        continue
                    last = _cache[user][pcr_id]
                    _cache[user][pcr_id] = res
                    if res[0] > last[0] and info['11']:
                        time = now.strftime("%H:%M:%S")
                        destination = {'user_id': info['uid']} if info['is_private'] else {'channel_id': _config['channel11']}
                        await send_msg(
                            **destination,
                            message=f'{time} : {name}的競技場排名發生變化：{last[0]}->{res[0]}，降低了{res[0]-last[0]}名。'
                                    + ('' if info['is_private']
                                    else at_person(user_id=user.replace("fake","")))  ### remove fake in ID
                        )

                    if res[1] > last[1] and info['33']:
                        time = now.strftime("%H:%M:%S")
                        destination = {'user_id': info['uid']} if info['is_private'] else {'channel_id': _config['channel33']}
                        await send_msg(
                            **destination,
                            message=f'{time} : {name}的公主競技場排名發生變化：{last[1]}->{res[1]}，降低了{res[1]-last[1]}名。' +
                            ('' if info['is_private'] else at_person(user_id=user.replace("fake","")))
                        )    
                    
                    if last[2] != name :
                     #   print("oldname", res[2]  ,name )
                        member = await guild.fetch_member(str(user_id))
                        group_11 = _binds[user_id]['11_group']
                        group_33 = _binds[user_id]['33_group']
                        tag_group = role_dict_11[str(group_11)] 
                        role11 = discord.utils.get(member.guild.roles, name=tag_group) #Bot get guild(server) roles
                        tag_group = role_dict_33[str(group_33)] 
                        role33 = discord.utils.get(member.guild.roles, name=tag_group) #Bot get guild(server) roles
                    #    print( 'role!!!!!!!!!!!!!!!' , role11.id   )
                        channel = await bot.fetch_channel(857205929274376232)
                        msg = f' <@&{str(role11.id)}> \n <@&{str(role33.id)}> \n{last[2]}已經改名為{name} ，同區大佬注意不要誤打 '
                        await channel.send(str(msg)  )
                        #await ctx.send(f'<@&{str(role.id)}> \n【{member_name}】在此跟同區1vs1-{group_11}區大佬訂下互不打恊議 \n當你打指令#11時會看到我遊戲名字劃線 \n代表每日15點排名結算前夕，除了前3名的自己人外 \n本人絕對不會刺其他非前3名的自已人 \n故結算前夕本人不在前3名時也請各位大佬不要刺我\n違者將通報記點，感謝高抬貴手(跪')
                     #   destination = {'user_id': info['uid']} if info['is_private'] else {'channel_id': _config['channel33']}
                    #    await send_msg(
                     #       **destination,
                     #       message=f'{time} : {name}的公主競技場排名發生變化：{last[1]}->{res[1]}，降低了{res[1]-last[1]}名。' +
                     #       ('' if info['is_private'] else at_person(user_id=user.replace("fake","")))
                     #   )     
            except:
                print(f'對{pcr_id}的檢查出錯\n{format_exc()}')

on_arena_schedule.start()

@bot.command('watch')
async def change_arena_sub(ctx, arena_type, state, *args):
    uid = str(ctx.author.id)
    expire =  _binds[uid].get('expire', "1999-01-04")  
    expire  = datetime.strptime(str(expire),'%Y-%m-%d')
    if datetime.now() > expire :
        return await ctx.send('該為付費內容 請聯絡Bot管理員')
    if state not in ['on', 'off'] or arena_type not in ['11', '33']:
        return await ctx.send('參數錯誤')
    uid = str(ctx.author.id)
   # async with lck:
    if uid not in _binds:
        await ctx.send('您該為付費內容 請聯絡Bot管理員')
    else:
        _binds[uid][arena_type] = state == 'on'
        save_binds()
        await ctx.send(f'{arena_type} {state}')

@bot.command(name='check_group')
async def check_group(ctx, *args):
    if len(args)==1:
        if "@" in str(args[0]) :
            uid = str(args[0]).replace('<@','').replace('>','').replace('!','') 
            pcr_id  = _binds[uid]['data'][0][1]
           # print(pcr_id)
        else:
            pcr_id = str(args[0])   
    else:
        uid  =str(ctx.author.id)    
        pcr_id  = _binds[uid]['data'][0][1]
    try:
        res = await query(pcr_id, _clients['4'])
        await ctx.send(f'''{res['user_name']} 台{4}:\n競技場組別：{res["arena_group"]}\n公主競技場組別：{res["grand_arena_group"]}''')
    except ApiException as e:
        await ctx.send(f'查詢出錯，{e}')
     
@bot.command(name='check_bind')
async def check_bind(ctx, *args):
    if len(args)==1:
        uid = str(args[0]).replace('<@','').replace('>','').replace('!','') 
    else:
        uid  =str(ctx.author.id)    
    if uid not in _binds:
        await ctx.send('該為付費內容 請聯絡Bot管理員')
    else:
        await ctx.send('有綁定競技場')


@bot.command(name='check_time')
async def check_bind(ctx, *args):
    if len(args)==1:
        uid = str(args[0]).replace('<@','').replace('>','').replace('!','') 
    else:
        uid  =str(ctx.author.id)    
    if uid not in _binds:
        await ctx.send('該id未bind')
    else:
        expire =  _binds[uid].get('expire', "沒有到期日")  
        await ctx.send(expire)

@bot.command('add_role')
async def on_member_join(ctx, *args): 
    if len(args)==1:
        uid = str(args[0]).replace('<@','').replace('>','').replace('!','') 
    else:
        uid  =str(ctx.author.id) 
    pcr_id  = _binds[uid]['data'][0][1]
    res = await query(pcr_id, _clients['4'])
    member = await ctx.guild.fetch_member(uid)
    role1 = role_dict_11[str(res["arena_group"])]  # Role to be autoroled when user joins
    rank = discord.utils.get(member.guild.roles, name=role1) #Bot get guild(server) roles
    await member.add_roles(rank)
    #  await ctx.send(f'{member} 成功加入了{role}')
    role2 = role_dict_33[str(res["grand_arena_group"])]  # Role to be autoroled when user joins
    rank = discord.utils.get(member.guild.roles, name=role2) #Bot get guild(server) roles
    await member.add_roles(rank)
    await ctx.send(f'{member} 成功加入了{role1} {role2}')

'''@bot.command('add_roles')
async def on_member_join2(ctx): 
    role_dict_11 ={ "1" : "1v1 (１)" , 
    "2" : "1v1 (２)" , 
    "3" : "1v1 (３)" , 
    "4" : "1v1 (４)" , 
    "5" : "1v1 (５)" ,
    "6" : "1v1 (６)" ,
    "7" : "1v1 (７)" ,
    "8" : "1v1 (８)" ,
    "9" : "1v1 (９)" ,
    "10" : "1v1 (１０)" ,
    "11": "1v1 (11)", 
    "12": "1v1 (12)", 
    "13": "1v1 (13)", 
    "14": "1v1 (14)", 
    "15": "1v1 (15)", 
    }
    role_dict_33 ={ "1" : "3v3 (１)" , 
    "2" : "3v3 (２)" , 
    "3" : "3v3 (３)" , 
    "4" : "3v3 (４)" , 
    "5" : "3v3 (５)" ,
    "6" : "3v3 (６)" ,
    "7" : "3v3 (７)" ,
    "8" : "3v3 (８)" ,
    "9" : "3v3 (９)" ,
    "10" : "3v3 (１０)" ,
    }
    #uid  =str(ctx.author.id) 
    for every_uid in _binds.keys():
        pcr_id  = _binds[every_uid]['data'][0][1]
        res = await query(pcr_id, _clients['4'])
        member = await ctx.guild.fetch_member(every_uid.replace("fake",""))
        role1 = role_dict_11[str(res["arena_group"])]  # Role to be autoroled when user joins
        rank = discord.utils.get(member.guild.roles, name=role1) #Bot get guild(server) roles
        await member.add_roles(rank)
        role2 = role_dict_33[str(res["grand_arena_group"])]  # Role to be autoroled when user joins
        rank = discord.utils.get(member.guild.roles, name=role2) #Bot get guild(server) roles
        await member.add_roles(rank)
        await ctx.send(f'{member} 成功加入了{role1} {role2}') 
        '''

@bot.command('update_bindsrerewrewrew')
async def update_binds(ctx): 
    for every_uid in _binds.keys():
        pcr_id  = _binds[every_uid]['data'][0][1]
        res = await query(pcr_id, _clients['4'])
        _binds[every_uid] = {
                'uid': every_uid,
                'gid': ctx.channel.id,
                '11':  True ,
                '33': True ,
                'data': _binds[every_uid]['data'] ,
                'is_private': False ,
                '11_group' :   res["arena_group"]   ,
                '33_group' :   res["grand_arena_group"],
                '11_rank' :   res["arena_rank"]   ,
                '33_rank' :   res["grand_arena_rank"]
            }
        save_binds()



@bot.command('private')
async def on_change_annonce(ctx, state):
    uid = str(ctx.author.id)
    await ctx.send('請向bot管理員申請')
    '''
    async with lck:
        if uid not in _binds:
            await ctx.send('您該為付費內容 請聯絡Bot管理員')
        else:
            _binds[uid]['is_private'] = state == 'on'
            save_binds()
            await ctx.send('send through {}'.format('private' if state == 'on' else 'channel'))
    pass'''

def save_binds():
    with open(_config['binds_file'], 'w') as f:
        json.dump(_binds, f, indent=4)

def save_enemy_chanel():
    with open(_config['enemy_chanel'], 'w') as f:
        json.dump(enemy_chanel, f, indent=4)
