#!/bin/sh
set -e

# ---------------- 配置 ----------------
# 镜像版本号，可通过第一个参数覆盖
VERSION=${1:-1.0.3}

# Docker 仓库地址
IMAGE=ghcr.io/hhq365/yfinance-api

# 是否推送镜像，可通过第二个参数覆盖
PUSH=${2:-true}

# 构建的平台
PLATFORMS="linux/amd64"

echo "🏷  Version: $VERSION"
echo "🛠️  Image: $IMAGE"
echo "🖥  Platforms: $PLATFORMS"
echo "🚀 Push: $PUSH"

PUSH_ARG=""
if [ "$PUSH" = "true" ]; then
  PUSH_ARG="--push"
fi

# ---------------- 构建 ----------------
docker buildx build \
  --platform ${PLATFORMS} \
  --cache-from=type=registry,ref=${IMAGE}:latest \
  -t ${IMAGE}:${VERSION} \
  -t ${IMAGE}:latest \
  --build-arg APP_VERSION=${VERSION} \
  $PUSH_ARG \
  --progress=plain \
  .

echo "✅ Build finished: $IMAGE:${VERSION}"