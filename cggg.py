#外來語ᄂᆞᆫ 鮮和兩人모던朝鮮外來語辭典ㅅ資料ᄅᆞᆯ 參考하느니라。
#漢字語ᄂᆞᆫ 漢字로 表記하느니라。  - 寶石 -



##라이부러리##
from pathlib import Path    #ᅋᅡ일 經路 라이부러리
from PIL import Image       #이마ーᅎᅵ ᅋᅡ일 操作 라이부러리

from fontTools.pens.ttGlyphPen import TTGlyphPen #.ttf 輪郭線 라이부러리
from fontTools.fontBuilder import FontBuilder        #.ttf 鍊成 라이부러리

from rules import *       #組合 規則 데ー타


##띠자인 初期化##
UPM = 1000
CHO_RANGE = [
    range(0x1100, 0x1160),
    range(0xA960, 0xA980),
]
JUNG_RANGE = [
    range(0x1161, 0x11A8),
    range(0xD7B0, 0xD7C7),
]
JONG_RANGE = [
    range(0x11A8, 0x1200),
    range(0xD7CB, 0xD7FC),
]



##함수 - 자모 수집##
def collect_jamo():
    cho = set()
    jung = set()
    jong = set()

    for r in CHO_RANGE:
        for value in r:
            cho.add(chr(value))
    for r in JUNG_RANGE:
        for value in r:
            jung.add(chr(value))
    for r in JONG_RANGE:
        for value in r:
            jong.add(chr(value))

    return cho, jung, jong



##函數 - 그뤂名 리턴##
def get_group(value, groups):
    for key, chars in groups.items():
        if value in chars:
            return key
    return None



##函數 - 初-中-終 區分##
def get_jamo(char):
    char = ord(char)
    
    if (char >= 0x1100 and char <= 0x115f) or (char >= 0xa960 and char <= 0xa97c):
        return "CHO"
    elif (char >= 0x1161 and char <= 0x11a7) or (char >= 0xD7B0 and char <= 0xD7C6):
        return "JUNG"
    elif (char >= 0x11a8 and char <= 0x11ff) or (char >= 0xD7CB and char <= 0xD7FB):
        return "JONG"
    
    return "IDK"



##函數 - 끌리프 브ᄅᆞ와오기##
def glyph_png_path(char, chars):
    match get_jamo(char):
        case "CHO":
            if len(chars)<=2: #終聲 有無
                group = get_group(chars[1], CHO_N_GROUP)
            else:
                group = get_group(chars[1],CHO_Y_GROUP)
            
        case "JUNG":
            if len(chars)<=2: #終聲 有無
                group = get_group(chars[0], JUNG_N_GROUP)
            else:
                group = get_group(chars[0],JUNG_Y_GROUP)
            
        case "JONG":
            group = get_group(chars[1],JONG_GROUP)
            
            #初聲에 의한 中聲 幅 변경에 따른 終聲의 경우
            if (chars[0] in JUNG_D) and (chars[1] in JONG_DD):
                match group:
                    case "VS":
                        group = "VD"
                    case "VD":
                        group = "H"
    
    return Path("Glyphs") / get_jamo(char) / group / f"U+{ord(char):04X}.png"



##함수 - 첫가끝 조합 생성##
def make_sequences():

    cho, jung, jong = collect_jamo()

    sequences = []

    for c in cho:

        for v in jung:

            # 초성 + 중성
            sequences.append(c + v)

            # 초성 + 중성 + 종성
            for j in jong:
                sequences.append(c + v + j)

    return sequences



##函數 - 이마ーᅎᅵ ᅋᅡ일 마스크化##
def load_png_mask(path):
    #이마ーᅎᅵ 브ᄅᆞ와오기
    image = Image.open(path).convert("RGBA")
    pixels = image.load()

    #알ᅋᅡ >= 1  : 참
    #알ᅋᅡ <   1  : 거짓
    return [
        [
            pixels[x, y][3] >= 1
            for x in range(PIXEL_SIZE)
        ]
        for y in range(PIXEL_SIZE)
    ]


##函數 - 마스크서 끌리프##
def mask_to_glyph(mask):
    #PPAP; Pen-Pineapple-Apple-Pen
    pen = TTGlyphPen(None)
    
    for y in range(PIXEL_SIZE):
        x = 0

        while x < PIXEL_SIZE:
            if not mask[y][x]:
                x += 1
                continue

            #連續된 픽셀 ᅀᅵᆮ기
            start_x = x
            while x < PIXEL_SIZE and mask[y][x]:
                x += 1
            end_x = x

            #連續 픽셀 範圍 座標 指定
            x0 = start_x * PIXEL_UNIT
            x1 = end_x * PIXEL_UNIT
            y1 = (PIXEL_SIZE - y) * PIXEL_UNIT
            y0 = (PIXEL_SIZE - y - 1) * PIXEL_UNIT
            #座標대로 끌리프 그리기
            pen.moveTo((x0, y0))
            pen.lineTo((x1, y0))
            pen.lineTo((x1, y1))
            pen.lineTo((x0, y1))
            pen.closePath()

    return pen.glyph()


##
def make_notdef():
    pen = TTGlyphPen(None)

    pen.moveTo((100, 100))
    pen.lineTo((900, 100))
    pen.lineTo((900, 900))
    pen.lineTo((100, 900))
    pen.closePath()

    return pen.glyph()


##
def make_base_glyphs():
    cho, jung, jong = collect_jamo()
    chars = cho | jung | jong
    glyphs = {}

    for char in chars:
        glyphs[f"u{ord(char):04X}"] = TTGlyphPen(None).glyph()

    return glyphs


##폰트 제작##
def build_font():
    cho, jung, jong = collect_jamo()

    sequences = make_sequences()



##메인##
if __name__ == "__main__":
    build_font()
