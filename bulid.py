#外來語ᄂᆞᆫ 鮮和兩人모던朝鮮外來語辭典ㅅ資料ᄅᆞᆯ 參考하느니라。
#漢字語ᄂᆞᆫ 漢字로 表記하느니라。  - 寶石 -



##라이부러리##
from pathlib import Path    #ᅋᅡ일 經路 라이부러리
from PIL import Image       #이마ーᅎᅵ ᅋᅡ일 操作 라이부러리

from fontTools.pens.ttGlyphPen import TTGlyphPen #.ttf 輪郭線 라이부러리
from fontTools.fontBuilder import FontBuilder        #.ttf 鍊成 라이부러리

from mapping import *  #漢陽-퓨아 組合 規則 데ー타
from rules import *       #漢陽-퓨아 組合 規則 데ー타



##띠자인 初期化##
PIXEL_SIZE = 13
PIXEL_UNIT = 64
UPM = PIXEL_SIZE * PIXEL_UNIT



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



##函數 - 字母 어우르기##
def compose_jamo_images(chars):
    #칸바스 初期化
    result = [
        [False] * PIXEL_SIZE
        for _ in range(PIXEL_SIZE)
    ]
    
    for char in chars:
        #자모 ᅋᅡ일 브ᄅᆞ와오기 -> 마스크化
        mask = load_png_mask(glyph_png_path(char, chars))

        #칸바스에 브티기
        for y in range(PIXEL_SIZE):
            for x in range(PIXEL_SIZE):
                if mask[y][x]: result[y][x] = True

    return result



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



##函數 - .ttf化##
def build_font():
    glyph_order = [".notdef", "space",]
    glyphs = {}

    #虛 끌리프(.notdef) ᄆᆞᆫᄃᆞᆯ기
    notdef_pen = TTGlyphPen(None)
    glyphs[".notdef"] = notdef_pen.glyph()
    #宇宙(space) ᄆᆞᆫᄃᆞᆯ기
    space_pen = TTGlyphPen(None)
    glyphs["space"] = space_pen.glyph()

    #유니-코드: "끌리프名"
    cmap = {0x20: "space",}

    #字文 幅 指定
    advance_width = PIXEL_SIZE * PIXEL_UNIT

    #漢陽-퓨아 處理
    for codepoint, jamo_string in DICT_HYPUA.items():
        codepoint = int(codepoint)             #10進 유니-코드
        glyph_name = f"uni{codepoint:04X}"  #字母 集合 文字列

        mask = compose_jamo_images(jamo_string)  #字母 합친 거 브ᄅᆞ와오기
        glyphs[glyph_name] = mask_to_glyph(mask)  #끌리프 <- 마스크 너흐기

        glyph_order.append(glyph_name)
        cmap[codepoint] = glyph_name

    #ᅋᅩᆫ트 生成者ᄅᆞᆯ 生成 下下下下下下
    fb = FontBuilder(UPM, isTTF=True)

    #處理한 데ー타 全部 適用하기
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)

    #字文 幅 初期化
    metrics = {
        glyph_name: (advance_width, 0)
        for glyph_name in glyph_order
    }
    fb.setupHorizontalMetrics(metrics)

    #字文도 위 아래가 있ᄉᆞᆸ니다
    fb.setupHorizontalHeader(
        ascent=UPM,
        descent=0,
    )

    #몰라
    fb.setupOS2(
        sTypoAscender=UPM,
        sTypoDescender=0,
        usWinAscent=UPM,
        usWinDescent=0,
    )

    #ᅋᅩᆫ트 정보 初期化
    fb.setupNameTable({
        "familyName": "My Hanyang Pixel",
        "styleName": "Regular",
        "fullName": "My Hanyang Pixel Regular",
        "psName": "MyHanyangPixel-Regular",
        "uniqueFontIdentifier": "MyHanyangPixel-Regular",
    })

    fb.setupPost()

    fb.save("output.ttf")
    print("完成ᄒᆞ얏ᄉᆞᆸ니다!!")



##메인##
if __name__ == "__main__":
    build_font()
