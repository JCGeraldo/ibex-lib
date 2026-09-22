#!/usr/bin/env bash
# Arranque del entorno RAA-K en una distro Ubuntu-24.04 recien instalada (se ejecuta como root).
#   1. dependencias de compilacion de ibex-lib / ibex-affine / ibexopt-raak
#   2. usuario 'evapo' (uid 1000 = defaultUid de la distro), sudo sin clave, usuario por defecto
#   3. como evapo: copia scripts y parches del repo de VS Code, clona y fija los repos (wsl_clone.sh)
#   4. como evapo: aplica 0001+0002 sobre ibex-affine y 0003 sobre ibex-lib (con --check previo)
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
REPO=/mnt/c/Users/evapo/OneDrive/Documentos/GitHub/ibex-lib

echo "== 1. apt ($(date +%T))"
apt-get update -qq > /tmp/apt-update.log 2>&1 || { tail -20 /tmp/apt-update.log; exit 1; }
apt-get install -y -qq --no-install-recommends \
    build-essential cmake git flex bison pkg-config python3 libcppunit-dev bc time ca-certificates \
    > /tmp/apt-install.log 2>&1 || { tail -30 /tmp/apt-install.log; exit 1; }
gcc --version | head -1
cmake --version | head -1
echo "   flex $(flex --version | head -1 | awk '{print $2}')  bison $(bison --version | head -1 | awk '{print $4}')  cppunit $(pkg-config --modversion cppunit 2>/dev/null || echo '?')"

echo "== 2. usuario evapo ($(date +%T))"
id evapo > /dev/null 2>&1 || useradd -m -u 1000 -s /bin/bash -G sudo evapo
echo 'evapo ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/evapo
chmod 440 /etc/sudoers.d/evapo
grep -q '^\[user\]' /etc/wsl.conf || printf '\n[user]\ndefault=evapo\n' >> /etc/wsl.conf
cat /etc/wsl.conf

echo "== 3. scripts, parches y clonado como evapo ($(date +%T))"
su - evapo -c "
  set -euo pipefail
  mkdir -p ~/ibex-local/scripts ~/ibex-local/patches
  cp $REPO/raak/scripts/*.sh ~/ibex-local/scripts/
  cp $REPO/raak/patches/*.patch ~/ibex-local/patches/
  sed -i 's/\r\$//' ~/ibex-local/scripts/*.sh ~/ibex-local/patches/*.patch
  chmod +x ~/ibex-local/scripts/*.sh
  bash ~/ibex-local/scripts/wsl_clone.sh
"

echo "== 4. parches ($(date +%T))"
su - evapo -c '
  set -euo pipefail
  cd ~/ibex-local/ibex-affine
  git apply --check ../patches/0001-*.patch && git apply ../patches/0001-*.patch && echo "   0001 aplicado"
  git apply --check ../patches/0002-*.patch && git apply ../patches/0002-*.patch && echo "   0002 aplicado"
  git log --oneline -1; git status --short
  cd ~/ibex-local/ibex-lib
  git apply --check ../patches/0003-*.patch && git apply ../patches/0003-*.patch && echo "   0003 aplicado"
  git log --oneline -1; git status --short
'
echo "== listo ($(date +%T))"
