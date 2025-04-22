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
        reserved_names = set([
            # C++ 關鍵字
            'if', 'else', 'for', 'while', 'do', 'break', 'continue', 'return',
            'switch', 'case', 'default', 'goto', 'try', 'catch', 'throw',
            'new', 'delete', 'this', 'class', 'struct', 'union', 'enum',
            'template', 'typedef', 'typename', 'namespace', 'using', 'public',
            'private', 'protected', 'virtual', 'static', 'const', 'volatile',
            'auto', 'register', 'extern', 'inline', 'explicit', 'friend',
            'operator', 'sizeof', 'asm', 'export', 'true', 'false', 'nullptr',
            
            # C++ 內建類型
            'void', 'int', 'char', 'short', 'long', 'float', 'double',
            'signed', 'unsigned', 'bool', 'wchar_t', 'size_t', 'byte',
            
            # Arduino 特定函數和常量
            'setup', 'loop', 'pinMode', 'digitalWrite', 'digitalRead', 
            'analogWrite', 'analogRead', 'delay', 'delayMicroseconds',
            'millis', 'micros', 'map', 'random', 'randomSeed', 'attachInterrupt',
            'detachInterrupt', 'interrupts', 'noInterrupts', 'Serial', 'print',
            'println', 'available', 'read', 'write', 'begin', 'end',
            
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
            'Servo', 'Wire', 'LiquidCrystal', 'SoftwareSerial', 'SD', 'Ethernet'
        ])
        
        # 1. 識別 Arduino 物件宣告
        obj_pattern = r'(\b(?:Servo|Wire|LiquidCrystal|SoftwareSerial|SD|Ethernet)\b)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        obj_matches = re.finditer(obj_pattern, code_without_comments)
        for match in obj_matches:
            obj_type = match.group(1)
            obj_name = match.group(2)
            if obj_name not in name_mapping and obj_name not in reserved_names:
                name_mapping[obj_name] = generate_obfuscated_name()
        
        # 2. 識別函數名和參數
        func_pattern = r'(void|int|float|double|char|bool|byte|COROUTINE)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)'
        func_matches = re.finditer(func_pattern, code_without_comments)
        for match in func_matches:
            func_name = match.group(2)
            if func_name not in name_mapping and func_name not in reserved_names:
                name_mapping[func_name] = generate_obfuscated_name()
            
            # 處理函數參數
            param_str = match.group(3)
            if param_str:
                # 改進的參數匹配，處理各種類型
                param_pattern = r'(?:int|float|double|char|bool|byte|unsigned\s+int)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:,|$)'
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
        var_patterns = [
            r'(const\s+)?(int|float|double|char|bool|byte|static\s+int)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:=|\[|;)',
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
        
        print(f"使用正則表達式方法成功混淆! 結果已寫入 {output_file}")
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