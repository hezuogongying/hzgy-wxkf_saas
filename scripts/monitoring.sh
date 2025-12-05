#!/bin/bash

# 部署后监控脚本
# 用法: ./scripts/monitoring.sh [staging|production]

set -e

ENVIRONMENT=${1:-staging}
NAMESPACE="wxkf-${ENVIRONMENT}"
HEALTH_URL="https://${ENVIRONMENT}.wxkf.shoudu888.com"
DURATION=${2:-600}  # 默认监控10分钟

echo "📊 开始 ${ENVIRONMENT} 环境部署后监控..."
echo "⏱️  监控时长: ${DURATION} 秒"
echo "🌐 健康检查URL: ${HEALTH_URL}"

# 初始化监控指标
HEALTH_CHECKS=0
FAILED_CHECKS=0
START_TIME=$(date +%s)
END_TIME=$((START_TIME + DURATION))

# 创建监控报告
REPORT_FILE="deployment-monitor-$(date +%Y%m%d-%H%M%S).log"
echo "📝 监控报告: ${REPORT_FILE}" > ${REPORT_FILE}
echo "开始时间: $(date)" >> ${REPORT_FILE}
echo "环境: ${ENVIRONMENT}" >> ${REPORT_FILE}
echo "监控时长: ${DURATION} 秒" >> ${REPORT_FILE}
echo "---" >> ${REPORT_FILE}

# 主监控循环
while [ $(date +%s) -lt ${END_TIME} ]; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    REMAINING=$((END_TIME - CURRENT_TIME))

    echo "⏰ 监控中... (${ELAPSED}/${DURATION}s, 剩余: ${REMAINING}s)"

    # 健康检查
    if curl -f -s --max-time 10 ${HEALTH_URL}/health >/dev/null 2>&1; then
        HEALTH_CHECKS=$((HEALTH_CHECKS + 1))
        echo "✅ 健康检查通过 (${HEALTH_CHECKS})"
        echo "$(date): ✅ 健康检查通过" >> ${REPORT_FILE}
    else
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        echo "❌ 健康检查失败 (${FAILED_CHECKS})"
        echo "$(date): ❌ 健康检查失败" >> ${REPORT_FILE}

        # 连续失败检查时报警
        if [ $FAILED_CHECKS -ge 3 ]; then
            echo "🚨 连续3次健康检查失败，触发报警!"
            echo "$(date): 🚨 触发连续失败报警" >> ${REPORT_FILE}

            # 发送Slack通知
            if [ -n "${SLACK_WEBHOOK_URL}" ]; then
                curl -X POST -H 'Content-type: application/json' \
                    --data "{
                        \"text\": \"🚨 部署后监控报警\",
                        \"attachments\": [{
                            \"color\": \"danger\",
                            \"fields\": [
                                {\"title\": \"环境\", \"value\": \"${ENVIRONMENT}\", \"short\": true},
                                {\"title\": \"失败次数\", \"value\": \"${FAILED_CHECKS}\", \"short\": true},
                                {\"title\": \"服务URL\", \"value\": \"${HEALTH_URL}\", \"short\": false}
                            ]
                        }]
                    }" \
                    ${SLACK_WEBHOOK_URL}
            fi

            # 检查是否需要回滚
            if [ $FAILED_CHECKS -ge 5 ]; then
                echo "🔄 连续5次失败，建议执行回滚!"
                echo "$(date): 🔄 建议执行回滚" >> ${REPORT_FILE}

                # 自动回滚选项 (如果设置了AUTO_ROLLBACK=true)
                if [ "${AUTO_ROLLBACK}" = "true" ]; then
                    echo "🔄 开始自动回滚..."
                    ./scripts/rollback.sh ${ENVIRONMENT}
                    break
                fi
            fi
        fi
    fi

    # 资源使用情况检查
    if [ $((ELAPSED % 60)) -eq 0 ]; then  # 每分钟检查一次
        echo "📊 检查资源使用情况..."

        # CPU使用率
        CPU_USAGE=$(kubectl top pods -n ${NAMESPACE} -l app=wxkf-${ENVIRONMENT} --no-headers | awk '{s+=$2} END {print s}')

        # 内存使用率
        MEMORY_USAGE=$(kubectl top pods -n ${NAMESPACE} -l app=wxkf-${ENVIRONMENT} --no-headers | awk '{s+=$3} END {print s}')

        # Pod状态
        READY_PODS=$(kubectl get pods -n ${NAMESPACE} -l app=wxkf-${ENVIRONMENT} --no-headers | grep "Running" | wc -l)
        TOTAL_PODS=$(kubectl get pods -n ${NAMESPACE} -l app=wxkf-${ENVIRONMENT} --no-headers | wc -l)

        echo "📈 资源使用 - CPU: ${CPU_USAGE}m, 内存: ${MEMORY_USAGE}Mi, Pods: ${READY_PODS}/${TOTAL_PODS}"
        echo "$(date): 📈 资源使用 - CPU: ${CPU_USAGE}m, 内存: ${MEMORY_USAGE}Mi, Pods: ${READY_PODS}/${TOTAL_PODS}" >> ${REPORT_FILE}

        # 资源使用报警
        if [ "${CPU_USAGE%.*}" -gt 1000 ]; then  # CPU超过1核
            echo "⚠️  CPU使用率过高: ${CPU_USAGE}m"
            echo "$(date): ⚠️  CPU使用率过高: ${CPU_USAGE}m" >> ${REPORT_FILE}
        fi

        if [ "${MEMORY_USAGE%.*}" -gt 2048 ]; then  # 内存超过2GB
            echo "⚠️  内存使用率过高: ${MEMORY_USAGE}Mi"
            echo "$(date): ⚠️  内存使用率过高: ${MEMORY_USAGE}Mi" >> ${REPORT_FILE}
        fi

        if [ $READY_PODS -lt $TOTAL_PODS ]; then
            echo "⚠️  有Pod未就绪: ${READY_PODS}/${TOTAL_PODS}"
            echo "$(date): ⚠️  有Pod未就绪: ${READY_PODS}/${TOTAL_PODS}" >> ${REPORT_FILE}
        fi
    fi

    sleep 30  # 每30秒检查一次
