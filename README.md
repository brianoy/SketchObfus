# SketchObfus
Just scrambles your arduino code variable names to make the code harder to read. Focused on what it does best: making things slightly uglier.

| before | after |
|:------------:|:-------------:|
| <img src="https://github.com/user-attachments/assets/414e6332-f762-4df6-8566-de5236304770" width = "90%">|<img src="https://github.com/user-attachments/assets/d35a7f1d-9488-4be3-93a8-e6e2f5d5d684" width = "90%">|

## 🔧 Features

- Removes both C-style (`/* */`) and C++-style (`//`) comments
- Obfuscates:
  - Global and local variables
  - Function names
  - Function parameters
  - Object instances (e.g., `Servo myServo;`)
- Ignores Arduino reserved keywords and function names
- Outputs clean, comment-free obfuscated code

## 📦 Requirements

- Python 3.13

## 🚀 Usage

1. Clone this project

```bash
git clone https://github.com/brianoy/SketchObfus.git
```

2. Start obfuscated

```bash
python SketchObfus.py your_sketch.ino
```

This generates an obfuscated version of the sketch named `your_sketch_obf.ino`.

You can also specify a custom output filename:

```bash
python SketchObfus.py your_sketch.ino obfuscated_output.ino
```

## 📁 Example

Before:
```cpp
int ledPin = 13;
void setup() {
  pinMode(ledPin, OUTPUT);
}
void loop() {
  digitalWrite(ledPin, HIGH);
  delay(1000);
  digitalWrite(ledPin, LOW);
  delay(1000);
}
```

After:
```cpp
int _0xA3B1C2D4 = 13;
void _0x1F9A3B7C() {
  pinMode(_0xA3B1C2D4, OUTPUT);
}
void _0x6D9C7A2E() {
  digitalWrite(_0xA3B1C2D4, HIGH);
  delay(1000);
  digitalWrite(_0xA3B1C2D4, LOW);
  delay(1000);
}
```

## 🛡️ Limitations

- Not suitable for sketches that rely on external macro-generated names or dynamically referenced variables.
- Does not analyze code semantically — relies solely on regex patterns.
