#!/bin/sh

CONFIG_FILE="/etc/xray/config.json"

# Генерация UUID если его еще нет
if grep -q "YOUR_UUID_WILL_BE_GENERATED" "$CONFIG_FILE"; then
    UUID=$(cat /proc/sys/kernel/random/uuid)
    sed -i "s/YOUR_UUID_WILL_BE_GENERATED/$UUID/g" "$CONFIG_FILE"
    echo "==================================="
    echo "Generated UUID: $UUID"
    echo "==================================="
fi

# Генерация ключей Reality если их еще нет
if grep -q "YOUR_PRIVATE_KEY_WILL_BE_GENERATED" "$CONFIG_FILE"; then
    KEYS=$(/usr/local/bin/xray x25519)
    PRIVATE_KEY=$(echo "$KEYS" | grep "Private key:" | awk '{print $3}')
    PUBLIC_KEY=$(echo "$KEYS" | grep "Public key:" | awk '{print $3}')
    
    sed -i "s/YOUR_PRIVATE_KEY_WILL_BE_GENERATED/$PRIVATE_KEY/g" "$CONFIG_FILE"
    
    echo "==================================="
    echo "Generated Keys:"
    echo "Private key: $PRIVATE_KEY"
    echo "Public key: $PUBLIC_KEY"
    echo "==================================="
fi

# Вывод конфигурации для клиента
echo ""
echo "==================================="
echo "VLESS CONNECTION STRING:"
echo "==================================="
UUID=$(grep '"id"' "$CONFIG_FILE" | head -1 | sed 's/.*": "//;s/".*//')
PUBLIC_KEY=$(grep '"privateKey"' "$CONFIG_FILE" | sed 's/.*": "//;s/".*//')

# Получение публичного ключа из приватного
PUBLIC_KEY=$(/usr/local/bin/xray x25519 -i "$PUBLIC_KEY" | grep "Public key:" | awk '{print $3}')

# Получение внешнего IP
EXTERNAL_IP=$(curl -s ifconfig.me)
if [ -z "$EXTERNAL_IP" ]; then
    EXTERNAL_IP="YOUR_SERVER_IP"
fi

echo ""
echo "vless://${UUID}@${EXTERNAL_IP}:443?encryption=none&flow=xtls-rprx-vision&security=reality&sni=www.microsoft.com&fp=chrome&pbk=${PUBLIC_KEY}&type=tcp&headerType=none#VLESS-Server"
echo ""
echo "==================================="
echo "Configuration Details:"
echo "==================================="
echo "Server: $EXTERNAL_IP"
echo "Port: 443"
echo "UUID: $UUID"
echo "Flow: xtls-rprx-vision"
echo "Security: reality"
echo "SNI: www.microsoft.com"
echo "Public Key: $PUBLIC_KEY"
echo "==================================="
echo ""
echo "Starting Xray server..."
echo ""

# Запуск Xray
exec /usr/local/bin/xray run -c "$CONFIG_FILE"