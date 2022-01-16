## 一旦

卒論提出用の状態

## 改修予定
- 不足しているコードをローカルから push 予定 😭
- mypy の型チェックが効いてないので修正予定 😭
- config.json の認証系のハードコーディングを修正予定 😭

## mongoDB の schema

- initial schema
  - 保存時の状態
```
{
  "_id": <tweet_id>,
  "tweet_data": <Dict[str, Any]>
}
```
- default schema
  - 位置情報追加された後
```
{
  "_id": <tweet_id>,
  "tweet_data": <Dict[str, Any]>,
  "location_name": <location_name> # such as "東京都練馬区~~"
}
```
- user description schema
  - initial schema から取り出された後
```
{
    "_id" : <ObjectId("~~~")>,
    "tweet_id" : <str>,
    "description" : <str>,
    "location_name" : <location_name>
    "user_id_str" : <str> # twitter での user id
}
```
- distinct tweet by user schema
  - userA: tweetA tweetA tweetA
    - count is 1
  - userB: tweetA tweetA tweetB
    - count is 2
  - total count is 1 + 2 = 3
```
{
    "_id" : ObjectId("~~"),
    "tweet_content" : <str>, # tweet
    "user_id_str" : <twitter user id>,
    "tweet_id" : <tweet id>
}
```

## 関連レポジトリ

- geo converter
  - 緯度軽度情報を地名に変換(python のバージョンの関係上、別コンテナ)
  - https://github.com/yutodotcat/twitter-research-geo-converter
