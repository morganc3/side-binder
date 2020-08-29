# side-binder
Tool for DNS Rebinding Attacks

1. Setup compute instance with open security groups (at least UDP 53 and TCP 80) on a machine that has `iptables`
2. Choose payload
3. Update hardcoded values in side-binder.py
4. `python3 side-binder.py`
