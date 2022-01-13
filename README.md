## とりあえず

卒論用の状態

## mongoDB の schema

- デフォルト(保存時)
```
{
  "_id": <tweet_id>,
  "tweet_data": <Dict[str, Any]>
}
```
- 位置情報追加された後
```
{
  "_id": <tweet_id>,
  "tweet_data": <Dict[str, Any]>,
  "location_name": <location_name> # like "東京都練馬区~~"
}
```
