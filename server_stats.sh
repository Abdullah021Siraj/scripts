#!/bin/bash

cpu_usage(){
echo "Total CPU Usage"
top -bn2 | grep "%Cpu" | tail -1 | awk '{print "CPU Usage(%): " 100-$8 "%"} {print "CPU Usage: " $8}'
echo ""
}

memory_usage(){
echo "Total Memory Usage"
free -m | awk 'NR==2 {used=$3+$5; free=$7; total=$2; printf "Used: %dMB (%.2f%%)\nFree: %dMB (%.2f%%)\n", used, used/total*100, free, free/total*100}'
echo ""
}

disk_usage(){
df -h --total | awk '/^total/ {used=$3; free=$4; total=$2; printf "Used: %s (%.2f%%)\nFree: %s (%.2f%%)\n", used, used/total*100, free, free/total*100}'
echo ""
}

top5_cpu_usage(){
echo "Top 5 CPU Usage"
ps -eo pid,comm,%cpu --sort=-%cpu | head -n 6
echo ""
}

top5_memory_usage(){
echo "Top 5 Memory Usage"
ps -eo pid,comm,%mem --sort=-%mem | head -n 6
echo ""
}

additional_info(){
echo "Additional Info"
echo ""
echo "System Info: $(hostnamectl)"
echo "Uptime: $(uptime -p)"
echo "Logged in Users: $(who | wc -l)"
echo ""
}

echo "Server Performance Stats"
echo ""
main() {
cpu_usage
memory_usage
disk_usage
top5_cpu_usage
top5_memory_usage
additional_info
}

main
