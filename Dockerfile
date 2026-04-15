FROM kalilinux/kali-rolling:latest

ENV DEBIAN_FRONTEND=noninteractive

# ----------------------------------------------------------------------
# 1. Base system + tools
# ----------------------------------------------------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    apt-transport-https \
    software-properties-common \
    gnupg \
    curl \
    wget \
    plocate \
    git \
    nano \
    vim \
    ripgrep \
    jq \
    fzf \
    tree \
    tmux \
    unzip \
    file \
    strace \
    ltrace \
    iputils-ping \
    net-tools \
    dnsutils \
    whois \
    traceroute \
    socat \
    netcat-openbsd \
    cifs-utils \
    build-essential \
    gcc-multilib \
    gdb \
    gdbserver \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    pkg-config \
    cmake \
    clang \
    binutils \
    libffi-dev \
    libssl-dev \
    ruby-full \
    libc6-dbg \
    zlib1g-dev \
    # scanners and enumeration tools
    nmap \
    masscan \
    nikto \
    smbclient \
    ldap-utils \
    openvpn \
    # metasploit
    metasploit-framework \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------------------
# 2. Install Go
# ----------------------------------------------------------------------
RUN wget https://go.dev/dl/go1.23.0.linux-amd64.tar.gz -O /tmp/go.tar.gz && \
    tar -C /usr/local -xzf /tmp/go.tar.gz && \
    rm /tmp/go.tar.gz

ENV PATH="/usr/local/go/bin:${PATH}"

# ----------------------------------------------------------------------
# 3. GEF & PEDA
# ----------------------------------------------------------------------
RUN git clone https://github.com/hugsy/gef.git /opt/gef && \
    echo "source /opt/gef/gef.py" >> /root/.gdbinit && \
    git clone https://github.com/longld/peda.git /opt/peda && \
    echo "source /opt/peda/peda.py" >> /root/.gdbinit

# ----------------------------------------------------------------------
# 4. ffuf + gobuster
# ----------------------------------------------------------------------
RUN git clone https://github.com/ffuf/ffuf.git /opt/ffuf-src && \
    cd /opt/ffuf-src && go build && cp ffuf /usr/local/bin/ffuf

RUN go install github.com/OJ/gobuster/v3@latest && \
    ln -s /root/go/bin/gobuster /usr/local/bin/gobuster

# ----------------------------------------------------------------------
# 5. SecLists
# ----------------------------------------------------------------------
RUN git clone https://github.com/danielmiessler/SecLists.git /opt/SecLists

# ----------------------------------------------------------------------
# 6. Python tools
# ----------------------------------------------------------------------
RUN python3 -m pip install --break-system-packages --no-cache-dir \
    pwntools \
    droopescan \
    impacket

# ----------------------------------------------------------------------
# 7. NetExec via pipx
# ----------------------------------------------------------------------
RUN apt-get update && apt-get install -y pipx && \
    pipx ensurepath && \
    pipx install git+https://github.com/Pennyw0rth/NetExec.git

# ----------------------------------------------------------------------
# 8. Environment PATH fixes (IMPORTANT)
# ----------------------------------------------------------------------
ENV PATH="/usr/local/go/bin:/root/.local/bin:/root/.local/pipx/venvs/netexec/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# ----------------------------------------------------------------------
# 9. Install newest FastMCP (includes HTTP server and client)
# ----------------------------------------------------------------------
RUN pip install --break-system-packages --no-cache-dir \
    fastmcp==2.14.3 \
    uvicorn

# ----------------------------------------------------------------------
# 10. Workspace + MCP server
# ----------------------------------------------------------------------
RUN mkdir -p /workspace

# Copy MCP server script from build context
COPY kali_mcp_server.py /opt/kali_mcp_server.py

# Expose HTTP MCP port (for Claude → container)
EXPOSE 8000

WORKDIR /workspace

CMD ["sh", "-c", "python3 /opt/kali_mcp_server.py & tail -f /dev/null"]