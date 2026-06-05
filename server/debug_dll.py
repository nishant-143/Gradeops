import ctypes
import os
import sys

dll_path = r'D:\Programming\GradeOps\gradeOps\server\venv\Lib\site-packages\cryptography\hazmat\bindings\_rust.pyd'

print(f"Checking if file exists: {os.path.exists(dll_path)}")

# Filter PATH to remove other Python installations
new_path = []
for p in os.environ['PATH'].split(';'):
    if 'C:\\Python' not in p and 'Python310' not in p:
        new_path.append(p)
os.environ['PATH'] = ';'.join(new_path)

print("\nIsolated PATH (no other Pythons):")
for p in os.environ['PATH'].split(';'):
    if 'Python' in p:
        print(p)

try:
    if hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(r'D:\Python')
    print("\nAttempting to load with WinDLL...")
    ctypes.WinDLL(dll_path)
    print("Success!")
except Exception as e:
    print(f"Failed to load: {e}")
