from flask import Flask, render_template, request
import requests
import smtplib
import os
from dotenv import load_dotenv
import logging
import ssl

load_dotenv()

MY_EMAIL = os.getenv("MY_EMAIL")
MY_PASSWORD = os.getenv("MY_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
SMTP_SERVER = os.getenv("SMTP_SERVER")


posts = requests.get("https://api.npoint.io/c790b4d5cab58020d391").json()

app = Flask(__name__)


@app.route('/')
def get_all_posts():
    return render_template("index.html", all_posts=posts)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == "GET":
        return render_template("contact.html", msg_sent=False)
    else:
        data = request.form
        name = data["name"]
        email = data["email"]
        phone = data["phone"]
        message = data["message"]
        logging.basicConfig(level=logging.DEBUG)
        send_email(name=name, email=email, phone=phone, message=message)
        return render_template("contact.html", msg_sent=True)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = None
    for blog_post in posts:
        if blog_post["id"] == index:
            requested_post = blog_post
    return render_template("post.html", post=requested_post)


def send_email(name, email, phone, message):
    email_message = f"Subject:New Message\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage:{message}"
    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, port=587, timeout=120) as connection:
        logging.debug(f"Server Address: {SMTP_SERVER}")
        logging.debug(f"Server Port: {587}")
        try:
            connection.starttls(context=context)
            connection.login(user=MY_EMAIL, password=MY_PASSWORD)
            connection.sendmail(
                        from_addr=MY_EMAIL,
                        to_addrs=RECEIVER_EMAIL,
                        msg=email_message
            )
            logging.info("Email sent successfully!")
        except ConnectionRefusedError as e:
            logging.error(f"Connection to SMTP server failed: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
        finally:
            connection.close()


if __name__ == "__main__":
    app.run(debug=True, port=5001)
