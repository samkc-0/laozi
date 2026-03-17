#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(
    description="Populate sentence example records with syntax-gloss analogue examples.",
  )
  parser.add_argument(
    "--input",
    default="data/sentence-examples.json",
    help="Path to the sentence record JSON file.",
  )
  parser.add_argument(
    "--output",
    default="data/sentence-examples.json",
    help="Where to write the populated JSON file.",
  )
  return parser.parse_args()


BANKS = {
  "callable": [
    ("茶可茶，非好茶。", "可以叫作茶的，不一定是好茶。", "Tea that can be called tea is not good tea."),
    ("酒可酒，非佳酒。", "可以叫作酒的，不一定是佳酒。", "Wine that can be called wine is not fine wine."),
    ("飯可飯，不足為飽飯。", "能算是飯，還不夠算是一頓真正吃飽的飯。", "Food that counts as food is not enough to be a truly filling meal."),
    ("貓可貓，未為乖貓。", "叫作貓容易，要算乖貓還早。", "A cat may count as a cat, but not yet as a well-behaved cat."),
    ("狗可狗，未必良狗。", "能算狗，不一定就是好狗。", "A dog that counts as a dog is not necessarily a good dog."),
    ("屋可屋，非好屋。", "是屋子，不等於是好住的屋子。", "A house that counts as a house is not a good house."),
    ("床可床，未必好床。", "能算床，不一定好睡。", "A bed that counts as a bed is not necessarily a good bed."),
    ("鞋可鞋，不足為好鞋。", "能穿在腳上，還不夠叫好鞋。", "Shoes that count as shoes are not enough to be good shoes."),
    ("車可車，未為好車。", "能開的車，還不算好車。", "A car that runs is not yet a good car."),
    ("書可書，未必佳書。", "成書容易，成佳書不易。", "A book that counts as a book is not necessarily a fine book."),
    ("網可網，非快網。", "連得上網，不等於網快。", "Internet that counts as internet is not fast internet."),
    ("咖啡可咖啡，未必醒咖啡。", "是咖啡，不一定真提神。", "Coffee that counts as coffee is not necessarily wake-up coffee."),
    ("班可班，不足為好班。", "有課可上，不等於是好班。", "A class that counts as a class is not enough to be a good class."),
    ("店可店，未為好店。", "能開成店，不一定是好店。", "A shop that counts as a shop is not yet a good shop."),
    ("手機可手機，安得為耐用手機。", "只是手機，怎麼就算耐用手機？", "A phone that merely counts as a phone is hardly a durable phone."),
    ("筆可筆，未必好筆。", "能寫字的是筆，不一定是好筆。", "A pen that counts as a pen is not necessarily a good pen."),
    ("桌可桌，非穩桌。", "像桌子，不一定穩當。", "A table that counts as a table is not a steady table."),
    ("門可門，未為好門。", "能開能關，不一定是好門。", "A door that counts as a door is not yet a good door."),
    ("衣可衣，不足為暖衣。", "能穿在身上，還不夠算保暖的衣服。", "Clothes that count as clothes are not enough to be warm clothes."),
    ("路可路，未必平路。", "能走成路，不一定平坦好走。", "A road that counts as a road is not necessarily an easy road."),
  ],
  "contrast": [
    ("甜與苦並，味乃分明。", "甜苦放在一起，味道才更清楚。", "Sweet and bitter placed together make the taste clearer."),
    ("高與下對，勢乃可見。", "有高有下，形勢才看得出來。", "With high and low set against each other, the shape becomes visible."),
    ("長與短較，度乃可知。", "長短一比，尺度才明白。", "When long and short are compared, measure becomes knowable."),
    ("快與慢參，程乃可辨。", "快慢一對照，進度才分得清。", "Set speed against slowness and the pace becomes clear."),
    ("多與少列，數乃自見。", "多和少並排，多少就自己顯出來。", "Place many beside few and quantity shows itself."),
    ("新與舊並，意乃不同。", "新舊一對照，感覺就不一樣。", "New and old side by side create different meaning."),
    ("明與暗分，光乃可覺。", "明暗分開，光感才出來。", "Light is felt more clearly when set against dark."),
    ("近與遠照，路乃成形。", "有近有遠，路的樣子才成。", "Near and far together give shape to the path."),
    ("熱與冷參，氣乃可察。", "冷熱相參，溫度才可察。", "Heat and cold together make temperature noticeable."),
    ("鬆與緊較，力乃可識。", "鬆緊一比，力道才知道。", "Compare loose and tight and the force becomes legible."),
    ("靜與動分，勢乃可名。", "動靜分明，局勢才說得清。", "Stillness and motion set apart make the pattern nameable."),
    ("先與後接，序乃自成。", "前後排開，次序自然出來。", "First and after arranged together make sequence on their own."),
    ("內與外照，界乃可守。", "裡外一照面，界線才守得住。", "Inner and outer define a boundary when they face each other."),
    ("寬與窄並，身乃知處。", "寬窄並看，人才知道怎麼站。", "Wide and narrow together teach the body where to stand."),
    ("重與輕較，手乃知分。", "重輕一拿，手感才分明。", "Weight becomes clear only when heavy and light are compared."),
    ("厚與薄列，材乃可辨。", "厚薄一比，材料就顯出差別。", "Thickness and thinness reveal the material by contrast."),
    ("前與側觀，形乃可成。", "從前面和側面一起看，形體才完整。", "Form emerges when front and side are seen together."),
    ("滿與缺對，意乃更深。", "滿和缺一對著看，意思就更深。", "Fullness and lack deepen meaning when paired."),
    ("直與曲參，路乃不單。", "直曲一起看，路就不是只有一種走法。", "Straight and curved together show that a path is never only one thing."),
    ("軟與硬並，用乃不同。", "軟硬並列，用法自然不同。", "Soft and hard set together show different kinds of use."),
  ],
  "inference": [
    ("天冷，故添衣。", "因為天冷，所以加衣。", "It is cold, therefore add a coat."),
    ("雨近，是以收衣。", "雨快到了，所以收衣服。", "Rain is near, so the clothes are brought in."),
    ("路遠，故早行。", "因為路遠，所以早點出門。", "The road is long, therefore leave early."),
    ("客至，是以掃庭。", "客人要來，所以先掃院子。", "Guests are coming, so the courtyard is swept."),
    ("水急，故緩步。", "水流得急，所以走慢一點。", "The water is swift, therefore walk more carefully."),
    ("鍋熱，是以減火。", "鍋太熱，所以把火轉小。", "The pot is too hot, so the flame is lowered."),
    ("夜深，故閉門。", "夜已深，所以把門關上。", "The night is deep, therefore the door is shut."),
    ("米少，是以省食。", "米不多，所以吃得節省些。", "Rice is scarce, so the meal is made modest."),
    ("人倦，故少言。", "人累了，所以少說話。", "People are tired, therefore speech grows sparse."),
    ("事繁，是以先簡。", "事情多，所以先把它理簡。", "The tasks are many, so one simplifies first."),
    ("風起，故掩窗。", "起風了，所以把窗掩好。", "Wind rises, therefore the window is closed."),
    ("道滑，是以徐行。", "路滑，所以慢慢走。", "The path is slick, so one walks slowly."),
    ("燈暗，故近書。", "燈光暗，所以把書拿近些。", "The lamp is dim, therefore the book is brought closer."),
    ("客多，是以添席。", "客人多，所以多加座位。", "There are many guests, so more seats are added."),
    ("聲雜，故低語。", "聲音雜，所以改用低聲說。", "The place is noisy, therefore one speaks softly."),
    ("飯熟，是以停火。", "飯熟了，所以把火關小或關掉。", "The rice is cooked, so the fire is stopped."),
    ("時晚，故歸。", "時候晚了，所以回去。", "It is late, therefore return."),
    ("紙薄，是以輕寫。", "紙很薄，所以寫字要輕。", "The paper is thin, so the writing must be light."),
    ("人急，故多失。", "人一急，就容易出錯。", "When a person grows hurried, errors follow."),
    ("心定，是以少亂。", "心定下來，所以少亂。", "When the mind is steady, disorder lessens."),
  ],
  "model": [
    ("良師少言，而人自明。", "好老師少說空話，學生反而更明白。", "A good teacher speaks little, and people understand more by themselves."),
    ("善醫不驚，而病自緩。", "好醫者不先嚇人，病人反而安下來。", "A good physician does not alarm first, and the illness settles."),
    ("巧匠不躁，而器自成。", "好工匠不急躁，器物反而成得好。", "A skilled craftsperson is not restless, and the work comes together."),
    ("明主不擾，而事自理。", "明白的領頭人不亂攪，事情反而理順。", "A clear leader does not meddle, and affairs arrange themselves."),
    ("善廚不爭，而味自和。", "好廚子不逞強，味道反而協調。", "A good cook does not compete with the ingredients, and the flavors harmonize."),
    ("佳友不逼，而情自近。", "好朋友不逼迫，感情反而更近。", "A true friend does not press, and closeness grows on its own."),
    ("長者不誇，而眾自服。", "長者不自誇，大家反而服氣。", "An elder who does not boast is trusted more readily."),
    ("善讀不急，而義自出。", "會讀書的人不急著下結論，意思自己會出來。", "A good reader does not rush, and the meaning emerges."),
    ("良農不貪，而田自厚。", "好農人不貪快，田地反而養得厚。", "A good farmer does not grasp too hard, and the field grows rich."),
    ("善商不欺，而客自來。", "好商人不欺人，客人自然回來。", "A good merchant does not cheat, and customers return on their own."),
    ("善工不亂，而序自見。", "做事好的人不亂來，次序自然看得見。", "A capable worker does not move chaotically, and order shows itself."),
    ("善聽不奪，而言自盡。", "會聽的人不搶話，對方自然說完。", "A good listener does not seize the floor, and speech completes itself."),
    ("善寫不飾，而意自真。", "會寫的人不亂裝飾，意思反而更真。", "A good writer does not over-ornament, and the meaning stays true."),
    ("善教不逼，而學自進。", "好教法不硬逼，學習反而前進。", "Good teaching does not force, and learning advances by itself."),
    ("善管不繁，而眾自安。", "好的管理不繁瑣，大家反而安心。", "Good governance is not over-complicated, and people settle."),
    ("善行不喧，而德自見。", "真正做得好的人不喧鬧，品行自己會顯。", "Good action does not need noise; character shows itself."),
    ("善守不閉，而室自安。", "會守的人不死閉，屋裡反而安穩。", "One who guards well does not merely shut things tight, and the house stays safe."),
    ("善帶不拉，而眾自齊。", "會帶人的人不硬拉，大家反而跟得齊。", "A good guide does not drag people along, and the group keeps together."),
    ("善學不滿，而智自長。", "會學的人不自滿，智慧自然增長。", "A good learner does not feel full too soon, and understanding grows."),
    ("善用不耗，而物自久。", "會用東西的人不亂耗，東西自然耐久。", "To use things well is not to exhaust them, and so they last."),
  ],
  "negation": [
    ("飯不香，未必不可食。", "飯不香，不代表不能吃。", "Rice that is not fragrant is not therefore inedible."),
    ("門不新，未為不好門。", "門不新，不等於不是好門。", "A door that is not new is not therefore a bad door."),
    ("衣不華，未必不暖。", "衣服不華麗，不一定不保暖。", "Clothes that are not fancy are not necessarily not warm."),
    ("店不大，未必不佳。", "店面不大，不一定不好。", "A shop that is not large is not necessarily not good."),
    ("字不多，未為無意。", "字不多，不等於沒有意思。", "Few words do not mean no meaning."),
    ("路不平，未必不通。", "路不平，也不一定不能走。", "A road that is uneven is not therefore impassable."),
    ("杯不滿，未必不足。", "杯子沒滿，不一定就不夠。", "A cup not filled to the brim is not necessarily insufficient."),
    ("屋不高，未為不安。", "屋子不高，不代表住得不安。", "A house that is not tall is not therefore uncomfortable."),
    ("人不語，未必無心。", "人不說話，不一定沒有心意。", "A person who does not speak is not necessarily without feeling."),
    ("茶不濃，未必不醒。", "茶不濃，不一定不能提神。", "Tea that is not strong is not necessarily not refreshing."),
    ("書不厚，未必不深。", "書不厚，不一定不深。", "A book that is not thick is not necessarily shallow."),
    ("車不快，未必不達。", "車不快，不代表到不了。", "A car that is not fast still may arrive."),
    ("人不先，未為不成。", "不搶先，不等於做不成。", "Not being first does not mean failure."),
    ("聲不高，未必不聞。", "聲音不高，不一定聽不到。", "A low voice is not necessarily unheard."),
    ("屋不寬，未必不居。", "屋子不寬，也還是能住。", "A narrow house may still be livable."),
    ("筆不貴，未必不善。", "筆不貴，不一定不好寫。", "A pen that is not expensive is not necessarily poor."),
    ("人不忙，未為無功。", "看起來不忙，不等於沒有做事。", "Someone who does not look busy is not therefore unproductive."),
    ("光不強，未必不明。", "光不強，不一定不夠看。", "Light that is not harsh may still be clear enough."),
    ("言不多，未為無見。", "話不多，不代表沒有見地。", "Few words do not mean no insight."),
    ("步不疾，未必不遠。", "走得不快，不一定走不遠。", "To walk without haste does not mean one cannot go far."),
  ],
  "question": [
    ("茶可茶，豈好茶。", "只是叫作茶，怎麼就算好茶？", "Tea that barely counts as tea — how could it already be good tea?"),
    ("酒可酒，安得為佳酒。", "只是酒，怎麼就叫佳酒？", "Wine that merely counts as wine — how could it be fine wine?"),
    ("飯可飯，何為佳飯。", "只是能吃的飯，怎麼就算佳飯？", "A meal that merely counts as food — why call it a fine meal?"),
    ("屋可屋，豈安屋。", "只是屋子，怎麼就說住得安？", "A house that barely counts as a house — how could it already be comfortable?"),
    ("車可車，安得為快車。", "只是能開的車，怎麼就叫快車？", "A vehicle that merely runs — how could it be a fast car?"),
    ("書可書，何為佳書。", "只是成書，怎麼就算佳書？", "A text that merely counts as a book — why call it a fine book?"),
    ("筆可筆，豈妙筆。", "只是筆，怎麼就成妙筆？", "A pen that is merely a pen — how could it already be a marvelous pen?"),
    ("店可店，安得為好店。", "只是開成店，怎麼就叫好店？", "A place that merely counts as a shop — how could it already be a good shop?"),
    ("鞋可鞋，何為佳鞋。", "只是鞋子，怎麼就算佳鞋？", "Shoes that merely count as shoes — why call them fine shoes?"),
    ("網可網，豈快網。", "只是上得去的網，怎麼就算快網？", "Internet that merely connects — how could it be fast internet?"),
    ("課可課，安得為好課。", "只是有課，怎麼就叫好課？", "A class that merely exists — how could it already be a good class?"),
    ("床可床，何為好床。", "只是能睡，怎麼就算好床？", "A bed that merely serves as a bed — why call it a good bed?"),
    ("屋可屋，安得為久屋。", "只是房子，怎麼就算耐住？", "A house that merely stands — how could it already be long-lasting?"),
    ("友可友，豈知己。", "只是朋友，怎麼就算知己？", "A friend is a friend — how could every friend be a soulmate?"),
    ("學可學，安得為深學。", "只是學過，怎麼就算學得深？", "To have studied at all — how could that alone count as deep learning?"),
    ("行可行，何為遠行。", "只是能走，怎麼就算遠行？", "To be able to walk — why call it a long journey already?"),
    ("聲可聲，豈妙音。", "只是有聲，怎麼就算妙音？", "A sound is a sound — how could it already be beautiful music?"),
    ("字可字，安得為好字。", "只是成字，怎麼就算好字？", "Writing that merely forms characters — how could it already be good writing?"),
    ("門可門，何為名門。", "只是有門，怎麼就算名門？", "A gate is a gate — why call it a distinguished house?"),
    ("名可名，安得為真名。", "只是叫得出來，怎麼就算真名？", "A name that can be spoken — how could it already be the true name?"),
  ],
  "chain": [
    ("生而不奪，成而不居。", "讓它生，也不搶它；讓它成，也不居功。", "Let it arise without seizing it; let it succeed without claiming it."),
    ("作而不擾，成而不誇。", "做事，但不亂擾；做成，也不誇口。", "Act without disturbing; complete without boasting."),
    ("看而不取，聞而不爭。", "看見了，不急著拿；聽見了，不急著爭。", "See without grabbing; hear without competing."),
    ("行而不逼，止而不怠。", "該走就走，但不逼迫；該停就停，也不懶散。", "Move without pressing; stop without collapsing."),
    ("教而不壓，引而不拖。", "教人但不壓人，引人但不硬拖。", "Teach without pressing down; guide without dragging."),
    ("守而不閉，用而不盡。", "守住它，但不死閉；使用它，但不耗盡。", "Guard without sealing shut; use without exhausting."),
    ("取而不貪，與而不誇。", "拿的時候不貪，給的時候不誇。", "Take without greed; give without display."),
    ("居而不滿，退而不失。", "在位不自滿，退下也不失分寸。", "Dwell without self-satisfaction; withdraw without losing measure."),
    ("進而不猛，緩而不廢。", "前進不猛撞，放慢也不荒廢。", "Advance without charging; slow down without neglecting."),
    ("知而不露，明而不耀。", "知道，但不急著露出來；明白，也不刺眼。", "Know without showing off; be clear without dazzling."),
    ("蓄而不塞，發而不傷。", "積蓄，但不堵死；發出，也不傷人。", "Store without blockage; release without harm."),
    ("問而不窮，答而不滿。", "發問但不逼死，回答也不說滿。", "Ask without cornering; answer without overfilling the claim."),
    ("得而不恃，失而不亂。", "得到了，不倚仗；失去了，也不亂。", "Gain without depending on it; lose without falling into disorder."),
    ("近而不狎，遠而不絕。", "靠近，但不輕慢；拉遠，也不斷絕。", "Come near without becoming careless; stand far without breaking off."),
    ("視而不執，聽而不隨。", "看見了不死抓，聽到了不亂跟。", "See without clinging; hear without blindly following."),
    ("為而不重，止而不空。", "做事不把自己壓得太重，停下也不是空掉。", "Act without overburdening; stop without emptiness."),
    ("收而不吝，放而不散。", "收住，但不小氣；放開，也不散亂。", "Gather without stinginess; release without scattering."),
    ("養而不縱，裁而不傷。", "養護但不放縱，裁減但不傷根。", "Nourish without indulgence; trim without damaging the root."),
    ("成而不據，久而不倦。", "做成了，不占住不放；做久了，也不疲於炫耀。", "Accomplish without occupying; continue without weariness of self-display."),
    ("興而不驕，衰而不亂。", "興起時不驕，衰下來也不亂。", "Rise without arrogance; decline without chaos."),
  ],
  "generic": [
    ("店有店樣，人有人情。", "店有店的樣子，人有人情味。", "A shop has the form of a shop; a person has human feeling."),
    ("飯有飯香，茶有茶味。", "飯有飯的香，茶有茶的味。", "Rice has the smell of rice; tea has the taste of tea."),
    ("書有書氣，字有字骨。", "書有書卷氣，字有字的骨架。", "A book has bookish air; writing has its own backbone."),
    ("門有門向，窗有窗光。", "門有開向，窗有採光。", "A door has its opening; a window has its light."),
    ("衣有衣裁，屋有屋勢。", "衣有剪裁，屋有格局。", "Clothing has its cut; a house has its structure."),
    ("車有車路，人有人步。", "車有車走的路，人有人走的步。", "Cars have car-roads; people have human steps."),
    ("山有山色，水有水聲。", "山有山的顏色，水有水的聲音。", "Mountains have mountain-color; water has water-sound."),
    ("筆有筆意，墨有墨性。", "筆有筆意，墨有墨的性情。", "The brush has its gesture; ink has its own nature."),
    ("課有課法，學有學程。", "課有教法，學有進程。", "Classes have their methods; learning has its pace."),
    ("市有市聲，夜有夜靜。", "白天有市聲，夜裡有夜靜。", "The market has its noise; the night has its stillness."),
    ("屋有屋影，燈有燈圈。", "屋子有影子，燈光有一圈光。", "A house has its shadows; a lamp has its circle of light."),
    ("雨有雨腳，風有風路。", "雨有雨線，風也有風走的路。", "Rain has its falling lines; wind too has its path."),
    ("人有人氣，器有器用。", "人有人的氣息，器有器的用處。", "People have human presence; tools have use."),
    ("茶有茶候，酒有酒性。", "泡茶有火候，喝酒有酒性。", "Tea has its proper timing; wine has its own tendency."),
    ("木有木理，石有石紋。", "木頭有紋理，石頭有紋路。", "Wood has grain; stone has veining."),
    ("遠有遠意，近有近情。", "遠有遠看的意思，近有近看的情味。", "Distance has one meaning; nearness has another feeling."),
    ("手有手感，眼有眼力。", "手有手感，眼有眼光。", "Hands have touch; eyes have discernment."),
    ("早有早光，晚有晚色。", "早晨有早晨的光，傍晚有傍晚的顏色。", "Morning has morning light; evening has evening color."),
    ("舊有舊味，新有新意。", "舊東西有舊味，新東西有新意。", "Old things have old flavor; new things have new intention."),
    ("動有動勢，靜有靜心。", "動的時候有動勢，靜的時候有靜心。", "Motion has its momentum; stillness has its own mind."),
  ],
}


