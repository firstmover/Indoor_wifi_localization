# Indoor_wifi_localization

## 运行环境说明

- 建议运行环境: ubuntu 16.x as sudo, python3
- 硬件要求: 支持monitor mode的网卡

## 运行前准备

- 查看所要运行网卡编号

  > iwconfig

  ![1526893820255](./figures/iwconfig1.png)

  如图这里选择wlan网卡**wlp3s0**

- 查看对应无线网卡是否支持**monitor mode**

  > iw list

   ![1526895198531](./figures/iwlist.png)

- 修改脚本**setmon.sh**,将其中的网卡名称换成对应的网卡名称

- **以管理员身份**执行**setmon.sh**，将网卡配置为**monitor mode**

  > sudo ./setmon.sh

  脚本会要求输入管理员密码，同时会关闭**network-manager**, 即之后无法使用该网卡联网

  运行之后可以执行

  > iwconfig

  确认所要运行的网卡已经处于**monitor mode**![1526894507738](./figures/iwconfig2.png)

- 配置输入SSID文件，文件中每一行对应一个所要提取rssi的AP的SSID,如下![1526894302071](./figures/ssid.png)

- 以**管理员身份**运行程序**sniff_rssi.py**, 注意以**python3**执行，执行**sudo python3 sniff_rssi.py -h**查看帮助，示例运行如下

  >sudo python3 sniff_rssi.py --iface wlp3s0 --input ssids.txt --output rssi.json --amount 100

  注意程序会将提取的rssi保存为**json**

- 运行完毕关闭**monitor mode**并开启**network-manager**

  > sudo ./unsetmon.sh



## 参考资料

- 关于**monitor mode**和一般网卡提取rssi的问题：https://wiki.wireshark.org/CaptureSetup/WLAN#Linux
- 开启**monitor mode**的另一工具: http://www.aircrack-ng.org/doku.php?id=airmon-ng
