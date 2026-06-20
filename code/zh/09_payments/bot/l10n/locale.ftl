
cmd-start =
    您好！感谢您使用本机器人。可用命令如下：

    • /donate_1: 捐赠 1 颗星。
    • /donate_25: 捐赠 25 颗星。
    • /donate_50: 捐赠 50 颗星。
    • /donate <数字>: 捐赠 <数字> 颗星。
    • /paysupport: 购买帮助。
    • /refund: 退款。

custom-donate-input-error = 请以 <code>/donate 数字</code> 的格式输入金额，其中数字在 1 到 2500 之间（含）。

invoice-title = 自愿捐赠
invoice-description =
    {$starsCount ->
        [one] {$starsCount} 颗星
       *[other] {$starsCount} 颗星
}

pre-checkout-failed-reason = 没有更多地方放钱了 😭

cmd-paysupport =
    如果您想退款，请使用 /refund 命令

refund-successful =
    退款成功。已花费的星星已返还到您的 Telegram 账户。

refund-no-code-provided =
    请输入命令 <code>/refund 代码</code>，其中代码是交易 ID。
    您可以在完成付款后看到它，也可以在 Telegram 应用的"星星"部分找到它。

refund-code-not-found =
    未找到该购买代码。请检查输入的数据并重试。
    请注意，您只能退还在此机器人中进行的交易的星星。

refund-already-refunded =
    该购买已经完成过退款。

payment-successful =
    <b>非常感谢！</b>

    您的交易 ID：
    <code>{$id}</code>

    请保存它，以防将来需要退款 😢

invoice-link-text =
    请使用<a href="{$link}">此链接</a>捐赠 1 颗星。
