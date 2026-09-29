# 20-giftwrap（礼品包装纸）

Giftwrap — 盒体展开近似面积（含重叠余量系数）

## 启动

```bash
docker compose up --build
```

| 入口 | 地址 |
| --- | --- |
| 前端 | http://localhost:4900 |
| API | http://localhost:9900 |

## 主链

盒长宽高 + 出血(mm) → 包装纸面积 → 展开示意

口径 `bleed_then_overlap:v1`：出血先逐边外扩几何，再乘折边系数；随单固化，改默认出血不回溯已写入用纸档。

## 技术栈

Python 3.12 + FastAPI + SQLite；Vue 3 + Vite + Nginx。
