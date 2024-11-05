import re
import shutil
from pathlib import Path

# input
RES_PATH = Path(r"")

INTEND_PATH = Path(__file__).parent / 'INTEND_RES_PATH'
INTEND_PATH.mkdir(exist_ok=True)

RE_MAP = {
    '3d_suit': r'3DSuit[A-Z]{1}[a-z]+[A-Z]{1}[a-z]+.png',
    'camp': r'IconCamp[^#]+.png',
    'mind': r'Mindscape_[0-9]{4}_[0-9]{1}.png',
    'role': r'IconRole[0-9]{2,3}.png',
    'role_circle': r'IconRoleCircle[0-9]{2,3}.png',
    'role_general': r'IconRoleGeneral[0-9]{2,3}.png',
    'suit': r'Suit[A-Z]{1}[a-z]+[A-Z]{1}[a-z]+.png',
    'weapon': r'Weapon_[A-Z]{1}_[0-9]{4}_High.png',
}


def main():
    for k in RE_MAP:
        path = INTEND_PATH / k
        path.mkdir(exist_ok=True)
        pattern = re.compile(RE_MAP[k])
        res = [
            file for file in RES_PATH.rglob("*") if pattern.match(file.name)
        ]
        for i in res:
            output = path / i.name
            shutil.copy(i, output)


if __name__ == '__main__':
    main()
