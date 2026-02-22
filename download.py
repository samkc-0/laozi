from ctext import *
import json

urn = "ctp:dao-de-jing"

laozi = gettextasparagraphlist(urn)

with open("laozi.json", "w") as f:
    json.dump(laozi, f, ensure_ascii=False)

print(laozi)
