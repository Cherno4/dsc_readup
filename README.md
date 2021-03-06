喋太郎
====

## Overview  
これは、DiscordのTTS Botです。

## Description
テキストチャンネルに入力されたテキストを元に合成音声APIを用いて音声ファイルを生成し、ボイスチャンネルで再生するBotです。読み上げ音声はVOICEROIDの結月ゆかり、弦巻マキ、月読アイ、水奈瀬コウと同じものを利用できます。

## Demo
https://www.nicovideo.jp/watch/sm34363918

ただし、この動画の喋太郎はバージョンが古いです。


## VS. 
Discordアプリケーションに組み込みであるTTS機能と違い、ボイスチャンネルに呼び出しておけば、居る間は自動で読み上げてくれます。また、辞書登録機能もあるので、読み間違いも是正していくことができます。

## Requirement
- python3.6.5
- discord.py 1.0.0a
- opus
- libffi
- ffmpeg --with-opus
- postgresql

その他、必要なライブラリは `requrire.txt` に記述してあります。  
それとは別に、以下のものが必要になります。
- Discord Bot Token
- docomo Developer support API key
    - 音声合成【Powerd by エーアイ】の利用申請を行なっているもの

## Usage
招待URLから、管理しているサーバへ正体してください。  
その後の使い方は、以下の記事に書いてあります。  
http://nonbiriyanonikki.hatenablog.com/entry/2019/02/09/122844

## Install
まず、Requirementにあるパッケージをインストールしてください。次に、  
```
$ pip install -r requrire.txt
```  
で必要なライブラリをインストールしてください。  
次に、postgresqlでデータベースを作成しておきます。  
次に、`token.json.example`を`token.json`にリネームします。内容を以下で指定したように適宜書き換えてください。
```
"docomo":"docomo Deveroper TOKEN",
"bot":"BOT TOKEN",
"manager_id":"BOT MANAGER DISCORD ID",
"db_user":"taro", #dbのユーザネーム
"password":"password", #dbのパスワード
"host":"localhost", #dbのアドレス
"db_name":"taro_dsc" #dbの名前
```
設定が終わったら、
```
$ python ctrl_db.py
```
を実行して、テーブルを作成します。
そのあとは、
```
$ python main.py
```
でBotが起動します。

## LICENSE
This software is released under the MIT License, see LICENSE.txt.  
images以下の画像についての著作権は、作者様に帰属します。