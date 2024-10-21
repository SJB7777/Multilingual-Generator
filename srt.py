from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Self
import os

def srt_time2datetime(srt_time_str):

    h, m, s_ms = srt_time_str.split(':')
    s, ms = s_ms.split(',')

    h = int(h)
    m = int(m)
    s = int(s)
    ms = int(ms)

    time_obj = datetime(1, 1, 1, hour=h, minute=m, second=s) + timedelta(milliseconds=ms)
    return time_obj

def datetime_to_srt_time(time_obj):
    # SRT 시간 형식: 00:00:00,000
    return time_obj.strftime('%H:%M:%S,%f')[:-3]

@dataclass
class SrtLine:
    index: int
    s_time: datetime
    e_time: datetime
    text: str

    def copy(self) -> Self:
        return SrtLine(
            self.index,
            self.s_time.replace(),
            self.e_time.replace(),
            self.text
        )

    def set_text(self, text: str):
        self.text = text

    def to_srt_format(self) -> str:
        return f'''{self.index}
{datetime_to_srt_time(self.s_time)} --> {datetime_to_srt_time(self.e_time)}
{self.text}

'''
with open(".\\input\\setting.txt", encoding='utf-8') as f:
    LANGS = f.read().strip().split(', ')


class SrtManager:
    # def check_blocks(self, blocks: list[str]):

    #     for block_index, block in enumerate(blocks):

    #         sub_blocks = block.split('\n\n')
    #         lang_block = {lang: None for lang in LANGS}
    #         for sub_block in sub_blocks:

    #             lang, *txt = (v for v in sub_block.split('\n') if v)

    #             lang = lang.strip()[:-1]
    #             lang_block[lang] = txt

    #         len_dict = {}
    #         for lang, txt in lang_block.items():

    #             if txt is None:
    #                 print(f'[Block Index {block_index}] ', end='')
    #                 print('Empty:', lang)
    #             else:
    #                 len_dict[lang] = len(txt)

    #         for lang, length in len_dict.items():
    #             if length != len_dict['원어']:
    #                 print(f'[Block Index {block_index}] ', end='')
    #                 print('Length unmatch:', end=' ')
    #                 print(f'원어 줄수: {len_dict["원어"]}, {lang} 줄수: {length}')

    def make_lang_texts(self, text: str):

        text_chunks = text.strip().split("원어:")
        text_chunks = [block.strip() for block in text_chunks if block.strip()]
        text_chunks = ["원어:\n" + block for block in text_chunks]

        lang_texts: dict[str, list[str]] = {}
        for chunk in text_chunks:
            blocks = chunk.split('\n\n')
            lang_block = {lang: None for lang in LANGS}
            for block in blocks:
                lang, *txts = (v for v in block.split('\n') if v)
                lang = lang.strip()[:-1]
                lang_block[lang] = txts

            eng_len = len(lang_block['영어'])
            for lang, txts in lang_block.items():

                # 비일치 조정
                if txts is None:
                    lang_block[lang] = [None] * eng_len
                elif len(txts) != eng_len:
                    if len(txts) > eng_len:
                        # lang_block[lang] = txts[:eng_len-1] + ['\n'.join(txts[eng_len:])]
                        lang_block['영어'] = txts + [None] * (len(txts) - eng_len)
                    else:
                        lang_block[lang] = txts + [None] * (eng_len - len(txts))

            for lang, txts in lang_block.items():
                lang_texts[lang] = lang_texts.get(lang, []) + txts
        return lang_texts

    def read_input(self, input_srt: str, input_txt: str, out_put_dir: str):
        with open(input_srt, encoding='utf-8') as cap, open(input_txt, encoding='utf-8') as trans:
            caps = cap.read().strip().split('\n\n')
            deepseek_text = trans.read()

        lang_texts = self.make_lang_texts(deepseek_text)

        # srt_whole_texts = []

        # for cap in caps:
        #     index, times, *texts = cap.split('\n')

        #     srt_whole_texts.extend(texts)

        # for srt_text, txt in zip(srt_whole_texts, lang_texts['영어']):
        #     print(f"{srt_text:80}|{txt}")
        # for cap, txt in zip(caps, lang_texts['영어']):
        #     print(f'{cap[2:]} | {txt}')

        srt_lines_dict:dict[str, list[SrtLine]] = {}
        txt_index = 0
        for cap in caps:
            index, times, *cap_texts = cap.split('\n')
            index = int(index)
            s_time, e_time = map(srt_time2datetime, times.strip().split(' --> '))

            for lang, txts in lang_texts.items():
                srt_text = '\n'.join(
                    txt if txt is not None else ''
                    for txt in txts[txt_index:txt_index + len(cap_texts)]
                )
                srt_lines_dict[lang] = srt_lines_dict.get(lang, []) + [SrtLine(index, s_time, e_time, srt_text)]

            txt_index = txt_index + len(cap_texts)

        for lang, srts in srt_lines_dict.items():
            save_file: str = os.path.join(out_put_dir, f'{lang}.srt')
            with open(save_file, 'w', encoding='utf-8') as f:
                for srt in srts:
                    f.write(srt.to_srt_format())
            print(f"{save_file} 저장 완료")


if __name__ == '__main__':

    root: str = '.\\'
    input_srt_file: str = os.path.join(root, 'input\\captions.srt')
    input_txt_file: str = os.path.join(root, 'input\\trans.txt')
    output_dir: str = os.path.join(root, 'output')
    srt = SrtManager()
    srt.read_input(input_srt_file, input_txt_file, output_dir)
    print('프로그램 종료')

