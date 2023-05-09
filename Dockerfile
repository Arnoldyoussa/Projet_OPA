FROM python:3.8
WORKDIR /exploit/Projet_OPA
COPY . .
RUN pip install -r Binance/requierement.txt -r Dash_Binance/requierement.txt
CMD python Dash_OPA.py