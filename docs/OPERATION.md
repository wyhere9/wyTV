# 运营说明

## 日常怎么维护

你只需要维护：

```text
config/channels.json
```

增加频道时复制一段：

```json
{
  "id": "channel-id",
  "name": "频道名称",
  "group": "分类",
  "enabled": true,
  "entries": [
    {"type": "webpage", "url": "https://官方直播页面", "region": "HK"},
    {"type": "youtube_search", "query": "频道名称 live official", "region": "US"}
  ]
}
```

## 自动维护逻辑

1. 按频道白名单读取入口。
2. 从网页 / YouTube / M3U / direct 发现候选源。
3. 用 ffprobe 检测是否可播放。
4. 同频道按地区排序：CN、HK、US、OTHER。
5. 写出一个 M3U：`output/live.m3u`。
6. GitHub Actions 自动提交更新。

## 为什么不是全网乱搜

全网乱搜容易采到盗版、付费盗链和失效源。这个项目采用白名单 + 官方入口 + 官方 YouTube 搜索方式，更稳、更安全、更容易长期维护。

## 想提高发现能力

可以增加：

- 更多官方直播页
- 官方 YouTube 频道搜索词
- 官方公开 M3U 地址
- 公开授权 FAST TV 平台入口

