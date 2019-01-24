import re
import sys
import json
import psycopg2
import discord
import ctrl_db
from discord.ext import commands
from pydub import AudioSegment
from voice import knockApi


# Discord アクセストークン読み込み
with open('token.json') as f:
    df = json.load(f)

token = df["bot"]
manager = int(df["manager_id"])

# Speakerの配列

sps = ['sumire', 'maki', 'ai', 'kou']

# コマンドプレフィックスを設定
bot = commands.Bot(command_prefix='?')

# サーバ別に各値を保持
voice = {} # ボイスチャンネルID
channel = {} # テキストチャンネルID

#bot自身
client = discord.Client()
syabe_taro = client.user

@bot.event
# ログイン時のイベント
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

# 標準のhelpコマンドを無効化
bot.remove_command('help')

# helpコマンドの処理
@bot.command()
async def help(ctx):
    embed = discord.Embed(title='喋太郎', description='メッセージを読み上げるBotやで。')
    embed.add_field(name='?summon', value='わいをボイスチャンネルに呼ぶコマンドや。', inline=False)
    embed.add_field(name='?bye', value='わいをボイスチャンネルから追い出す時に使うんや。', inline=False)
    embed.add_field(name='?spk', value='声を変えるのに使うで。詳しくは、「?spk help」を見てほしい。', inline=False)

    await ctx.send(embed=embed)

# summonコマンドの処理
@bot.command()
async def summon(ctx):
    global voice
    global channel
    global msger
    global guild_id
    guild_id = ctx.guild.id # サーバIDを取得
    vo_ch = ctx.author.voice # 召喚した人が参加しているボイスチャンネルを取得
    # 召喚された時、voiceに情報が残っている場合
    if guild_id in voice:
        await voice[guild_id].disconnect()
        del voice[guild_id] 
        del channel[guild_id]
    # 召喚した人がボイスチャンネルにいた場合
    if not isinstance(vo_ch, type(None)): 
        voice[guild_id] = await vo_ch.channel.connect()
        channel[guild_id] = ctx.channel.id
        add_guild_db(ctx.guild)
        noties = notify(ctx)
        await ctx.channel.send('毎度おおきに。わいは喋太郎や。"?help"コマンドで使い方を表示するで')
        for noty in noties:
            await ctx.channel.send(noty)
        if len(noties) != 0:
            await ctx.channel.send('もし良ければ、製作者にポップコーンでも奢ってあげてください\rhttp://amzn.asia/5fx6FNv')
    else :
        await ctx.channel.send('あんたボイスチャンネルおらへんやんけ！')


# byeコマンドの処理            
@bot.command()
async def bye(ctx):
    global guild_id
    global voice
    global channel
    guild_id = ctx.guild.id
    # コマンドが、呼び出したチャンネルで叩かれている場合
    if ctx.channel.id == channel[guild_id]:
        await ctx.channel.send('じゃあの')
        await voice[guild_id].disconnect() # ボイスチャンネル切断
        # 情報を削除
        del voice[guild_id] 
        del channel[guild_id]

# speakerコマンドの処理
@bot.command()
async def spk(ctx, arg1):
    cand = arg1
    guild_id = ctx.guild.id

    if cand == 'help':
        embed = discord.Embed(title='?spk', description='声を変えるコマンド')
        embed.add_field(name='?spk yukari', value='ゆかりさんに変身', inline=False)
        embed.add_field(name='?spk maki', value='マキマキに変身', inline=False)
        embed.add_field(name='?spk ai', value='アイちゃんに変身', inline=False)
        embed.add_field(name='?spk kou', value='コウ先生に変身', inline=False)

        await ctx.send(embed=embed)
    else:
        # 呼び出したチャンネルでコマンドが叩かれた場合
        if ctx.channel.id == channel[guild_id]:
            if cand not in sps:
                # 引き数のキャラが存在しない場合
                await ctx.channel.send('おっと、そのキャラは未実装だ。すまねえ。')
            else if cand == 'ai':
                # アイの場合
                cand = 'anzu'
            else if cand == 'kou':
                # コウの場合
                cand = 'osamu'

            # 話者を設定
            ctrl_db.set_user(str(ctx.author.id), cand)

@bot.command()
async def notify(ctx, arg1, arg2):
    # 管理人からしか受け付けない
    if ctx.author.id != manager:
        return
    ctrl_db.add_news(arg1, arg2.replace("\\r", "\r"))


# メッセージを受信した時の処理
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    global voice
    global channel
    global msger
    global mess_time
    global mess_start
    mess_id = message.author.id # メッセージを送った人のユーザID

    #ギルドIDがない場合、DMと判断する
    if isinstance(message.guild, type(None)):
        # 管理人からのDMだった場合
        if message.author.id == manager:
            #コマンド操作になっているか
            if message.content.startswith("?"):
                await message.channel.send("コマンドを受け付けたで")
                await bot.process_commands(message) # メッセージをコマンド扱いにする
                return
            else:
                await message.channel.send("コマンド操作をしてくれ")
                return
        else:
            await message.channel.send("喋太郎に何かあれば、だーやまんの質問箱(https://peing.net/ja/gamerkohei?event=0)までお願いします。")
            return

    guild_id = message.guild.id # サーバID

    # ユーザ情報(speaker)を取得
    user = ctrl_db.get_user(str(mess_id))
    if isinstance(user, type(None)):
        # ユーザ情報がなければ、dbへ登録。話者はsumire
        ctrl_db.add_user(str(mess_id), message.author.name, 'sumire')
        user = ctrl_db.get_user(str(mess_id))

    # 召喚されていないか、コマンドだった場合
    if guild_id not in channel or message.content.startswith("?"):
        await bot.process_commands(message) # メッセージをコマンド扱いにする
        return

    str_guild_id = str(guild_id)

    # メッセージを、呼び出されたチャンネルで受信した場合
    if message.channel.id == channel[guild_id]:
        # 音声ファイルを再生中の場合再生終了まで止まる
        while (voice[guild_id].is_playing()):
            pass
        # メッセージを、音声ファイルを作成するモジュールへ投げる処理
        try :
            # URLを、"URL"へ置換
            get_msg = re.sub(r'http(s)?://([\w-]+\.)+[\w-]+(/[-\w ./?%&=]*)?', 'URL', message.content)
            knockApi(get_msg , user.speaker, str_guild_id)
        # 失敗した場合(ログは吐くようにしたい)
        except :
            await message.channel.send('ちょいとエラー起きたみたいや。少し待ってからメッセージ送ってくれな。')
            return 
        
        # 再生処理
        voice_mess = './sound/{}/msg.wav'.format(str_guild_id) # 音声ファイルのディレクトリ
        voice[guild_id].play(discord.FFmpegPCMAudio(voice_mess), after=lambda e: print('done', e)) # 音声チャンネルで再生
    
    await bot.process_commands(message)

def add_guild_db(guild):
    str_id = str(guild.id)
    guilds = ctrl_db.get_guild(str_id)

    if isinstance(guilds, type(None)):
        ctrl_db.add_guild(str_id, guild.name)

def notify(ctx):
    str_id = str(ctx.guild.id)
    notifis = ctrl_db.get_notify(str_id)
    newses = ctrl_db.get_news()
    list_noty = []

    for new in newses:
        is_notify = False
        for noty in notifis:
            if new.id == noty.news_id:
                is_notify = True
        if is_notify == False:
            list_noty.append('[{}] {}'.format(new.category, new.text))
            ctrl_db.add_notify(new.id, str_id)
    
    return list_noty

bot.run(token)