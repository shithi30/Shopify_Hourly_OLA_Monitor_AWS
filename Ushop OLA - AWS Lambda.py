# import
import boto3
from boto3.dynamodb.conditions import Key, Attr
import smtplib
from email.mime.text import MIMEText
import os
import json

# lambda fn
def lambda_handler(event, context):
    
    # log
    print(event)
    for record in event["Records"]:
        if record["eventName"] == "INSERT":
            
            # EOF, report time
            eof = record["dynamodb"]["NewImage"]["sku"]["S"]
            if eof == "EOF":
                report_time = record["dynamodb"]["NewImage"]["report_time"]["S"]
                print("EOF, report_time identified.")
    
                # session
                dynamo_client = boto3.resource (
                    service_name = "dynamodb",
                    region_name = "ca-central-1",
                    aws_access_key_id = os.getenv("AWS_ACC"),
                    aws_secret_access_key = os.getenv("AWS_SEC")
                )
                
                # table
                ushop_tbl = dynamo_client.Table("ushop_ola")
                print("Session created, table selected.")
                
                # ATS
                ats_items = []
                items = ushop_tbl.scan(FilterExpression = Attr("report_time").eq(report_time) & Attr("previous_ola").eq(False))["Items"]
                for item in items: ats_items.append(item["sku"])
                print("ATS determined.")
                
                # OOS
                oos_items = ["EOF"]
                items = ushop_tbl.scan(FilterExpression = Attr("report_time").ne(report_time))["Items"]
                for item in items: oos_items.append(item["sku"])
                print("OOS determined.")
                
                # recency
                for key in oos_items: response = ushop_tbl.delete_item(Key={"sku": key})
                print("OOS deleted, database up-to-date.")
                
                # from, to, body
                sender_email = "shithi30@gmail.com"
                recver_email = ["shithi30@outlook.com"]
                oos = "&#9940 Out of Stock: <i>" + ", ".join(oos_items[1:]) + "</i><br>" if len(oos_items)> 1 else ""
                ats = "&#9989 Added to Stock: <i>" + ", ".join(ats_items) + "</i><br>" if len(ats_items) > 0 else ""
                print("Email body ready.")
                
                # object
                html_msg = MIMEText(oos + ats, "html")
                html_msg["Subject"] = "Ushop OOS + ATS ~ Full"
                html_msg["From"] = "Shithi Maitra"
                html_msg["To"] = ", ".join(recver_email)
                print("Email object ready.")
                
                # send
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(sender_email, os.getenv("EMAIL_PASS"))
                    if len(oos_items[1:]) + len(ats_items) > 1: server.sendmail(sender_email, recver_email, html_msg.as_string())
                print("Email notification sent.")

                # depart
                break
    
    # success
    return {
        "statusCode": 200,
        "body": json.dumps("Lambda function returned.")
    }
