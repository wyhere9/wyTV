# IPTV Maintainer

一个用于**合法公开直播源**的自动维护平台：

- 维护频道白名单
- 从官方网页 / YouTube 官方直播 / 公共 M3U 入口自动发现直播源
- 检测可播放性
- 按地区优先级排序：CN → HK → US → OTHER
- 自动生成 `output/live.m3u`
- 通过 GitHub Actions 定时自动更新并提交结果

> 本项目不用于破解、绕过鉴权、抓取付费频道、盗链或规避 DRM。

## 快速使用

1. 上传整个项目到 GitHub。
2. 打开仓库 `Actions`，启用 workflow。
3. 手动运行 `Maintain IPTV M3U`，或等待定时任务。
4. 查看生成文件：

```text
output/live.m3u
```

## 你主要维护的文件

```text
config/channels.json
config/settings.json
```

### channels.json

频道目录、分类、官方入口都在这里维护。

```json
{
  "id": "nasa-tv",
  "name": "NASA TV",
  "group": "英语科学",
  "enabled": true,
  "entries": [
    {
      "type": "webpage",
      "url": "https://www.nasa.gov/live/",
      "region": "US"
    },
    {
      "type": "youtube_search",
      "query": "NASA live official",
      "region": "US"
    }
  ]
}
```

支持入口类型：

| type | 说明 |
|---|---|
| `webpage` | 从官方网页中提取 `.m3u8` |
| `youtube_search` | 搜索公开 YouTube 官方直播并用 yt-dlp 提取临时播放地址 |
| `m3u` | 从公开 M3U 入口读取 |
| `direct` | 直接使用已知 m3u8 |

## 地区优先级

默认：

```text
CN → HK → US → OTHER
```

同一个频道会按这个顺序写入 M3U。每个地区内部再按检测结果排序。

## GitHub Actions 定时

默认每 6 小时运行一次：

```yaml
- cron: "0 */6 * * *"
```

你可以在 `.github/workflows/maintain.yml` 修改。

## 本地运行

需要 Python 3.11+ 与 ffmpeg：

```bash
pip install -r requirements.txt
python -m iptv_maintainer maintain
```

## 输出

```text
output/live.m3u
output/results.json
output/report.md
```

## 合规原则

- 只采集公开网页、官方直播、公开视频平台直播、公开授权 M3U。
- 不绕过登录、会员、token、DRM、防盗链、地区限制。
- 不收录疑似盗版、付费频道盗链、破解源。
