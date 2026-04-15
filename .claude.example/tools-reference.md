# Tools Reference (Kali MCP Container)

You are talking to a Kali container with at least:

- nmap
- masscan
- nikto
- smbclient
- ldap-utils (ldapsearch)
- ffuf
- gobuster
- metasploit (msfconsole)
- NetExec (nxc)
- impacket
- SecLists at /opt/SecLists

Common patterns:

## Nmap

- `nmap -sV -Pn <target>`

## NetExec (NXC)

- SMB:
  - `nxc smb <target> --shares`
  - `nxc smb <target> -u '' -p '' --shares` (guest/anon)
- RDP:
  - `nxc rdp <target> -u <user> -p <pass>`
- WinRM:
  - `nxc winrm <target> -u <user> -p <pass>`

## SMB

- List shares (anonymous):
  - `smbclient -L //<target>/ -N`

## HTTP

- Directory discovery:
  - `ffuf -u http://<target>/FUZZ -w /opt/SecLists/Discovery/Web-Content/common.txt`

## Logging

- You may choose to redirect outputs:
  - `nmap -sV -Pn <target> -oN /workspace/logs/nmap-<target>.txt`
  - Then use `read_file` or `tail_log` on `/workspace/logs/nmap-<target>.txt`.