def detect_pattern(sentence: str) -> str:
  if re.search(r"(.{1,3})可\1", sentence):
    return "callable"
  if any(marker in sentence for marker in ["乎", "孰", "何", "安得", "豈"]):
    return "question"
  if sentence.startswith(("故", "是以", "是故", "故常", "故有")):
    return "inference"
  if "聖人" in sentence:
    return "model"
  if sentence.count("而") >= 1 and sentence.count("，") >= 1:
    return "chain"
  if ("無" in sentence and "有" in sentence) or sentence.count("相") >= 2:
    return "contrast"
  if "不" in sentence or "無" in sentence or "弗" in sentence:
    return "negation"
  return "generic"


def main() -> int:
  args = parse_args()
  input_path = Path(args.input)
  output_path = Path(args.output)

  records = json.loads(input_path.read_text(encoding="utf-8"))
  if not isinstance(records, list):
    raise ValueError(f"{input_path} must contain a list of sentence records.")

  populated = []
  for record in records:
    sentence = record.get("sentence")
    if not isinstance(sentence, str):
      raise ValueError("Each record must contain a string 'sentence' field.")

    examples = [
      {"wenyan": wenyan, "zh": zh, "en": en}
      for wenyan, zh, en in BANKS[detect_pattern(sentence)]
    ]
    populated.append({**record, "examples": examples})

  output_path.write_text(
    json.dumps(populated, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
  )
  print(f"records: {len(populated)}")
  print(f"examples_per_record: {len(populated[0]['examples']) if populated else 0}")
  print(f"output: {output_path}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
