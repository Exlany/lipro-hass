#!/bin/bash
# One-click install script for Lipro Smart Home integration
#
# Usage:
#   wget -q -O - https://raw.githubusercontent.com/Exlany/lipro-hass/main/install.sh | bash -
#   wget -q -O - https://raw.githubusercontent.com/Exlany/lipro-hass/main/install.sh | ARCHIVE_TAG=v1.0.0 bash -
#   wget -q -O - https://raw.githubusercontent.com/Exlany/lipro-hass/main/install.sh | HUB_DOMAIN=ghfast.top bash -
set -e

DOMAIN="lipro"
REPO_PATH="Exlany/lipro-hass"
REPO_NAME="lipro-hass"

[ -z "$ARCHIVE_TAG" ] && ARCHIVE_TAG="$1"
[ -z "$ARCHIVE_TAG" ] && ARCHIVE_TAG="main"
[ -z "$HUB_DOMAIN" ] && HUB_DOMAIN="github.com"
ARCHIVE_URL="https://$HUB_DOMAIN/$REPO_PATH/archive/$ARCHIVE_TAG.zip"

RED_COLOR='\033[0;31m'
GREEN_COLOR='\033[0;32m'
YELLOW_COLOR='\033[1;33m'
NO_COLOR='\033[0m'

declare haPath
declare ccPath
declare -a paths=(
    "$PWD"
    "$PWD/config"
    "/config"
    "$HOME/.homeassistant"
    "/usr/share/hassio/homeassistant"
)

info()  { echo -e "${GREEN_COLOR}INFO: $1${NO_COLOR}"; }
warn()  { echo -e "${YELLOW_COLOR}WARN: $1${NO_COLOR}"; }
error() { echo -e "${RED_COLOR}ERROR: $1${NO_COLOR}"; if [ "$2" != "false" ]; then exit 1; fi; }

check_requirement() {
    if [ -z "$(command -v "$1")" ]; then
        error "'$1' is not installed / '$1' 未安装"
    fi
}

check_requirement "wget"
check_requirement "unzip"

info "Archive URL: $ARCHIVE_URL"
info "Trying to find Home Assistant configuration directory..."

for path in "${paths[@]}"; do
    if [ -n "$haPath" ]; then
        break
    fi
    if [ -f "$path/home-assistant.log" ]; then
        haPath="$path"
    elif [ -d "$path/.storage" ] && [ -f "$path/configuration.yaml" ]; then
        haPath="$path"
    fi
done

if [ -z "$haPath" ]; then
    echo
    error "Could not find the directory for Home Assistant" false
    error "找不到 Home Assistant 配置目录" false
    echo "Please cd to your Home Assistant configuration directory and run this script again."
    echo "请手动进入 Home Assistant 配置目录后再次执行此脚本。"
    exit 1
fi

info "Found Home Assistant configuration directory at '$haPath'"
cd "$haPath" || error "Could not change path to $haPath"

ccPath="$haPath/custom_components"
if [ ! -d "$ccPath" ]; then
    info "Creating custom_components directory..."
    mkdir "$ccPath"
fi

cd "$ccPath" || error "Could not change path to $ccPath"

info "Downloading $ARCHIVE_TAG..."
wget -t 2 -O "$ccPath/$ARCHIVE_TAG.zip" "$ARCHIVE_URL"

if [ -d "$ccPath/$DOMAIN" ]; then
    warn "custom_components/$DOMAIN already exists, removing old version..."
    rm -rf "$ccPath/$DOMAIN"
fi

info "Unpacking..."
unzip -o "$ccPath/$ARCHIVE_TAG.zip" -d "$ccPath" >/dev/null 2>&1

# Determine the extracted directory name (GitHub strips leading 'v' from tag)
ver="${ARCHIVE_TAG/#v/}"
extractedDir="$ccPath/$REPO_NAME-$ver"
if [ ! -d "$extractedDir" ]; then
    extractedDir="$ccPath/$REPO_NAME-$ARCHIVE_TAG"
fi
if [ ! -d "$extractedDir" ]; then
    error "Could not find extracted directory: $REPO_NAME-$ver" false
    error "找不到解压目录: $REPO_NAME-$ver"
fi

if [ ! -d "$extractedDir/custom_components/$DOMAIN" ]; then
    error "Component directory not found in archive: custom_components/$DOMAIN" false
    error "压缩包中找不到组件目录: custom_components/$DOMAIN"
fi

cp -rf "$extractedDir/custom_components/$DOMAIN" "$ccPath"

info "Cleaning up temp files..."
rm -rf "$ccPath/$ARCHIVE_TAG.zip"
rm -rf "$extractedDir"

echo
info "Installation complete! / 安装成功！"
info "Please restart Home Assistant to activate the integration."
info "请重启 Home Assistant 以激活集成。"
