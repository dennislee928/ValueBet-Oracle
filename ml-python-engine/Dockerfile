# ValueBet Oracle - ML Python Engine
# python:3.10-slim，複製模型與程式碼，啟動 Uvicorn
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data_pipeline.py train_model.py main.py ./
COPY data/ data/
COPY models/ models/

# 若 models/ 為空，執行時需先掛載或於 entrypoint 訓練
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
