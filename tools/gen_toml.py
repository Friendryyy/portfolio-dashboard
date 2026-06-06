import json

print("วาง path ของไฟล์ JSON Service Account แล้วกด Enter:")
path = input("> ").strip().strip('"')

with open(path, encoding="utf-8") as f:
    d = json.load(f)

print("\n" + "="*60)
print("คัดลอกข้อความด้านล่างทั้งหมดไปวางใน Streamlit Secrets:")
print("="*60 + "\n")

print("[gcp_service_account]")
for k, v in d.items():
    if k == "private_key":
        print(f'private_key = """{v}"""')
    else:
        print(f'{k} = "{v}"')

print("\n" + "="*60)
input("\nกด Enter เพื่อปิด...")
