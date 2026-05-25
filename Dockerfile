# 阶段 1：构建前端（生产 base /campus-qna/）
FROM node:20-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
ENV VITE_API_BASE=/campus-qna
RUN npm run build

# 阶段 2：Python API + 静态资源
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app/src
COPY api /app/api
COPY --from=frontend-build /frontend/dist /app/frontend/dist

# chroma_db、data、.env 由 docker-compose 挂载，不打包进镜像
RUN mkdir -p /app/chroma_db /app/data

ENV ROOT_PATH=/campus-qna

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
