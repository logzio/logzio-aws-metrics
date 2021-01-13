FROM python:3.7-slim

ADD requirements.txt ./requirements.txt
ADD configuration ./configuration
ADD ./util/* ./util/
ADD ./cw_namespaces/* ./cw_namespaces/
ADD builder.py ./builder.py
ADD configuration_raw ./configuration_raw
RUN pip install -r requirements.txt && \
    rm requirements.txt
CMD python builder.py