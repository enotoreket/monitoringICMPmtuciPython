# -*- coding: cp1251 -*-
import argparse
import platform
import subprocess
import time
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class HostStatus:
    host: str
    is_alive: bool
    latency: float  # в миллисекундах
    last_check: float  # timestamp


class NetworkMonitor:
    def __init__(self, hosts: List[str], interval: float = 5.0, timeout: int = 1000):
        self.hosts = hosts
        self.interval = interval  # интервал проверки в секундах
        self.timeout = timeout  # таймаут ping в миллисекундах
        self.statuses: Dict[str, HostStatus] = {}

        # Инициализация статусов для всех хостов
        for host in hosts:
            self.statuses[host] = HostStatus(host, False, 0.0, 0.0)

    def ping(self, host: str) -> (bool, float):
        #Выполняет ping указанного хоста и возвращает (доступен, задержка)
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        timeout_ms = self.timeout

        try:
            # Выполняем ping с 1 пакетом и таймаутом
            command = ['ping', param, '1', '-w', str(timeout_ms), host]
            output = subprocess.run(command, capture_output=True, text=True, timeout=(timeout_ms / 1000 + 1),encoding='cp866')
            # Парсим вывод для получения времени
            if 'время' in output.stdout:
                time_str = output.stdout.split('время')[1].split()[0][1:]
                latency = float(time_str.replace('мс', ''))
                return True, latency
            elif 'time' in output.stdout:
                time_str = output.stdout.split('time')[1].split()[0][1:]
                latency = float(time_str.replace('ms', ''))
                return True, latency
            return False, 0.0
        except:
            return False, 0.0

    def check_hosts(self):
        #Проверяет все хосты и обновляет их статусы
        for host in self.hosts:
            is_alive, latency = self.ping(host)
            self.statuses[host] = HostStatus(
                host=host,
                is_alive=is_alive,
                latency=latency,
                last_check=time.time()
            )

    def run_continuous_monitoringCicle(self):
        #Запускает непрерывный мониторинг
        print(f"Starting network monitoring for {len(self.hosts)} hosts...")
        try:
            while True:
                self.check_hosts()
                self.print_statuses()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")

    def run_continuous_monitoring(self):
        print(f"Network monitoring for {len(self.hosts)} hosts...")
        try:
            self.check_hosts()
            self.print_statuses()
            time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
    def print_statuses(self):
        #Выводит текущие статусы хостов
        print("\n" + "=" * 50)
        print(f"Status at {time.strftime('%H:%M:%S  %d.%m.%Y')}")
        for host, status in self.statuses.items():
            status_str = "UP" if status.is_alive else "DOWN"
            latency_str = f"{status.latency:.2f}ms" if status.is_alive else "N/A"
            print(f"{host:20} {status_str:5} Latency: {latency_str}")


if __name__ == "__main__":
    hosts_to_monitor = []
    with open('hosts.txt') as f:
        raw_hosts_to_monitor = f.readlines()
    for i in range(len(raw_hosts_to_monitor)):
        host = raw_hosts_to_monitor[i].replace("\n","")
        if host not in hosts_to_monitor:
            hosts_to_monitor.append(host)
    parser = argparse.ArgumentParser(description ='Monitoring ip')
    parser.add_argument('-c',
                        type=str,
                        help="Arguments, need for not cycle program",
                        default=None)
    args = parser.parse_args()
    monitor = NetworkMonitor(hosts=hosts_to_monitor, interval=2.0)
    if args.c:
        monitor.run_continuous_monitoring()
    else:
        monitor.run_continuous_monitoringCicle()
