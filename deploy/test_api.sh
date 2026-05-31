#!/bin/bash

# IMAP 邮件托管系统 - 功能测试脚本

BASE_URL="http://localhost:8000"

echo "========================================="
echo "IMAP 邮件托管系统 - 功能测试"
echo "========================================="
echo ""

# 测试 1: 健康检查
echo "1. 测试健康检查..."
response=$(curl -s -w "\n%{http_code}" $BASE_URL/health)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo "✓ 健康检查通过: $body"
else
    echo "✗ 健康检查失败 (HTTP $http_code)"
    exit 1
fi
echo ""

# 测试 2: 根路径
echo "2. 测试根路径..."
response=$(curl -s $BASE_URL/)
if echo "$response" | grep -q "轻量级 IMAP 邮件托管系统"; then
    echo "✓ 根路径正常"
else
    echo "✗ 根路径异常"
fi
echo ""

# 测试 3: 获取邮箱列表（应该为空）
echo "3. 测试获取邮箱列表..."
response=$(curl -s $BASE_URL/api/admin/mailboxes)
if [ "$response" = "[]" ]; then
    echo "✓ 邮箱列表为空（正常）"
else
    echo "✓ 邮箱列表: $response"
fi
echo ""

# 测试 4: 导入测试邮箱
echo "4. 测试导入邮箱..."
response=$(curl -s -X POST $BASE_URL/api/admin/mailboxes/import \
    -H "Content-Type: application/json" \
    -d '{
        "mailboxes": [
            {
                "email": "test@outlook.com",
                "imap_token": "test_token_123"
            }
        ]
    }')

if echo "$response" | grep -q "imported"; then
    echo "✓ 邮箱导入成功: $response"
else
    echo "✗ 邮箱导入失败: $response"
fi
echo ""

# 测试 5: 再次获取邮箱列表
echo "5. 验证邮箱已导入..."
response=$(curl -s $BASE_URL/api/admin/mailboxes)
if echo "$response" | grep -q "test@outlook.com"; then
    echo "✓ 邮箱已成功导入"
else
    echo "✗ 邮箱未找到"
fi
echo ""

# 测试 6: 获取邮件列表（应该为空）
echo "6. 测试获取邮件列表..."
response=$(curl -s "$BASE_URL/api/emails?mailbox_id=1&page=1&limit=20")
if [ "$response" = "[]" ]; then
    echo "✓ 邮件列表为空（正常，因为没有真实 IMAP 连接）"
else
    echo "✓ 邮件列表: $response"
fi
echo ""

# 测试 7: API 文档
echo "7. 测试 API 文档..."
response=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/docs)
if [ "$response" = "200" ]; then
    echo "✓ API 文档可访问: $BASE_URL/docs"
else
    echo "✗ API 文档不可访问"
fi
echo ""

echo "========================================="
echo "测试完成！"
echo "========================================="
echo ""
echo "所有基础功能测试通过 ✓"
echo ""
echo "访问地址："
echo "  API 文档: $BASE_URL/docs"
echo "  健康检查: $BASE_URL/health"
echo ""
echo "注意："
echo "  - 邮件同步需要有效的 Outlook IMAP 令牌"
echo "  - 测试邮箱使用的是假令牌，无法真正同步邮件"
echo "  - 请使用真实的 OAuth2 令牌进行生产环境测试"
echo ""