done

# 监控结束总结
TOTAL_CHECKS=$((HEALTH_CHECKS + FAILED_CHECKS))
SUCCESS_RATE=$(echo "scale=2; $HEALTH_CHECKS * 100 / $TOTAL_CHECKS" | bc)

echo "---" >> ${REPORT_FILE}
echo "结束时间: $(date)" >> ${REPORT_FILE}
echo "总检查次数: ${TOTAL_CHECKS}" >> ${REPORT_FILE}
echo "成功次数: ${HEALTH_CHECKS}" >> ${REPORT_FILE}
echo "失败次数: ${FAILED_CHECKS}" >> ${REPORT_FILE}
echo "成功率: ${SUCCESS_RATE}%" >> ${REPORT_FILE}

echo "📊 监控完成!"
echo "📈 总检查次数: ${TOTAL_CHECKS}"
echo "✅ 成功次数: ${HEALTH_CHECKS}"
echo "❌ 失败次数: ${FAILED_CHECKS}"
echo "📊 成功率: ${SUCCESS_RATE}%"

# 成功率评估
if (( $(echo "$SUCCESS_RATE >= 95" | bc -l) )); then
    echo "🎉 部署质量优秀 (成功率 >= 95%)"
    echo "$(date): 🎉 部署质量优秀" >> ${REPORT_FILE}
elif (( $(echo "$SUCCESS_RATE >= 90" | bc -l) )); then
    echo "✅ 部署质量良好 (成功率 >= 90%)"
    echo "$(date): ✅ 部署质量良好" >> ${REPORT_FILE}
elif (( $(echo "$SUCCESS_RATE >= 80" | bc -l) )); then
    echo "⚠️  部署质量一般 (成功率 >= 80%)"
    echo "$(date): ⚠️  部署质量一般" >> ${REPORT_FILE}
else
    echo "❌ 部署质量较差 (成功率 < 80%)"
    echo "$(date): ❌ 部署质量较差" >> ${REPORT_FILE}
fi

# 发送最终报告
if [ -n "${SLACK_WEBHOOK_URL}" ]; then
    echo "📢 发送最终监控报告..."

    COLOR="good"
    if (( $(echo "$SUCCESS_RATE < 80" | bc -l) )); then
        COLOR="danger"
    elif (( $(echo "$SUCCESS_RATE < 90" | bc -l) )); then
        COLOR="warning"
    fi

    curl -X POST -H 'Content-type: application/json' \
        --data "{
            \"text\": \"📊 ${ENVIRONMENT} 环境部署监控完成\",
            \"attachments\": [{
                \"color\": \"${COLOR}\",
                \"fields\": [
                    {\"title\": \"监控时长\", \"value\": \"${DURATION}秒\", \"short\": true},
                    {\"title\": \"成功率\", \"value\": \"${SUCCESS_RATE}%\", \"short\": true},
                    {\"title\": \"成功次数\", \"value\": \"${HEALTH_CHECKS}\", \"short\": true},
                    {\"title\": \"失败次数\", \"value\": \"${FAILED_CHECKS}\", \"short\": true}
                ]
            }]
        }" \
        ${SLACK_WEBHOOK_URL}
fi

echo "📄 详细报告已保存到: ${REPORT_FILE}"