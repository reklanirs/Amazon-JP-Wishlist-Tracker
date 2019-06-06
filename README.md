# Amazon JP Wishlist Price Drop Alerter

### Description

A simple wishlist price comparer and alerter for amazon japan. 

I always use it to track kinde book price drop.



The script will fetch the information like:

>  **￥3,658** 
>
> **価格が50%下がりました** 
>
> ほしい物リストに追加した時の価格は、￥7,314 でした

When the discount meets the threshold, it will alert you via email using ifttt.



----

### Usage

#### IFTTT

- Register an [ifttt](https://ifttt.com/discover) account.

- Create an applet.  You can use this [link](https://ifttt.com/create/if-receive-a-web-request-then-send-me-an-email?sid=6) directly and omit the following substep 1.

  1. if `Receive a web request` then `Send me an email`.  In **Event Name** of *Receive a web request*, you can use  `amazon_wish_list`.

  2. In subject, fill in

     ```
     Some items from your Amazon wishlist have discounts over {{Value2}}!
     ```

     or anything you like in email subject. `{{Value2}}` refers to your discount value.

  3. In body, fill in

     ```html
     Hello,<br>
     The following items on your wishlist are on sale:<br>
     {{Value1}}<br>
     <br>
     <br>
     What: {{EventName}}<br>
     When: {{OccurredAt}}<br>
     ```

  4. Click Save.

#### Script preparation

- Install requests and configparser for your python3:

  ```shell
  pip3 install configparser requests -U
  ```

- Fill in config.ini:

  ```
  [DEFAULT]
  wish_list = https://www.amazon.co.jp/hz/wishlist/ls/xxxxxxx
  # Set it to public if you don't know how to set cookie below.
  
  threshold = 30%
  # How much discount you want.
  
  cookie = x-wl-uid=1zSyAxxxxxxxxxxx
  # At Amazon JP wishlist page, log in, open chrome Developer Tools, refresh page, locate to the first link in Network tab, click it, in the right open 'Headers' page, copy the long long string behind 'cookie:'
  
  ifttt_webhook =  https://maker.ifttt.com/trigger/amazon_wish_list/with/key/<your_key>
  # format: https://maker.ifttt.com/trigger/{event}/with/key/your_key
  # get the <your_key> under account info from https://ifttt.com/services/maker_webhooks/settings. The string after https://maker.ifttt.com/use/
  ```

- Set up crontab task on your linux machine or VPS:

  ```
  crontab -e
  Then add the following line into it:
  @daily python3 /path/to/the/script/amazon_tracker.py
  ```

  