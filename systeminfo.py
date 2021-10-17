import psutil, platform, GPUtil, cpuinfo, os, sys, wmi, winreg, getpass, subprocess
from tabulate import tabulate
from datetime import datetime
from multiprocessing import Process, freeze_support


def get_wifi_pass():
    data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8').split('\n')
    wifis = [line.split(':')[1][1:-1] for line in data if "All User Profile" in line]

    for wifi in wifis:
        results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', wifi, 'key=clear']).decode(
            'utf-8').split('\n')
        results = [line.split(':')[1][1:-1] for line in results if "Key Content" in line]
        try:
            print(f'Name: {wifi}, Password: {results[0]}')
        except IndexError:
            print(print(f'Name: {wifi}, Password: Cannot be read!'))

    return data


def f():
    pass


if __name__ == '__main__':
    freeze_support()
    Process(target=f).start()


def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def get_ram():
    # Memory Information
    svmem = psutil.virtual_memory()
    ram_size = get_size(svmem.total)
    return ram_size


def get_hd():
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:

            continue
        return get_size(partition_usage.total)
        # print(f"  Used: {get_size(partition_usage.used)}")
        # print(f"  Free: {get_size(partition_usage.free)}")


def get_gpu():
    gpus = GPUtil.getGPUs()
    list_gpus = []
    for gpu in gpus:
        gpu_id = gpu.id
        gpu_name = gpu.name
        return gpu_name


def get_os():
    platform_details = platform.platform()
    if platform_details.__contains__("Windows-10"):
        key = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        val = r"ReleaseID"

        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as key:
            releaseId = int(winreg.QueryValueEx(key, val)[0])

        platform_details = releaseId
        message = "Windows 10 {}".format(platform_details)
    else:
        message = platform_details
    return message


def get_cpu():
    return cpuinfo.get_cpu_info()['brand_raw']


def get_motherboard_serial():
    try:
        os_type = sys.platform.lower()
        if "win" in os_type:
            #command = "wmic baseboard get product,Manufacturer,version,serialnumber"
            serial_number = "wmic baseboard get serialnumber"
            motherboard_name = "wmic baseboard get product"
            manufacturer = "wmic baseboard get Manufacturer"


            serial_number = (os.popen(serial_number).read().replace("\n", "").replace("     ", "").replace("SerialNumber", "").replace("  ", ""))
            motherboard_name = (os.popen(motherboard_name).read().replace("\n", "").replace("     ","").replace("Product  ", "").replace("  ", ""))
            manufacturer = (os.popen(manufacturer).read().replace("\n", "").replace("Manufacturer           ", "").replace("  ", ""))

        motherboard_details = [serial_number, motherboard_name, manufacturer]

        return motherboard_details

        # output machine serial code: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXX
    except Exception:
        return "None"

def get_dell_servicetag():
    try:
        computer = wmi.WMI()
        bios_info = computer.Win32_SystemEnclosure()
        for info in bios_info:
            return info.SerialNumber
    except Exception:
        return "None"


# get windows key
def decode_key(rpk):
    rpkOffset = 52
    i = 28
    szPossibleChars = "BCDFGHJKMPQRTVWXY2346789"
    szProductKey = ""

    while i >= 0:
        dwAccumulator = 0
        j = 14
        while j >= 0:
            dwAccumulator = dwAccumulator * 256
            d = rpk[j + rpkOffset]
            if isinstance(d, str):
                d = ord(d)
            dwAccumulator = d + dwAccumulator
            rpk[j + rpkOffset] = int(dwAccumulator / 24) if int(dwAccumulator / 24) <= 255 else 255
            dwAccumulator = dwAccumulator % 24
            j = j - 1
        i = i - 1
        szProductKey = szPossibleChars[dwAccumulator] + szProductKey

        if ((29 - i) % 6) == 0 and i != -1:
            i = i - 1
            szProductKey = "-" + szProductKey
    return szProductKey


def get_key_from_reg_location(key, value='DigitalProductID'):
    arch_keys = [0, winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY]
    for arch in arch_keys:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key, 0, winreg.KEY_READ | arch)
            value, type = winreg.QueryValueEx(key, value)
            # Return the first match
            return decode_key(list(value))
        except (FileNotFoundError, TypeError) as e:
            pass


def get_windows_product_key_from_reg():
    return get_key_from_reg_location('SOFTWARE\Microsoft\Windows NT\CurrentVersion')


def get_windows_product_key_from_wmi():
    w = wmi.WMI()
    try:
        product_key = w.softwarelicensingservice()[0].OA3xOriginalProductKey
        if product_key != '':
            return product_key
        else:
            return None
    except AttributeError:
        return None


def get_windows_key():
    try:
        if __name__ == '__main__':
            # print('Windows Key from WMI: %s' % get_windows_product_key_from_wmi())
            return get_windows_product_key_from_reg()
    except Exception:
        return "None"

def get_wifi():
    try:
        # getting meta data
        meta_data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'])

        # decoding meta data
        data = meta_data.decode('utf-8', errors="backslashreplace")

        # spliting data by line by line
        data = data.split('\n')

        # creating a list of profiles
        profiles = []

        # traverse the data
        for i in data:

            # find "All User Profile" in each item
            if "All User Profile" in i:
                # if found
                # split the item
                i = i.split(":")

                # item at index 1 will be the wifi name
                i = i[1]

                # formatting the name
                # first and last chracter is use less
                i = i[1:-1]

                # appending the wifi name in the list
                profiles.append(i)

                # printing heading
        print("{:<30}| {:<}".format("Wi-Fi Name", "Password"))
        print("----------------------------------------------")

        # traversing the profiles
        for i in profiles:

            # try catch block beigins
            # try block
            try:
                # getting meta data with password using wifi name
                results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', i, 'key = clear'])

                # decoding and splitting data line by line
                results = results.decode('utf-8', errors="backslashreplace")
                results = results.split('\n')

                # finding password from the result list
                results = [b.split(":")[1][1:-1] for b in results if "Key Content" in b]

                # if there is passowrd it will print the pass word
                try:
                    print("{:<30}| {:<}".format(i, results[0]))

                    # else it will print blank in fornt of pass word
                except IndexError:
                    print("{:<30}| {:<}".format(i, ""))

                    # called when this process get failed
            except subprocess.CalledProcessError:
                print("Encoding Error Occured")
    except Exception:
        return "None"

def write_to_file():
    with open('computer_info.txt', 'w+') as f:
        f.write("User: {} \n".format(getpass.getuser()))
        f.write("CPU: {} \n".format(get_cpu()))
        f.write("RAM: {} \n".format(get_ram()))
        f.write("HD: {} \n".format(get_hd()))
        f.write("OS: {} \n".format(get_os()))
        f.write("Windows Key: {} \n".format(get_windows_key()))
        f.write("GPU: {} \n".format(get_gpu()))
        #Motherboard Serial, Name, Brand
        f.write("\nMotherboard--------------\n")
        f.write("\tBrand: {} \n".format(get_motherboard_serial()[2]))
        f.write("\tName: {} \n".format(get_motherboard_serial()[1]))
        f.write("\tSerial: {} \n".format(get_motherboard_serial()[0]))
        f.write("\n")
        f.write("Wifi Information: \n")
        f.write("Wifi: {}".format(get_wifi()))
        f.write("\n\n")
        f.write("Dell Service Tag: {} \n".format(get_dell_servicetag()))
    os.startfile('computer_info.txt')


write_to_file()


