FROM python:3.8
WORKDIR /app
COPY . /app
RUN pip install -r Binance/requierement.txt -r Dash_Binance/requierement.txt
EXPOSE 8050
CMD python Dash_OPA.py