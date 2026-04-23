---
title: 特殊更新
description: my_chat_member 与 chat_member
---

# 特殊更新 {: id="special-updates" }

!!! info ""
    使用的 aiogram 版本：3.7.0

## 介绍 {: id="intro" }

在 Telegram 中，大多数事件都能被用户直接“看见”：普通消息、服务消息、回调、内联模式等。
但还有两类更新，主要是给机器人本身使用的：`my_chat_member` 和 `chat_member`。

过去，群组机器人经常处于“信息真空”状态：
开发者不得不频繁调用 `getChatMember` / `getChatAdministrators` 来确认权限变化，
还要做短时缓存以避免触发 Bot API 限制。

从 2021 年 3 月 Bot API v5.1 开始，情况明显改善：
Telegram 增加了 `my_chat_member` 与 `chat_member` 两种更新，
它们都包含同一种对象：
[ChatMemberUpdated](https://core.telegram.org/bots/api#chatmemberupdated)。

两者区别可以概括为：

- `my_chat_member`：与机器人自身相关的状态变化（私聊中被拉黑/解除拉黑、被加入群组、被移除、权限变化等）；
- `chat_member`：机器人所在群组/频道中，普通用户状态的变化（进群/退群、权限变化、管理员变更等）。

!!! warning "重要"
    默认情况下，Telegram 可能不会主动推送 `chat_member` 更新，
    需要在你的接收配置中显式启用。

## ChatMemberUpdated 对象 {: id="chatmemberupdated" }

`ChatMemberUpdated` 最关键的是“前后状态对比”：

- `from_user`：谁触发了这次变更；
- `old_chat_member`：变更前状态；
- `new_chat_member`：变更后状态；
- `invite_link`：可选，用户通过邀请链接加入时会出现。

例如，管理员把某个成员封禁：
`old_chat_member` 可能是 `member`，而 `new_chat_member` 变成 `kicked/banned`。

## my_chat_member 更新 {: id="my-chat-member" }

这类更新常用于：

- 判断用户是否在私聊中屏蔽/解除屏蔽机器人；
- 判断机器人是否被加入或移出群组/频道；
- 监听机器人权限变化并动态调整功能。

## chat_member 更新 {: id="chat-member" }

这类更新常用于：

- 处理成员加入/离开；
- 跟踪管理员升降级；
- 维护本地权限模型；
- 触发自动化审核与欢迎流程。

## 参考资料 {: id="extras" }

- 俄文原文：`/special-updates/`
- 英文页面：`/en/special-updates/`
