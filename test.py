from netaddr import IPNetwork, cidr_merge, IPAddress
import time

# 保存成pkl
import pickle
# with open('firewall.pkl', 'wb') as f:
#     pickle.dump(summary, f)

# 读取pkl
with open('firewall.pkl', 'rb') as f:
    summary = pickle.load(f)

ip_address = ''
ip = IPNetwork(ip_address)
supernets = ip.supernet(8)
supernets.append(IPNetwork(ip_address+'/32'))

# 取交集
start = time.time()
x = set(summary).intersection(set(supernets))
end = time.time()
if x:
    print('DE')
else:
    print('Not DE')
print('time used: ', end-start)
