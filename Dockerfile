FROM pytorch/pytorch:2.6.0-cuda12.4-cudnn9-runtime

ENV PYTERRIER_VERSION='5.7'
ENV PYTERRIER_HELPER_VERSION='0.0.7'

RUN apt-get update \
	&& apt-get install -y git openjdk-11-jdk \
	&& pip3 install python-terrier pandas jupyterlab runnb \
	&& python3 -c "import pyterrier as pt; pt.init(version='${PYTERRIER_VERSION}', helper_version='${PYTERRIER_HELPER_VERSION}');" \
	&& python3 -c "import pyterrier as pt; pt.init(version='${PYTERRIER_VERSION}', helper_version='${PYTERRIER_HELPER_VERSION}', boot_packages=['com.github.terrierteam:terrier-prf:-SNAPSHOT']);"

COPY requirements.txt .
#COPY inputs /workspace
COPY src /src

#WORKDIR /workspace

RUN apt-get update && apt-get install -y git

RUN pip install --no-cache-dir -r requirements.txt
#install QualT5 (pyterrier-quality)
RUN python -m pip install git+https://github.com/terrierteam/pyterrier-quality

#test
RUN python -c "import torch"

#run app
#CMD ["python","src/quality_scoring.py"]

ENTRYPOINT ["python","/src/quality_scoring.py"]