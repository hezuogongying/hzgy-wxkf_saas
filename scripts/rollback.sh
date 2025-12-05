#!/bin/bash

# 自动回滚脚本
# 用法: ./scripts/rollback.sh [staging|production] [rollback-tag]

set -e

ENVIRONMENT=${1:-staging}
ROLLBACK_TAG=${2:-rollback-$(date +%Y%m%d-%H%M%S)}
NAMESPACE="wxkf-${ENVIRONMENT}"

echo "🔄 开始 ${ENVIRONMENT} 环境回滚..."
echo "📦 回滚标签: ${ROLLBACK_TAG}"

# 1. 检查当前部署状态
echo "🔍 检查当前部署状态..."
kubectl get deployment wxkf-${ENVIRONMENT} -n ${NAMESPACE} -o yaml > current-deployment.yaml

# 2. 获取前一个镜像
CURRENT_IMAGE=$(kubectl get deployment wxkf-${ENVIRONMENT} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.containers[0].image}')
echo "📦 当前镜像: ${CURRENT_IMAGE}"

# 3. 从deployment history获取前一个版本
echo "📋 获取部署历史..."
kubectl rollout history deployment/wxkf-${ENVIRONMENT} -n ${NAMESPACE}

# 4. 如果指定了回滚标签，使用该标签的镜像
if [ -n "$ROLLBACK_TAG" ] && [ "$ROLLBACK_TAG" != "rollback-$(date +%Y%m%d-%H%M%S)" ]; then
    PREVIOUS_IMAGE="ghcr.io/hezuogongying/hzgy-wxkf_saas:${ROLLBACK_TAG}"
    echo "🔄 使用指定回滚镜像: ${PREVIOUS_IMAGE}"
else
    # 获取前一个镜像标签
    PREVIOUS_REVISION=$(kubectl rollout history deployment/wxkf-${ENVIRONMENT} -n ${NAMESPACE} --revision=1 | grep "REVISION" | awk '{print $2}' | tail -n 2 | head -n 1)

    if [ -n "$PREVIOUS_REVISION" ]; then
        echo "🔄 回滚到版本: ${PREVIOUS_REVISION}"
        kubectl rollout undo deployment/wxkf-${ENVIRONMENT} -n ${NAMESPACE} --to-revision=${PREVIOUS_REVISION}
    else
        echo "❌ 无法找到前一个版本"
        exit 1
    fi
fi

# 5. 等待回滚完成
echo "⏳ 等待回滚完成..."
kubectl rollout status deployment/wxkf-${ENVIRONMENT} -n ${NAMESPACE} --timeout=300s

# 6. 健康检查
echo "🏥 执行健康检查..."
HEALTH_URL="https://${ENVIRONMENT}.wxkf.shoudu888.com/health"

for i in {1..30}; do
    if curl -f ${HEALTH_URL} >/dev/null 2>&1; then
        echo "✅ 健康检查通过 (尝试 $i/30)"
        break
    else
        echo "🔄 等待服务恢复... $i/30"
        sleep 10
    fi

    if [ $i -eq 30 ]; then
        echo "❌ 健康检查失败"
        exit 1
    fi
done

# 7. 创建回滚标签
echo "🏷️ 创建回滚标签..."
git tag ${ROLLBACK_TAG}
git push origin ${ROLLBACK_TAG}

# 8. 发送通知
echo "📢 发送回滚通知..."
if command -v curl >/dev/null 2>&1 && [ -n "${SLACK_WEBHOOK_URL}" ]; then
    curl -X POST -H 'Content-type: application/json' \
        --data "{
            \"text\": \"🔄 环境回滚完成\",
            \"attachments\": [{
                \"color\": \"warning\",
                \"fields\": [
                    {\"title\": \"环境\", \"value\": \"${ENVIRONMENT}\", \"short\": true},
                    {\"title\": \"回滚标签\", \"value\": \"${ROLLBACK_TAG}\", \"short\": true},
                    {\"title\": \"前镜像\", \"value\": \"${CURRENT_IMAGE}\", \"short\": false},
                    {\"title\": \"当前状态\", \"value\": \"健康检查通过\", \"short\": true}
                ]
            }]
        }" \
        ${SLACK_WEBHOOK_URL}
fi

# 9. 清理回滚后检查
echo "🔧 清理和最终检查..."
kubectl get pods -n ${NAMESPACE} -l app=wxkf-${ENVIRONMENT}
kubectl get service -n ${NAMESPACE}
kubectl get ingress -n ${NAMESPACE}

echo "✅ ${ENVIRONMENT} 环境回滚完成!"
echo "🌐 服务地址: https://${ENVIRONMENT}.wxkf.shoudu888.com"

# 10. 性能检查
echo "📊 执行性能检查..."
for i in {1..5}; do
    curl -w "@curl-format.txt" -o /dev/null -s ${HEALTH_URL}
    sleep 2
done

echo "🎉 回滚流程全部完成!"