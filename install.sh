#!/bin/bash
# One-click install script for Lipro Smart Home integration
#
# Usage:
#   wget -q -O - https://raw.githubusercontent.com/Exlany/lipro-hass/main/install.sh | ARCHIVE_TAG=latest bash -
#   wget -q -O - https://raw.githubusercontent.com/Exlany/lipro-hass/main/install.sh | ARCHIVE_TAG=v1.0.0 bash -
#   wget -q -O - https://raw.githubusercontent.com/Exlany/lipro-hass/main/install.sh | LIPRO_ALLOW_MIRROR=1 HUB_DOMAIN=ghfast.top bash -
set -euo pipefail

DOMAIN="lipro"
REPO_PATH="Exlany/lipro-hass"

ARCHIVE_TAG="${ARCHIVE_TAG:-}"
HUB_DOMAIN="${HUB_DOMAIN:-}"

[ -z "$ARCHIVE_TAG" ] && ARCHIVE_TAG="${1:-}"
[ -z "$ARCHIVE_TAG" ] && ARCHIVE_TAG="latest"
[ -z "$HUB_DOMAIN" ] && HUB_DOMAIN="github.com"
ARCHIVE_URL=""

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
error() {
    local shouldExit
    shouldExit="${2:-true}"
    echo -e "${RED_COLOR}ERROR: $1${NO_COLOR}"
    if [ "$shouldExit" != "false" ]; then
        exit 1
    fi
}

check_requirement() {
    if [ -z "$(command -v "$1")" ]; then
        error "'$1' is not installed / '$1' 未安装"
    fi
}

check_requirement "wget"
check_requirement "unzip"

python_preflight_scan_zip() {
    local zipPath
    zipPath="$1"

    local pythonBin
    pythonBin=""
    if command -v python3 >/dev/null 2>&1; then
        pythonBin="python3"
    elif command -v python >/dev/null 2>&1; then
        pythonBin="python"
    fi

    if [ -z "$pythonBin" ]; then
        error "Python not found; cannot safely validate archive (symlink/size/path checks). Please install python3 or python."
    fi

    # This scan rejects dangerous paths and symlink/device-type entries before unzip runs.
    # It also caps file counts/sizes to reduce zip-bomb risk.
    "$pythonBin" - "$zipPath" <<'PY'
import os
import re
import stat
import sys
import zipfile

zip_path = sys.argv[1]

max_files = int(os.environ.get("LIPRO_INSTALL_MAX_FILES", "5000"))
max_total_bytes = int(
    os.environ.get("LIPRO_INSTALL_MAX_UNCOMPRESSED_BYTES", str(100 * 1024 * 1024))
)
max_single_file_bytes = int(
    os.environ.get("LIPRO_INSTALL_MAX_SINGLE_FILE_BYTES", str(20 * 1024 * 1024))
)

drive_prefix = re.compile(r"^[A-Za-z]:/")

total = 0
count = 0

with zipfile.ZipFile(zip_path) as zf:
    for info in zf.infolist():
        name = info.filename
        if not isinstance(name, str) or not name:
            print("Invalid zip entry name", file=sys.stderr)
            sys.exit(2)

        normalized = name.replace("\\", "/")
        if normalized.startswith("/") or drive_prefix.match(normalized):
            print(f"Unsafe absolute path in archive: {name}", file=sys.stderr)
            sys.exit(2)

        parts = [p for p in normalized.split("/") if p and p != "."]
        if any(p == ".." for p in parts):
            print(f"Unsafe path traversal in archive: {name}", file=sys.stderr)
            sys.exit(2)

        # Size caps (directories contribute 0 bytes).
        count += 1
        if count > max_files:
            print(f"Archive too large: {count} entries (max {max_files})", file=sys.stderr)
            sys.exit(2)

        file_size = int(getattr(info, "file_size", 0))
        if file_size < 0:
            print(f"Invalid file size in archive: {name}", file=sys.stderr)
            sys.exit(2)
        if file_size > max_single_file_bytes:
            print(
                f"Archive entry too large: {name} ({file_size} bytes)",
                file=sys.stderr,
            )
            sys.exit(2)

        total += file_size
        if total > max_total_bytes:
            print(
                f"Archive uncompressed size too large: {total} bytes (max {max_total_bytes})",
                file=sys.stderr,
            )
            sys.exit(2)

        mode = int(getattr(info, "external_attr", 0)) >> 16
        if mode:
            if (
                stat.S_ISLNK(mode)
                or stat.S_ISCHR(mode)
                or stat.S_ISBLK(mode)
                or stat.S_ISFIFO(mode)
                or stat.S_ISSOCK(mode)
            ):
                print(f"Unsafe file type in archive: {name}", file=sys.stderr)
                sys.exit(2)

print(f"Archive preflight ok: {count} entries, {total} bytes", file=sys.stderr)
PY
}

