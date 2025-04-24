import re
import random
import os
import sys

def generate_obfuscated_name(length=8):
    hex_chars = "0123456789ABCDEF"
    hex_part = ''.join(random.choice(hex_chars) for _ in range(length))
    return f"_0x{hex_part}"

def remove_comments(code):
    # 刪除 C 風格的多行註釋 (/* ... */)
    code = re.sub(r'/\*[\s\S]*?\*/', '', code)
    
    # 刪除 C++ 風格的單行註釋 (// ...)
    code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
    
    return code

def obfuscate_cpp_with_regex(input_file, output_file):
    name_mapping = {}
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # 先刪除所有註釋，這樣可以更準確地識別變數和函數
        code_without_comments = remove_comments(code)
        
        # 完整的 C++ 關鍵字和 Arduino 保留名稱列表
        # 注意: set需要每個element用逗號連接，如果少逗號不會出現error，會忽略掉逗號後方的元素
        # A set requires each element to be separated by a comma. 
        # If a comma is missing, no error will occur, but the element after the missing comma will be ignored.

        reserved_names = set([

            # C++ 保留字
            'alignas', 'alignof', 'and', 'and_eq', 'asm',
            'auto', 'bitand', 'bitor', 'bool', 'break',
            'case', 'catch', 'char', 'char16_t', 'char32_t',
            'class', 'compl', 'const', 'constexpr', 'const_cast',
            'continue', 'decltype', 'default', 'delete', 'do',
            'double', 'dynamic_cast', 'else', 'enum', 'explicit',
            'export', 'extern', 'false', 'float', 'for',
            'friend', 'goto', 'if', 'inline', 'int',
            'long', 'mutable', 'namespace', 'new', 'noexcept',
            'not', 'not_eq', 'nullptr', 'operator', 'or',
            'or_eq', 'private', 'protected', 'public', 'register',
            'reinterpret_cast', 'return', 'short', 'signed', 'sizeof',
            'static', 'static_assert', 'static_cast', 'struct', 'switch',
            'template', 'this', 'thread_local', 'throw', 'true',
            'try', 'typedef', 'typeid', 'typename', 'union',
            'unsigned', 'using', 'virtual', 'void', 'volatile',
            'wchar_t', 'while', 'xor', 'xor_eq', 'size_t', 'byte','String','uint8_t','uint16_t','uint32_t',

            # cstring headers
            'memcpy', 'memmove', 'memset', 'memcmp',
            'strcpy', 'strncpy', 'strcat', 'strncat',
            'strcmp', 'strncmp', 'strchr', 'strrchr',
            'strstr', 'strlen', 'strspn', 'strcspn',
            'strpbrk', 'strtok', 'strerror',

            # cstdlib
            'malloc', 'calloc', 'realloc', 'free',
            'abort', 'exit', 'atexit', 'system',
            'getenv', 'atoi', 'atol', 'atoll',
            'strtod', 'strtof', 'strtold',
            'strtol', 'strtoll', 'strtoul', 'strtoull',
            'rand', 'srand', 'abs', 'labs', 'llabs',
            'div', 'ldiv', 'lldiv', 'bsearch', 'qsort',

            # cstdio
            'printf', 'fprintf', 'sprintf', 'snprintf',
            'vprintf', 'vfprintf', 'vsprintf', 'vsnprintf',
            'scanf', 'fscanf', 'sscanf',
            'fopen', 'freopen', 'fclose',
            'fflush', 'setbuf', 'setvbuf',
            'fread', 'fwrite', 'fgetc', 'fgets',
            'fputc', 'fputs', 'getc', 'getchar',
            'gets', 'putc', 'putchar', 'puts',
            'ungetc', 'fseek', 'ftell', 'rewind',
            'fgetpos', 'fsetpos', 'clearerr',
            'feof', 'ferror', 'perror', 'remove',
            'rename', 'tmpfile', 'tmpnam',

            # cmath
            'acos', 'asin', 'atan', 'atan2',
            'cos', 'sin', 'tan',
            'acosh', 'asinh', 'atanh',
            'cosh', 'sinh', 'tanh',
            'exp', 'frexp', 'ldexp',
            'log', 'log10', 'modf',
            'exp2', 'expm1', 'ilogb', 'log1p',
            'log2', 'logb', 'scalbn', 'scalbln',
            'pow', 'sqrt', 'cbrt', 'hypot',
            'fabs', 'abs', 'fmod', 'remainder',
            'remquo', 'fma', 'fmax', 'fmin',
            'fdim', 'nan', 'nearbyint', 'rint',
            'lrint', 'llrint', 'round', 'lround',
            'llround', 'trunc', 'ceil', 'floor',

            # Arduino 特定函數和常量
            'setup', 'loop', 'pinMode', 'digitalWrite', 'digitalRead', 
            'analogWrite', 'analogRead', 'delay', 'delayMicroseconds',
            'millis', 'micros', 'map', 'random', 'randomSeed', 'attachInterrupt',
            'detachInterrupt', 'interrupts', 'noInterrupts', 'Serial', 'print',
            'println', 'available', 'read', 'write', 'begin', 'end', 'random8',
            
            # Arduino 常量
            'HIGH', 'LOW', 'INPUT', 'OUTPUT', 'INPUT_PULLUP',
            'LED_BUILTIN', 'true', 'false', 'A0', 'A1', 'A2', 'A3', 'A4', 'A5',
            'LSBFIRST', 'MSBFIRST', 'CHANGE', 'FALLING', 'RISING',
            
            # AceRoutine 庫相關
            'COROUTINE', 'COROUTINE_LOOP', 'COROUTINE_YIELD', 'COROUTINE_DELAY',
            'COROUTINE_AWAIT', 'COROUTINE_END',
            
            # 其他常用函數
            'shiftOut', 'shiftIn', 'pulseIn', 'tone', 'noTone',
            
            # Arduino 類別
            'Servo', 'Wire', 'LiquidCrystal', 'SoftwareSerial', 'SD', 'Ethernet',

            # Fastled
            'FastLED', 'CRGB', 'CRGBPalette16','DEFINE_GRADIENT_PALETTE','blend','show',
            'CHSV', 'qsub8', 'qadd8', 'HeatColor', 'ColorFromPalette',

            # BT
            'BluetoothSerial',

            # RFID
            'Adafruit_PN532','begin','SAMConfig','getFirmwareVersion','sendCommandCheckAck',
            'writeGPIO','readGPIO','setPassiveActivationRetries','readPassiveTargetID',
            'startPassiveTargetIDDetection','readDetectedPassiveTargetID','inDataExchange',
            'inListPassiveTarget','AsTarget','getDataTarget','setDataTarget','reboot',
            'UnlockBackdoor','mifareclassic_IsFirstBlock','mifareclassic_IsTrailerBlock',
            'mifareclassic_AuthenticateBlock','mifareclassic_ReadDataBlock','mifareclassic_WriteDataBlock',
            'mifareclassic_FormatNDEF','mifareclassic_WriteNDEFURI','mifareultralight_ReadPage',
            'mifareultralight_WritePage','ntag2xx_ReadPage','ntag2xx_WritePage','ntag2xx_WriteNDEFURI',
            'PrintHex','PrintHexChar'
        ])

        
        # 1. 識別 Arduino 物件宣告
        obj_pattern = r'(\b(?:Servo|Wire|LiquidCrystal|SoftwareSerial|SD|Ethernet|CRGB|CRGBPalette16|BluetoothSerial|Adafruit_PN532)\b)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        obj_matches = re.finditer(obj_pattern, code_without_comments)
        for match in obj_matches:
            obj_type = match.group(1)
            obj_name = match.group(2)
            if obj_name not in name_mapping and obj_name not in reserved_names:
                name_mapping[obj_name] = generate_obfuscated_name()

        # 2. 識別函數名和參數
        func_pattern = r'(void|int|float|double|char|bool|byte|COROUTINE|String|uint8_t|uint16_t|uint32_t|#define)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)'
        func_matches = re.finditer(func_pattern, code_without_comments)
        for match in func_matches:
            func_name = match.group(2)
            if func_name not in name_mapping and func_name not in reserved_names:
                name_mapping[func_name] = generate_obfuscated_name()

            # 處理函數參數
            param_str = match.group(3)
            if param_str:
                # 改進的參數匹配，處理各種類型
                param_pattern = r'(?:int|float|double|char|bool|byte|String|uint8_t|uint16_t|uint32_t|unsigned\s+int)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:,|$)'
                param_matches = re.finditer(param_pattern, param_str)
                for param_match in param_matches:
                    param_name = param_match.group(1)
                    if param_name and param_name not in name_mapping and param_name not in reserved_names:
                        name_mapping[param_name] = generate_obfuscated_name()
        
        # 3. 直接搜索參數定義行
        param_line_pattern = r'void\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(\s*int\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\)'
        param_line_matches = re.finditer(param_line_pattern, code_without_comments)
        for match in param_line_matches:
            param_name = match.group(1)
            if param_name not in name_mapping and param_name not in reserved_names:
                name_mapping[param_name] = generate_obfuscated_name()
        
        
        # 4. 識別普通變數
        # function 內的變數定義
        var_patterns = [
            r'(const\s+)?(int|float|double|char|bool|String|uint8_t|uint16_t|uint32_t|byte|static\s+int)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:=|\[|;)',
            r'static\s+int\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'int\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\[\d+\](?:\[\d+\])?\s*=',
            r'\bfor\s*\(\s*int\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'\bbyte\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*='
        ]
        
        for pattern in var_patterns:
            var_matches = re.finditer(pattern, code_without_comments)
            for match in var_matches:
                # 取最後一個捕獲組作為變數名
                var_name = match.groups()[-1]
                if var_name not in name_mapping and var_name not in reserved_names:
                    name_mapping[var_name] = generate_obfuscated_name()
        
        # 5. 特別處理特定函數中的參數
        # 尋找像 "void function(int ledIndex)" 的模式
        special_param_pattern = r'void\s+[a-zA-Z0-9_]+\s*\(\s*int\s+ledIndex\s*\)'
        if re.search(special_param_pattern, code_without_comments):
            if 'ledIndex' not in name_mapping and 'ledIndex' not in reserved_names:
                name_mapping['ledIndex'] = generate_obfuscated_name()
        
        # 混淆代碼
        obfuscated_code = code
        
        # 按長度排序原始名稱，避免較短的名稱作為較長名稱的一部分被錯誤替換
        sorted_names = sorted(name_mapping.keys(), key=len, reverse=True)
        
        # 替換所有匹配的名稱
        for original_name in sorted_names:
            obfuscated_name = name_mapping[original_name]
            pattern = r'\b' + re.escape(original_name) + r'\b'
            obfuscated_code = re.sub(pattern, obfuscated_name, obfuscated_code)
        
        # 移除所有註釋
        obfuscated_code = remove_comments(obfuscated_code)
        
        # 寫入輸出文件 - 不添加註釋
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(obfuscated_code)
        
        print(f"結果已寫入 {output_file}")
        print(f"共混淆了 {len(name_mapping)} 個變數名和函數名")
        
        # 可選：輸出映射表供參考 (按原始名稱字母排序)
        print("\n變數名映射:")
        for orig, new in sorted(name_mapping.items()):
            print(f"{orig} -> {new}")
        
    except Exception as e:
        print(f"正則表達式混淆出錯: {e}")
        import traceback
        traceback.print_exc()

def main():
    if len(sys.argv) < 2:
        print("使用方法: python SketchObfus.py [input_file.ino]")
        print("或: python SketchObfus.py [input_file.ino] [output_file.ino]")
        return
    
    input_file = sys.argv[1]
    
    # 自動生成輸出文件名
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        base_name, ext = os.path.splitext(input_file)
        output_file = f"{base_name}_obf{ext}"
    
    obfuscate_cpp_with_regex(input_file, output_file)  # 直接使用正則表達式方法

if __name__ == "__main__":
    main()