import argparse
from lxml import etree
import os
import time


TYPE_MAPPING = {
    '&surname;': '名字',
    '&place;': '地名',
    # '&unclass;': '',
    '&company;': '商号',
    '&product;': 'ブランド',
    '&work;': '著作物',
    '&masc;': '男性名',
    '&fem;': '女性名',
    '&person;': '氏名',
    '&given;': '下の名前',
    '&station;': '駅名',
    '&organization;': '組織の名称・呼称',
    # '&ok;': '',
}


def parse_jmnedict(xmltree, output_path, included_types):
    if included_types is not None:
        included_types = list(map(lambda x: '&'+x+';', included_types))
    entries_processed = 0
    entries_written = 0
    with open(output_path, mode='w', encoding="utf-8-sig") as output_desc:
        for trans_ele in xmltree.xpath("//entry/trans"):
            entry = trans_ele.getparent()
            if included_types is None:
                process_entry_to_stream(entry, None, output_desc)
                entries_written = entries_written + 1
            else:
                # get all types for this entry
                name_type_eles = trans_ele.findall('name_type')
                if len(name_type_eles) > 0:
                    entry_type_vals = [name_type_ele[0].text for
                                       name_type_ele in name_type_eles]

                    # only process if there are matching types
                    entry_type_matches = list(set(entry_type_vals) & set(included_types))
                    if len(entry_type_matches) > 0:
                        process_entry_to_stream(entry, entry_type_matches, output_desc)
                        entries_written = entries_written + 1
            entries_processed = entries_processed + 1
            # if entries_written > 200:
            #     break  # DEBUG: bail out early

    return entries_processed


# Output entry using this CSV definition
# https://mentaldetritus.blogspot.com/2013/03/compiling-custom-dictionary-for.html
# Field 1 - entry
# Fields 2-4 - Left cost/Right cost/entry cost
# Fields 5-10 - Part of speech
# Field 11 - Base form
# Field 12 - Reading
# Field 13 - Pronunciation
# + match NLPJapaneseDictionary.KuromojiIpadic.Compile.DictionaryEntry
# Note: those are zero-based
# PART_OF_SPEECH_LEVEL_1 = 4;
# PART_OF_SPEECH_LEVEL_2 = 5;
# PART_OF_SPEECH_LEVEL_3 = 6;
# PART_OF_SPEECH_LEVEL_4 = 7;
# CONJUGATION_TYPE = 8;
# CONJUGATION_FORM = 9;
# BASE_FORM = 10;
# READING = 11;
# PRONUNCIATION = 12;

# see samples @ https://github.com/neologd/mecab-ipadic-neologd/tree/master/seed
def process_entry_to_stream(entry_element, entry_types, outfd):
    if entry_types is None:
        entry_types_eles = entry_element.findall('.//name_type')
        if len(entry_types_eles) > 0:
            entry_types = [entry_types_ele[0].text for
                           entry_types_ele in entry_types_eles]
        else:
            entry_types = []

    for entry_type in entry_types:
        for k_ele in entry_element.findall('k_ele'):  # For every Kanji Element in an entry
            keb = k_ele.find('keb')
            # for sake of simplicity, only keep the first reading
            r_ele = entry_element.find('.//r_ele/reb')
            csv_line = '{},{},{},{},{},{},{},{},{},{},{}'.format(
                keb.text,
                500, 500, 1200,
                '名詞',  # PART_OF_SPEECH_LEVEL_1
                '固有名詞',  # PART_OF_SPEECH_LEVEL_2
                TYPE_MAPPING.get(entry_type, '一般'),  # PART_OF_SPEECH_LEVEL_3
                keb.text,  # PART_OF_SPEECH_LEVEL_4
                '*,*,*',  # CONJUGATION_TYPE, CONJUGATION_FORM, BASE_FORM)
                r_ele.text,  # READING
                r_ele.text)  # PRONUNCIATION
            outfd.write(csv_line + "\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input_xml",
                        nargs='?',
                        default="JMnedict.xml",
                        help="XML file to process (default: JMnedict.xml)")
    parser.add_argument("--include",
                        type=str,
                        dest="included_types",
                        help="Comma-separated list of JMnedict entry types to include (DTD entities)."
                        )
    parser.add_argument("--output",
                        type=str,
                        default=None,
                        help="OUTPUT kuromoji-compatible CSV userdict target file."
                        )
    args = parser.parse_args()
    # args.included_types = 'surname,masc,fem,given'
    if args.included_types is not None:
        args.included_types = args.included_types.split(',')
    if args.output is None:
        args.output = os.path.join(
                            os.path.dirname(args.input_xml),
                            os.path.splitext(os.path.basename(args.input_xml))[0] + '.csv')
    print("XML parsing: {0}".format(args.input_xml))
    start_time = time.time()
    xmlparser = etree.XMLParser(ns_clean=True, remove_blank_text=True, resolve_entities=False)
    xmltree = etree.parse(args.input_xml, xmlparser)
    print("Built DOM in {0:.2f} seconds".format(time.time() - start_time))

    start_time = time.time()
    num_processed = parse_jmnedict(xmltree, args.output, args.included_types)
    print("Processed {0} entries in {1:.2f} seconds".format(num_processed,
                                                            time.time() - start_time))
