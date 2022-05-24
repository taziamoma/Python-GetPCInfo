import psutil, platform, GPUtil, cpuinfo, os, sys, wmi, winreg, getpass, subprocess
from tabulate import tabulate
from datetime import datetime
from multiprocessing import Process, freeze_support


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
    w = wmi.WMI()
    try:
        gpu = w.win32_VideoController()[0].name
        if gpu != '':
            return gpu
        else:
            return None
    except AttributeError:
        return None
    # gpus = GPUtil.getGPUs()
    # list_gpus = []
    # for gpu in gpus:
    #     gpu_id = gpu.id
    #     gpu_name = gpu.name
    #     return gpu_name


def get_os():
    system_name = platform.system()
    system_version = platform.release()
    system_build = platform.version().split('.')[2]

    return "{} {} {}".format(system_name, system_version, system_build)


def get_cpu():
    return cpuinfo.get_cpu_info()['brand_raw']


def get_motherboard_serial():
    try:
        os_type = sys.platform.lower()
        if "win" in os_type:
            # command = "wmic baseboard get product,Manufacturer,version,serialnumber"
            serial_number = "wmic baseboard get serialnumber"
            motherboard_name = "wmic baseboard get product"
            manufacturer = "wmic baseboard get Manufacturer"

            serial_number = (
                os.popen(serial_number).read().replace("\n", "").replace("     ", "").replace("SerialNumber",
                                                                                              "").replace("  ", ""))
            motherboard_name = (
                os.popen(motherboard_name).read().replace("\n", "").replace("     ", "").replace("Product  ",
                                                                                                 "").replace("  ", ""))
            manufacturer = (
                os.popen(manufacturer).read().replace("\n", "").replace("Manufacturer           ", "").replace("  ",
                                                                                                               ""))

        motherboard_details = [serial_number, motherboard_name, manufacturer]

        return motherboard_details

        # output machine serial code: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXX
    except Exception:
        return "None"


def get_service_tag():
    try:
        computer = wmi.WMI()
        bios_info = computer.Win32_SystemEnclosure()
        for info in bios_info:
            return info.SerialNumber
    except Exception:
        return "None"


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
        return get_windows_product_key_from_wmi()
    except Exception:
        return "None"


def get_wifi():
    wifi_keys = {}
    try:
        data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8').split('\n')
        profiles = [i.split(":")[1][1:-1] for i in data if "All User Profile" in i]
        for i in profiles:
            results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', i, 'key=clear']).decode(
                'utf-8').split('\n')
            results = [b.split(":")[1][1:-1] for b in results if "Key Content" in b]
            wifi_keys[i] = results

    except Exception:
        return "None"

    return wifi_keys


def computer_name():
    c = wmi.WMI()
    my_system = c.Win32_ComputerSystem()[0]

    return my_system.Model


def computer_manufacturer():
    c = wmi.WMI()
    my_system = c.Win32_ComputerSystem()[0]

    return my_system.Manufacturer


def print_wifi(wifi_keys, f):
    for key, value in wifi_keys.items():
        f.write("{}: {}\n".format(key, value).replace("[", "").replace("]", ""))


def write_to_file():
    with open('computer_info.txt', 'w+') as f:
        f.write("Computer Name--------------\n")
        f.write("Model: {} \n".format(computer_name()))
        f.write("{} Service Tag: {} \n".format(computer_manufacturer(), get_service_tag()))
        f.write("\nComputer Specifications--------------\n")
        f.write("User: {} \n".format(getpass.getuser()))
        f.write("CPU: {} \n".format(get_cpu()))
        f.write("RAM: {} \n".format(get_ram()))
        f.write("HD: {} \n".format(get_hd()))
        f.write("OS: {} \n".format(get_os()))
        f.write("Windows Key: {} \n".format(get_windows_key()))
        f.write("GPU: {} \n".format(get_gpu()))
        # Motherboard Serial, Name, Brand
        f.write("\nMotherboard--------------\n")
        f.write("\tBrand: {} \n".format(get_motherboard_serial()[2]))
        f.write("\tName: {} \n".format(get_motherboard_serial()[1]))
        f.write("\tSerial: {} \n".format(get_motherboard_serial()[0]))
        f.write("\n")
        f.write("Wifi Information: \n")
        f.write("Wifi: {}".format(print_wifi(get_wifi(), f)))
        f.write("\n\n")




write_to_file()
os.startfile('computer_info.txt')