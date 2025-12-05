#!/bin/bash

# 创建Kubernetes密钥脚本
# 用法: ./scripts/create-secrets.sh [staging|production]

set -e

ENVIRONMENT=${1:-staging}
NAMESPACE="wxkf-${ENVIRONMENT}"

echo "🔐 创建 ${ENVIRONMENT} 环境的Kubernetes密钥..."

# 创建命名空间
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

# Staging环境密钥
if [ "$ENVIRONMENT" = "staging" ]; then
    echo "📝 创建staging环境密钥..."

    # 数据库密钥
    kubectl create secret generic wxkf-${ENVIRONMENT}-secrets \
        --from-literal=db-host="your-staging-db-host" \
        --from-literal=db-port="3306" \
        --from-literal=db-name="wxkf_saas_staging" \
        --from-literal=db-user="wxkf_staging" \
        --from-literal=db-password="your-staging-db-password" \
        --namespace=${NAMESPACE} \
        --dry-run=client -o yaml | kubectl apply -f -

    # Redis密钥
    kubectl create secret generic wxkf-${ENVIRONMENT}-secrets \
        --from-literal=redis-host="your-staging-redis-host" \
        --from-literal=redis-port="6379" \
        --from-literal=redis-password="your-staging-redis-password" \
        --namespace=${NAMESPACE} \
        --dry-run=client -o yaml | kubectl apply -f -

    # 微信服务商密钥
    kubectl create secret generic wxkf-${ENVIRONMENT}-secrets \
        --from-literal=suite-id="your-staging-suite-id" \
        --from-literal=suite-secret="your-staging-suite-secret" \
        --from-literal=provider-secret="your-staging-provider-secret" \
        --from-literal=provider-token="your-staging-provider-token" \
        --from-literal=provider-encoding-aes-key="your-staging-provider-encoding-aes-key" \
        --namespace=${NAMESPACE} \
        --dry-run=client -o yaml | kubectl apply -f -

# 生产环境密钥
elif [ "$ENVIRONMENT" = "production" ]; then
    echo "📝 创建生产环境密钥..."

    # 从环境变量读取敏感信息
    kubectl create secret generic wxkf-${ENVIRONMENT}-secrets \
        --from-literal=db-host="${PROD_DB_HOST}" \
        --from-literal=db-port="${PROD_DB_PORT}" \
        --from-literal=db-name="${PROD_DB_NAME}" \
        --from-literal=db-user="${PROD_DB_USER}" \
        --from-literal=db-password="${PROD_DB_PASSWORD}" \
        --from-literal=redis-host="${PROD_REDIS_HOST}" \
        --from-literal=redis-port="${PROD_REDIS_PORT}" \
        --from-literal=redis-password="${PROD_REDIS_PASSWORD}" \
        --from-literal=suite-id="${PROD_SUITE_ID}" \
        --from-literal=suite-secret="${PROD_SUITE_SECRET}" \
        --from-literal=provider-secret="${PROD_PROVIDER_SECRET}" \
        --from-literal=provider-token="${PROD_PROVIDER_TOKEN}" \
        --from-literal=provider-encoding-aes-key="${PROD_PROVIDER_ENCODING_AES_KEY}" \
        --namespace=${NAMESPACE} \
        --dry-run=client -o yaml | kubectl apply -f -

else
    echo "❌ 错误: 不支持的环境 '$ENVIRONMENT'"
    echo "⚡ 用法: $0 [staging|production]"
    exit 1
fi

# 创建Docker Registry密钥
kubectl create secret docker-registry ghcr-secret \
    --docker-server=ghcr.io \
    --docker-username=${GITHUB_ACTOR} \
    --docker-password=${GITHUB_TOKEN} \
    --namespace=${NAMESPACE} \
    --dry-run=client -o yaml | kubectl apply -f -

# 创建TLS证书密钥 (使用cert-manager)
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: wxkf-${ENVIRONMENT}-tls
  namespace: ${NAMESPACE}
spec:
  secretName: wxkf-${ENVIRONMENT}-tls
  dnsNames:
  - ${ENVIRONMENT}.wxkf.shoudu888.com
  issuerRef:
    name: letsencrypt-${ENVIRONMENT}
    kind: ClusterIssuer
EOF

echo "✅ ${ENVIRONMENT} 环境密钥创建完成!"
echo "🔍 检查密钥:"
kubectl get secrets -n ${NAMESPACE}