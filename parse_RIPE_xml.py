import sys
import getopt
from StringIO import StringIO
from lxml import etree
from math import log


def prepare_net_block(net_block):
    # Supported format: 109.106.192.0 - 109.106.199.255
    if ' - ' in net_block:
        network, broadcast = net_block.split(' - ')
        start = network.split('.')
        end = broadcast.split('.')
        bit = 0
        for i in range(4):
            if int(end[i]) - int(start[i]) == 0:
                bit += 8
            else:
                # Difference with next subnet
                dif = (int(end[i]) + 1) - int(start[i])
                # How many bits belong to network
                bit += 8 - int(log(dif, 2))
                break
        return network + '/' + str(bit)
    else:
        print '[!] Unsupported format of ip range.'


def parse_xml(xml_file):
    net_blocks = []
    with open(xml_file) as input_file:
        xml = input_file.read()
    tree = etree.parse(StringIO(xml))
    root = tree.getroot()
    for obj in root.findall('.//object'):
        if obj.attrib['type'] == 'inetnum':
            list = []
            for attribute in obj.findall('.//attributes/attribute'):
                if attribute.attrib['name'] == 'inetnum':
                    list.append(unicode(attribute.attrib['value']))
                elif attribute.attrib['name'] == 'netname':
                    list.append(unicode(attribute.attrib['value']))
                elif attribute.attrib['name'] == 'descr':
                    list.append(unicode(attribute.attrib['value']))
            net_blocks.append(list)
    return net_blocks


def main():
    source_file = ''
    output_file = ''
    out_format = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:o:w', ['input', 'output', 'wssm'])
    except getopt.GetoptError as err:
        print err
        sys.exit(1)

    for o, a in opts:
        if o in ['-i', '--input']:
            source_file = a
        elif o in ['-o', '--output']:
            output_file = a
        elif o in ['-w', '--wssm']:
            out_format = True
        else:
            sys.exit(1)

    if source_file:
        net_blocks = parse_xml(source_file)
        formatted = []
        if out_format:
            for net_block in net_blocks:
                formatted.append(prepare_net_block(net_block[0]) + '\n')
        else:
            for net_block in net_blocks:
                formatted.append(' | '.join(net_block) + '\n')

        if output_file:
            with open(output_file, 'w+') as out_file:
                for rec in formatted:
                    out_file.write(rec)
            print '[*] Data was saved in ' + output_file
        else:
            for rec in formatted:
                print rec


if __name__ == '__main__':
    main()
