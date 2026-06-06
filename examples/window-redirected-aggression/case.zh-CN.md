# 窗外猫触发攻击

虚构用户输入：

```text
Use $cat-behavior-consult to assess this case:

我家 4 岁已绝育室内猫在客厅窗边看到一只户外猫。大约 20 秒后，它冲过来攻击我的小腿。它又咬又抓，其中一处咬伤破皮。这个月已经发生两次，每次都在同一扇窗附近。它大约 40 分钟后才平静下来。家里没有小孩，还有另一只猫，目前已经隔开。最近没有做过兽医检查。
```

预期 skill 行为：

1. 追问缺失的医学和事件细节。
2. 先给破皮咬伤的安全处理提醒。
3. 复述并确认 case summary 后，再进入完整 consult。
4. 检索 owner-directed aggression、redirected aggression、stress 和医学鉴别相关证据。
5. 有 web access 时，搜索相似公开真实案例。
6. 输出带引用的 consult，包括安全管理、行为改变方案和升级条件。
