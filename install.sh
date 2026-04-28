#!/bin/bash
# One-click install script for Lipro Smart Home integration
#
# Supported install paths:
#   bash install.sh                          # default: resolve the latest tagged release
#   bash install.sh --archive-file ./lipro-hass-vX.Y.Z.zip --checksum-file ./SHA256SUMS
#
# Advanced / preview-only remote paths:
#   ARCHIVE_TAG=main bash install.sh
#   ARCHIVE_TAG=main LIPRO_ALLOW_MIRROR=1 HUB_DOMAIN=ghfast.top bash install.sh
set -euo pipefail

DOMAIN="lipro"
REPO_PATH="Exlany/lipro-hass"

ARCHIVE_TAG="${ARCHIVE_TAG:-}"
ARCHIVE_FILE="${ARCHIVE_FILE:-}"
CHECKSUM_FILE="${CHECKSUM_FILE:-}"
HUB_DOMAIN="${HUB_DOMAIN:-}"

RED_COLOR='\033[0;31m'
GREEN_COLOR='\033[0;32m'
YELLOW_COLOR='\033[1;33m'
NO_COLOR='\033[0m'

ARCHIVE_URL=""
ARCHIVE_MODE="remote"
MIN_PYTHON_VERSION="3.14.2"

declare haPath
haPath=""
declare ccPath
ccPath=""
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

show_help() {
    cat <<'HELP'
Usage:
  bash install.sh
  bash install.sh --archive-file <lipro-hass-vX.Y.Z.zip> --checksum-file <SHA256SUMS>

Default remote path:
  bash install.sh              # resolves the latest tagged release

Advanced / preview-only remote paths:
  ARCHIVE_TAG=main bash install.sh
  ARCHIVE_TAG=<branch> LIPRO_ALLOW_BRANCH_FALLBACK=1 bash install.sh
  ARCHIVE_TAG=main LIPRO_ALLOW_MIRROR=1 HUB_DOMAIN=<mirror> bash install.sh

Options:
  --archive-file <path>   Local release zip path (supported path)
  --checksum-file <path>  SHA256SUMS file for the local release zip
  --tag, --archive-tag    Remote tag/branch selector for advanced preview installs
  -h, --help              Show this help
HELP
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --archive-file)
            [ "$#" -ge 2 ] || error "Missing value for --archive-file"
            ARCHIVE_FILE="$2"
            shift 2
            ;;
        --checksum-file)
            [ "$#" -ge 2 ] || error "Missing value for --checksum-file"
            CHECKSUM_FILE="$2"
            shift 2
            ;;
        --tag|--archive-tag)
            [ "$#" -ge 2 ] || error "Missing value for $1"
            ARCHIVE_TAG="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            if [ -z "$ARCHIVE_TAG" ]; then
                ARCHIVE_TAG="$1"
                shift
            else
                error "Unknown argument: $1"
            fi
            ;;
    esac
done

[ -z "$HUB_DOMAIN" ] && HUB_DOMAIN="github.com"
if [ -n "$ARCHIVE_FILE" ]; then
    ARCHIVE_MODE="local"
fi
if [ "$ARCHIVE_MODE" = "remote" ] && [ -z "$ARCHIVE_TAG" ]; then
    ARCHIVE_TAG="latest"
fi

check_requirement() {
    if [ -z "$(command -v "$1")" ]; then
        error "'$1' is not installed / '$1' 未安装"
    fi
}

check_requirement "unzip"

resolve_python_bin() {
    if command -v python3 >/dev/null 2>&1; then
        echo "python3"
        return 0
    fi
    if command -v python >/dev/null 2>&1; then
        echo "python"
        return 0
    fi
    return 1
}

assert_min_python_version() {
    local pythonBin requiredVersion
    pythonBin="$1"
    requiredVersion="${2:-$MIN_PYTHON_VERSION}"

    "$pythonBin" - "$requiredVersion" <<'PY'
import sys

required = tuple(int(part) for part in sys.argv[1].split('.'))
current = sys.version_info[:3]
if current < required:
    print(
        f"Python {sys.version.split()[0]} is too old; need >= {sys.argv[1]}",
        file=sys.stderr,
    )
    sys.exit(2)
PY
}

