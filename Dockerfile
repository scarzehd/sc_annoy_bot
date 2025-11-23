FROM python:3.10
WORKDIR /usr/local/app

ENV DISCORD_BOT_TOKEN=""

COPY . .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN echo DISCORD_BOT_TOKEN=$DISCORD_BOT_TOKEN > .env

CMD ["python3", "bot.py"]