resolve_latest_release_tag() {
    local latestUrl
    latestUrl="https://$HUB_DOMAIN/$REPO_PATH/releases/latest"

    # We avoid depending on jq/curl. GitHub returns a 302 redirect to:
    #   .../releases/tag/<tag>
    # We grab the Location header without following redirects.
    local location
    location="$(
        wget -qS --max-redirect=0 -O /dev/null "$latestUrl" 2>&1 \
            | awk '/^[ ]*Location: / {print $2}' \
            | tail -1 \
            | tr -d '\r'
    )"

    if [[ "$location" != *"/releases/tag/"* ]]; then
        return 1
    fi

    local tag
    tag="${location##*/}"
    tag="${tag%%\?*}"
    if [ -z "$tag" ] || [ "$tag" = "latest" ]; then
        return 1
    fi

    echo "$tag"
}

download_archive() {
    local dest
    dest="$1"
    shift

    local url
    for url in "$@"; do
        info "Trying archive URL: $url"
        if wget -t 2 -O "$dest" "$url"; then
            ARCHIVE_URL="$url"
            return 0
        fi
        warn "Download failed: $url"
    done
    return 1
}

requestedArchiveTag="$ARCHIVE_TAG"
if [ "$HUB_DOMAIN" != "github.com" ]; then
    if [ "${LIPRO_ALLOW_MIRROR:-0}" != "1" ]; then
        error "Refusing to install from non-default HUB_DOMAIN='$HUB_DOMAIN'. Set LIPRO_ALLOW_MIRROR=1 to override (DANGEROUS)."
    fi
    warn "HUB_DOMAIN is set to '$HUB_DOMAIN'. This will download and install code from that domain. Only use trusted mirrors."
fi
if [ "$ARCHIVE_TAG" = "latest" ]; then
    info "Resolving latest release tag..."
    if resolvedTag="$(resolve_latest_release_tag)"; then
        ARCHIVE_TAG="$resolvedTag"
        info "Resolved latest to '$ARCHIVE_TAG'"
    else
        error "Could not resolve latest release tag. Please pin ARCHIVE_TAG=<tag> (e.g. v1.0.0). Use ARCHIVE_TAG=main explicitly to install development branch."
    fi
fi

allowBranchFallback=1
if [ "$requestedArchiveTag" = "latest" ]; then
    allowBranchFallback=0
elif [[ "$ARCHIVE_TAG" =~ ^v[0-9] ]] || [[ "$ARCHIVE_TAG" =~ ^[0-9] ]] || [[ "$ARCHIVE_TAG" == *.* ]]; then
    allowBranchFallback=0
fi
if [ "${LIPRO_ALLOW_BRANCH_FALLBACK:-0}" = "1" ]; then
    allowBranchFallback=1
fi

declare -a archiveUrls=("https://$HUB_DOMAIN/$REPO_PATH/archive/refs/tags/$ARCHIVE_TAG.zip")
if [ "$allowBranchFallback" = "1" ]; then
    archiveUrls+=(
        "https://$HUB_DOMAIN/$REPO_PATH/archive/refs/heads/$ARCHIVE_TAG.zip"
        "https://$HUB_DOMAIN/$REPO_PATH/archive/$ARCHIVE_TAG.zip"
    )
else
    info "Tag-only install mode: will not fall back to branch archives. Set LIPRO_ALLOW_BRANCH_FALLBACK=1 to override."
fi

info "Archive tag: $requestedArchiveTag (resolved: $ARCHIVE_TAG)"
if [ "$requestedArchiveTag" = "latest" ]; then
    info "Tip: pin ARCHIVE_TAG=<tag> for reproducible installs (e.g. ARCHIVE_TAG=v1.0.0)"
fi
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

tmpRoot="$(mktemp -d)"
tmpZip="$tmpRoot/archive.zip"
tmpExtract="$tmpRoot/extract"
tmpInstall="$ccPath/.${DOMAIN}.install_tmp"
backupDir="$ccPath/.${DOMAIN}.backup"

cleanup() {
    rm -rf "$tmpRoot" 2>/dev/null || true
    rm -rf "$tmpInstall" 2>/dev/null || true
}
trap cleanup EXIT

