import sys
import getopt
import subprocess
from os import mkdir, chdir, path, listdir
import re

ip = ''
ports = '80,443,8080,8443'
work_dir = ''
ip_regex = '(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(\/\d{1,2}|$)'


def fire():
    create_work_dir()
    is_pic_exist = launch_nmap()
    if is_pic_exist:
        create_preview_page()


def create_work_dir():
    global work_dir

    name = ''
    if '/' in ip:
        name = ip.split('/')
        name = name[0] + '_' + name[1]
        if not path.isdir(name):
            mkdir(name)
    else:
        if not path.isdir(ip):
            mkdir(ip)
        name = ip

    work_dir = name


def launch_nmap():
    print '[*] Launching nmap for ' + ip
    chdir(work_dir)
    try:
        subprocess.call('nmap --script=http-screenshot -v -p ' + ports + ' --max-retries 1 ' + ip, shell=True)
    except subprocess.CalledProcessError as err:
        print err
        sys.exit(1)
    chdir('..')

    for file_name in listdir(work_dir):
        if file_name.endswith('.png'):
            return True

    return False


def create_preview_page():
    chdir(work_dir)
    with open('preview.html', 'w+') as html_file:
        html_file.write('<html><head><title>' + work_dir + '</title></head><body>')
        for file_name in listdir('.'):
            if file_name.endswith('.png'):
                html_file.write(file_name + '<br>')
                html_file.write('<img src="./' + file_name + '" width=800 /><br><br>')
        html_file.write('</body></html>')
    chdir('..')


def main():
    global ports
    global ip

    file_path = ''

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:p:f:', ['ip', 'ports', 'file'])
    except getopt.GetoptError as err:
        print err
        sys.exit(1)

    for opt, arg in opts:
        if opt in ['-i', '--ip']:
            ip = arg
        elif opt in ['-p', '--ports']:
            ports = arg
        elif opt in ['-f', '--file']:
            file_path = arg
        else:
            print '[!] Required params not specified.'
            sys.exit(1)

    if file_path:
        with open(file_path) as file_with_ip:
            for line in file_with_ip:
                line = line.strip(' \t\r\n')
                if re.match(ip_regex, line):
                    ip = line
                    fire()
        sys.exit(1)

    if ip:
        if re.match(ip_regex, ip):
            fire()
        else:
            print '[!] IP address incorrect.'
            sys.exit(1)

    print '[*] Done!'

if __name__ == '__main__':
    main()