This is a notifier developed for Unilever BD, alerting on Out-of-Stock (OOS) and Addition-to-Stock (ATS) situations.
<br>
Tech Stack (Amazon Web Services - <strong>AWS</strong>):  ```DynamoDB``` ```Lambda``` ```CloudWatch``` ```Python Boto3``` ```smtplib```

### Output Notifications 
<p align="center">
<img width="775" alt="ushop" src="https://github.com/shithi30/Shopify-UShop-Portal-Hourly-OLA-Monitoring/assets/43873081/96e583da-1cec-43fc-8cbc-94abd88dfb13">
<img width="725" alt="ee1" src="https://github.com/shithi30/Shopify-UShop-Portal-Hourly-OLA-Monitoring/assets/43873081/c1398f0c-2c21-4a5e-a422-696a03432df1">
</p>

### Why DynamoDB?
- <strong>Key-Value Storage Design</strong> helped perform simple, de-duplicated insertions (+ updates) of SKUs.
- <strong>Flexible Schema</strong> helped handle offers, discounts - since not all SKUs have them live always.
- <strong>TTL (Time-to-Live)</strong> helped keep database updated, with periodical deletion of outdated SKU's data.
- <strong>CloudWatch Log Stream Monitoring</strong> triggered the <strong>Lambda Function</strong>, to notify (email) OOS/ATS-events.
- Enabling <strong>Global Secondary Index (GSI)</strong> helped query faster on timestamp (not primary key), to identify OOS.