python_preflight_scan_zip() {
    local zipPath
    zipPath="$1"

    local pythonBin
    pythonBin="$(resolve_python_bin || true)"

    if [ -z "$pythonBin" ]; then
        error "Python not found; cannot safely validate archive (symlink/size/path checks). Please install python3 or python 3.14.2+."
    fi

    assert_min_python_version "$pythonBin"

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

python_verify_release_checksum() {
    local archivePath checksumPath expectedName
    archivePath="$1"
    checksumPath="$2"
    expectedName="$3"

    local pythonBin
    pythonBin="$(resolve_python_bin || true)"
    if [ -z "$pythonBin" ]; then
        error "Python not found; cannot verify archive checksum with hashlib. Please install python3 or python 3.14.2+."
    fi

    assert_min_python_version "$pythonBin"

    "$pythonBin" - "$archivePath" "$checksumPath" "$expectedName" <<'PY'
import hashlib
import pathlib
import sys

archive_path = pathlib.Path(sys.argv[1])
checksum_path = pathlib.Path(sys.argv[2])
expected_name = sys.argv[3]

entries: dict[str, str] = {}
for line in checksum_path.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line:
        continue
    parts = line.split()
    if len(parts) < 2:
        continue
    digest = parts[0]
    name = parts[-1].lstrip("*")
    entries[name] = digest

expected_digest = entries.get(expected_name)
if not expected_digest:
    print(f"SHA256SUMS does not contain an entry for {expected_name}", file=sys.stderr)
    sys.exit(2)

sha = hashlib.sha256()
with archive_path.open("rb") as handle:
    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
        sha.update(chunk)
actual_digest = sha.hexdigest()

if actual_digest != expected_digest:
    print(
        f"Checksum mismatch for {expected_name} (expected {expected_digest}, got {actual_digest})",
        file=sys.stderr,
    )
    sys.exit(2)

print(f"Checksum verified: {expected_name}", file=sys.stderr)
PY
}

resolve_latest_release_tag() {
    local latestUrl
    latestUrl="https://$HUB_DOMAIN/$REPO_PATH/releases/latest"

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

prepare_remote_archive_urls() {
    local requestedArchiveTag allowBranchFallback
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
            error "Could not resolve latest release tag. Please pin ARCHIVE_TAG=<tag> (e.g. vX.Y.Z). Use ARCHIVE_TAG=main explicitly to install development branch."
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

    declare -ga archiveUrls=("https://$HUB_DOMAIN/$REPO_PATH/archive/refs/tags/$ARCHIVE_TAG.zip")
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
        info "Tip: pin ARCHIVE_TAG=<tag> for reproducible installs (e.g. ARCHIVE_TAG=vX.Y.Z)"
    fi

    if [ "$allowBranchFallback" = "1" ] || [ "$ARCHIVE_TAG" = "main" ] || [ "$HUB_DOMAIN" != "github.com" ]; then
        warn "Remote installs via main/branch/mirror are preview-only and unsupported for production. Prefer verified release assets instead."
    fi
}

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

if [ "$ARCHIVE_MODE" = "local" ]; then
    [ -f "$ARCHIVE_FILE" ] || error "Archive file not found: $ARCHIVE_FILE"
    [ -n "$CHECKSUM_FILE" ] || error "Local release-asset installs require --checksum-file / CHECKSUM_FILE"
    [ -f "$CHECKSUM_FILE" ] || error "Checksum file not found: $CHECKSUM_FILE"

    releaseZipName="$(basename "$ARCHIVE_FILE")"
    info "Using local verified release asset: $releaseZipName"
    cp "$ARCHIVE_FILE" "$tmpZip"
    python_verify_release_checksum "$tmpZip" "$CHECKSUM_FILE" "$releaseZipName" || error "Checksum verification failed / 压缩包校验失败"
    ARCHIVE_URL="$ARCHIVE_FILE"
else
    check_requirement "wget"
    prepare_remote_archive_urls

    info "Downloading $ARCHIVE_TAG..."
    downloadedFromRelease=0
    if [ "$HUB_DOMAIN" = "github.com" ] \
        && [ "${#archiveUrls[@]}" -eq 1 ] \
        && [ "$ARCHIVE_TAG" != "main" ]; then
        releaseZipName="lipro-hass-${ARCHIVE_TAG}.zip"
        releaseZipUrl="https://github.com/$REPO_PATH/releases/download/$ARCHIVE_TAG/$releaseZipName"
        releaseSumsUrl="https://github.com/$REPO_PATH/releases/download/$ARCHIVE_TAG/SHA256SUMS"
        releaseSumsFile="$tmpRoot/SHA256SUMS"

        info "Trying GitHub Release asset: $releaseZipName"
        if ! wget -t 2 -O "$tmpZip" "$releaseZipUrl"; then
            error "Release asset not found for $ARCHIVE_TAG; verified release install cannot continue"
        fi
        if ! wget -t 2 -O "$releaseSumsFile" "$releaseSumsUrl"; then
            error "SHA256SUMS not found for $ARCHIVE_TAG; cannot verify archive integrity"
        fi

        python_verify_release_checksum "$tmpZip" "$releaseSumsFile" "$releaseZipName" || error "Checksum verification failed / 压缩包校验失败"
        downloadedFromRelease=1
        ARCHIVE_URL="$releaseZipUrl"
    fi

    if [ "$downloadedFromRelease" = "0" ]; then
        download_archive "$tmpZip" "${archiveUrls[@]}" || error "Failed to download archive for $ARCHIVE_TAG"
        warn "Downloaded a preview/unsupported archive path. Prefer verified release assets for production installs."
    fi
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
