import requests as requests
import systeminfo, webscraper

customer_name = input("Customer name?")
customer_id = input("Customer Id?")
pc_name = input("PC Brand?")
asset_id = input("Asset ID?")

user = systeminfo.getpass.getuser()
cpu = systeminfo.get_cpu()
ram = systeminfo.get_ram()
hd = systeminfo.get_hd()
pc_os = systeminfo.get_os()
windows_key = systeminfo.get_windows_key()
gpu = systeminfo.get_gpu()
mb_brand = systeminfo.get_motherboard_serial()[2]
mb_name = systeminfo.get_motherboard_serial()[1]
mb_serial = systeminfo.get_motherboard_serial()[0]
pc_serial = systeminfo.get_dell_servicetag()

if (pc_name.lower().__contains__("dell")):
    pc_name = webscraper.getDellName(pc_serial)
    if (pc_name == "None"):
        pc_name = "Dell Computer"
elif (pc_name.lower().__contains__("hp")):
    pc_name = webscraper.getHPName(pc_serial)
    if (pc_name == "None"):
        pc_name = "HP Computer"

data = {'NAME' : customer_name, 'CUSTOMER_ID' : customer_id, 'PC_NAME' : pc_name, 'ASSET_ID' : asset_id,'USER' : user, 'CPU' : cpu, 'RAM' : ram, 'HD' : hd, 'PC_OS' : pc_os, 'WINDOWS_KEY' : windows_key, 'GPU' : gpu, 'MB_BRAND' : mb_brand, 'MB_NAME' : mb_name, 'MB_SERIAL' : mb_serial, 'PC_SERIAL' : pc_serial}
r = requests.post('http://127.0.0.1:8000/api/', json=data)
print(r.text)
