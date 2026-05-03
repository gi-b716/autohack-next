#!/bin/bash
set -e

# Arguments:
# $1 = Release type (Pre-release, Release, Commit)
# $2 = Current tag name (or commit hash)
# $3 = Version
# $4 = Output file path

RELEASE_TYPE="$1"
CURRENT_TAG="$2"
VERSION="$3"
OUTPUT_FILE="$4"
CURRENT_COMMIT=$(git rev-parse --short HEAD)

# Fetch all tags to ensure we have complete history
git fetch --tags --unshallow --force 2>/dev/null || git fetch --tags --force 2>/dev/null || true

# Get all tags sorted by version, excluding prereleases and current tag
PREV_TAG=$(git tag --list --sort=-version:refname | \
  grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' | \
  grep -v "^$CURRENT_TAG$" | \
  head -1)

if [ -z "$PREV_TAG" ]; then
  # If no previous release found, use the first commit
  PREV_TAG=$(git rev-list --max-parents=0 HEAD)
  echo "No previous release found, using first commit: $PREV_TAG"
else
  echo "Previous release found: $PREV_TAG"
fi

# Create changelog file
echo "# $RELEASE_TYPE $CURRENT_TAG" > "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Get commits between previous tag and current commit
if git rev-parse "$PREV_TAG" >/dev/null 2>&1; then
  if [ "$PREV_TAG" = "$(git rev-list --max-parents=0 HEAD)" ]; then
    COMMIT_RANGE="HEAD"
    echo "## 📝 All Changes (Initial Release)" >> "$OUTPUT_FILE"
  else
    COMMIT_RANGE="$PREV_TAG..HEAD"
    echo "## 📝 Changes since $PREV_TAG" >> "$OUTPUT_FILE"
  fi
else
  COMMIT_RANGE="HEAD"
  echo "## 📝 All Changes" >> "$OUTPUT_FILE"
fi

echo "" >> "$OUTPUT_FILE"

# Count commits
COMMIT_COUNT=$(git rev-list --count $COMMIT_RANGE)
if [ "$COMMIT_COUNT" -eq 0 ]; then
  echo "No new commits since last release." >> "$OUTPUT_FILE"
else
  echo "**$COMMIT_COUNT commits** in this release:" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"

  # Generate commit log with better formatting
  git log $COMMIT_RANGE \
    --pretty=format:"- [\`%h\`](../../commit/%H) %s (%an, %ad)" \
    --date=short \
    --reverse >> "$OUTPUT_FILE"
fi

echo "" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Generate contributors list with commit counts
echo "## 👥 Contributors" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

if [ "$COMMIT_COUNT" -gt 0 ]; then
  # Get contributors with commit counts
  git log $COMMIT_RANGE \
    --pretty=format:"%an | <%ae>" | \
    sort | uniq -c | sort -nr | \
    while read count info; do
      echo "- **$info** ($count commits)" >> "$OUTPUT_FILE"
    done
else
  echo "No contributors in this release." >> "$OUTPUT_FILE"
fi

echo "" >> "$OUTPUT_FILE"

# Add build information
echo "## 🏗️ Build Information" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "- **Commit**: [\`$CURRENT_COMMIT\`](../../commit/$CURRENT_COMMIT)" >> "$OUTPUT_FILE"
echo "- **Build Date**: $(date -u '+%Y-%m-%d %H:%M:%S UTC')" >> "$OUTPUT_FILE"
echo "- **Release Type**: $RELEASE_TYPE" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Platform information
echo "## 🖥️ Supported Platforms" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "| Platform | Architecture | Package Name |" >> "$OUTPUT_FILE"
echo "|----------|--------------|--------------|" >> "$OUTPUT_FILE"
echo "| Linux | x64 | \`autohack-linux-x64-$CURRENT_TAG-$CURRENT_COMMIT.zip\` |" >> "$OUTPUT_FILE"
echo "| Linux | ARM64 | \`autohack-linux-arm64-$CURRENT_TAG-$CURRENT_COMMIT.zip\` |" >> "$OUTPUT_FILE"
echo "| Windows | x64 | \`autohack-windows-x64-$CURRENT_TAG-$CURRENT_COMMIT.zip\` |" >> "$OUTPUT_FILE"
echo "| Windows | ARM64 | \`autohack-windows-arm64-$CURRENT_TAG-$CURRENT_COMMIT.zip\` |" >> "$OUTPUT_FILE"
echo "| macOS | Intel | \`autohack-macos-Intel-$CURRENT_TAG-$CURRENT_COMMIT.zip\` |" >> "$OUTPUT_FILE"
echo "| macOS | ARM64 (Apple Silicon) | \`autohack-macos-arm64-$CURRENT_TAG-$CURRENT_COMMIT.zip\` |" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "## 📦 Installation" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "### Python Package" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
if [ "$RELEASE_TYPE" = "Pre-release" ]; then
  echo "This is a pre-release version. To install from TestPyPI, use the following command:" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  echo "\`\`\`bash" >> "$OUTPUT_FILE"
  echo "pip install -i https://test.pypi.org/simple/ autohack-next==$VERSION" >> "$OUTPUT_FILE"
  echo "\`\`\`" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  echo "For stable releases, use the command below:" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  echo "\`\`\`bash" >> "$OUTPUT_FILE"
  echo "pip install autohack-next" >> "$OUTPUT_FILE"
  echo "\`\`\`" >> "$OUTPUT_FILE"
elif [ "$RELEASE_TYPE" = "Commit" ]; then
  echo "This is a development version built from a specific commit. To install, download the .whl file from the assets below and use the following command (replace <file_name> with the actual file name):" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  echo "\`\`\`bash" >> "$OUTPUT_FILE"
  echo "pip install <file_name>.whl" >> "$OUTPUT_FILE"
  echo "\`\`\`" >> "$OUTPUT_FILE"
else
  echo "To install the latest stable release from PyPI, use the following command:" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  echo "\`\`\`bash" >> "$OUTPUT_FILE"
  echo "pip install autohack-next==$VERSION" >> "$OUTPUT_FILE"
  echo "\`\`\`" >> "$OUTPUT_FILE"
fi
echo "" >> "$OUTPUT_FILE"
echo "### Standalone Executable" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "1. Download the appropriate package for your platform from the assets below" >> "$OUTPUT_FILE"
echo "2. Extract the zip file" >> "$OUTPUT_FILE"
echo "3. Run the \`autohack\` executable" >> "$OUTPUT_FILE"
