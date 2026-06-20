
cmd-start =
    Hello! Thank you for using this bot. Available commands:

    • /donate_1: donate 1 star.
    • /donate_25: donate 25 stars.
    • /donate_50: donate 50 stars.
    • /donate <number>: donate <number> stars.
    • /paysupport: help with purchases.
    • /refund: refund a payment.

custom-donate-input-error = Please enter the amount in the format <code>/donate NUMBER</code>, where NUMBER is between 1 and 2500 inclusive.

invoice-title = Voluntary Donation
invoice-description =
    {$starsCount ->
        [one] {$starsCount} star
       *[other] {$starsCount} stars
}

pre-checkout-failed-reason = No more room for money 😭

cmd-paysupport =
    If you want to refund a purchase, use the /refund command

refund-successful =
    Refund completed successfully. The spent stars have already been returned to your Telegram account.

refund-no-code-provided =
    Please enter the command <code>/refund CODE</code>, where CODE is the transaction ID.
    You can see it after completing a payment, as well as in the "Stars" section of the Telegram app.

refund-code-not-found =
    This purchase code was not found. Please check the entered data and try again.
    Note that you can only refund stars for transactions made in this bot.

refund-already-refunded =
    A refund has already been processed for this purchase.

payment-successful =
    <b>Thank you so much!</b>

    Your transaction ID:
    <code>{$id}</code>

    Save it in case you need to refund in the future 😢

invoice-link-text =
    Use <a href="{$link}">this link</a> to donate 1 star.