info "Downloading $ARCHIVE_TAG..."
downloadedFromRelease=0
if [ "$HUB_DOMAIN" = "github.com" ] && [ "$allowBranchFallback" = "0" ] && [ "$ARCHIVE_TAG" != "main" ]; then
    releaseZipName="lipro-hass-${ARCHIVE_TAG}.zip"
    releaseZipUrl="https://github.com/$REPO_PATH/releases/download/$ARCHIVE_TAG/$releaseZipName"
    releaseSumsUrl="https://github.com/$REPO_PATH/releases/download/$ARCHIVE_TAG/SHA256SUMS"
    releaseSumsFile="$tmpRoot/SHA256SUMS"

    info "Trying GitHub Release asset: $releaseZipName"
    if wget -t 2 -O "$tmpZip" "$releaseZipUrl"; then
        downloadedFromRelease=1
        ARCHIVE_URL="$releaseZipUrl"

        if wget -t 2 -O "$releaseSumsFile" "$releaseSumsUrl"; then
            if command -v sha256sum >/dev/null 2>&1; then
                expectedSha="$(
                    awk -v name="$releaseZipName" '($2 == name || $2 == ("*" name)) {print $1; exit}' "$releaseSumsFile"
                )"
                if [ -z "$expectedSha" ]; then
                    if [ "${LIPRO_REQUIRE_CHECKSUM:-0}" = "1" ]; then
                        error "SHA256SUMS does not contain an entry for $releaseZipName"
                    fi
                    warn "SHA256SUMS missing entry for $releaseZipName; skipping verification"
                else
                    actualSha="$(sha256sum "$tmpZip" | awk '{print $1}')"
                    if [ "$expectedSha" != "$actualSha" ]; then
                        error "Checksum mismatch for $releaseZipName (expected $expectedSha, got $actualSha)"
                    fi
                    info "Checksum verified: $releaseZipName"
                fi
            else
                if [ "${LIPRO_REQUIRE_CHECKSUM:-0}" = "1" ]; then
                    error "'sha256sum' is not installed; cannot verify archive checksum"
                fi
                warn "'sha256sum' not found; skipping checksum verification"
            fi
        else
            if [ "${LIPRO_REQUIRE_CHECKSUM:-0}" = "1" ]; then
                error "SHA256SUMS not found for $ARCHIVE_TAG; cannot verify archive integrity"
            fi
            warn "SHA256SUMS not found for $ARCHIVE_TAG; continuing without verification"
        fi
    else
        rm -f "$tmpZip" 2>/dev/null || true
        warn "Release asset not found for $ARCHIVE_TAG; falling back to source archive"
        if [ "${LIPRO_REQUIRE_CHECKSUM:-0}" = "1" ]; then
            error "Release asset not found for $ARCHIVE_TAG; checksum verification required"
        fi
    fi
fi

if [ "$downloadedFromRelease" = "0" ]; then
    download_archive "$tmpZip" "${archiveUrls[@]}" || error "Failed to download archive for $ARCHIVE_TAG"
fi
info "Archive URL: $ARCHIVE_URL"

info "Validating archive..."
python_preflight_scan_zip "$tmpZip" || error "Archive preflight scan failed / 压缩包预检失败"
unzip -t "$tmpZip" >/dev/null 2>&1 || error "Downloaded archive is not a valid zip / 下载的压缩包无效"
if unzip -Z -1 "$tmpZip" 2>/dev/null | grep -Eq '(^/|^\.\./|/\.\./)'; then
    error "Unsafe paths detected in archive / 压缩包包含不安全路径"
fi

info "Unpacking..."
mkdir -p "$tmpExtract"
unzip -o "$tmpZip" -d "$tmpExtract" >/dev/null 2>&1

# Determine extracted top-level directory from archive content.
mapfile -t extractedRoots < <(
    unzip -Z -1 "$tmpZip" 2>/dev/null | awk -F/ 'NF > 1 {print $1}' | sort -u
)
if [ "${#extractedRoots[@]}" -ne 1 ]; then
    error "Could not determine extracted root directory from archive" false
    error "无法从压缩包中确定解压根目录"
fi
extractedDir="$tmpExtract/${extractedRoots[0]}"
if [ ! -d "$extractedDir" ]; then
    error "Could not find extracted directory: ${extractedRoots[0]}" false
    error "找不到解压目录: ${extractedRoots[0]}"
fi

if [ ! -d "$extractedDir/custom_components/$DOMAIN" ]; then
    error "Component directory not found in archive: custom_components/$DOMAIN" false
    error "压缩包中找不到组件目录: custom_components/$DOMAIN"
fi

info "Staging component..."
rm -rf "$tmpInstall"
cp -rf "$extractedDir/custom_components/$DOMAIN" "$tmpInstall"
if [ ! -f "$tmpInstall/manifest.json" ]; then
    error "Staged component missing manifest.json / 暂存组件缺少 manifest.json"
fi
if find "$tmpInstall" -type l -print -quit 2>/dev/null | grep -q .; then
    error "Symlinks detected in staged component / 暂存组件包含符号链接"
fi

info "Activating..."
if [ -d "$ccPath/$DOMAIN" ]; then
    rm -rf "$backupDir"
    mv "$ccPath/$DOMAIN" "$backupDir"
fi
	if ! mv "$tmpInstall" "$ccPath/$DOMAIN"; then
	    warn "Install failed, attempting rollback... / 安装失败，尝试回滚..."
	    rm -rf "${ccPath:?}/${DOMAIN:?}" 2>/dev/null || true
	    if [ -d "$backupDir" ]; then
	        mv "$backupDir" "$ccPath/$DOMAIN" 2>/dev/null || true
	    fi
	    error "Failed to activate new version / 无法激活新版本"
	fi
rm -rf "$backupDir"

info "Cleaning up temp files..."
rm -rf "$tmpRoot"

echo
info "Installation complete! / 安装成功！"
info "Please restart Home Assistant to activate the integration."
info "请重启 Home Assistant 以激活集成。"
