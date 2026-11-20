"""Builds jobs.json: one Higgsfield job per image the İrisya site needs.

Models (cheapest models that still look premium, ~0.12 credits each at 2k):
  text2image_soul_v2 (people), soul_cinematic (eye macros, clinical scenes), soul_location (places, no people)
"""
import json
from pathlib import Path

SOUL, CINE, LOC = "text2image_soul_v2", "soul_cinematic", "soul_location"

LOOK = ("Premium editorial photography for a luxury ophthalmology clinic in Istanbul. Natural, realistic skin texture, "
        "soft flattering daylight, calm and refined mood, subtle cool navy and ice-blue colour grading. "
        "No text, no watermark, no logos.")
EYES = "The eyes are sharp and in focus and the iris colour is clearly visible, natural and believable, not glowing, not contact-lens-like."
CLINIC = ("Modern minimalist eye clinic interior: white walls, pale ice-blue and deep navy accents, light oak details, "
          "spotless and calm, large windows with soft daylight. No text, no logos, no watermark.")

SHADES = {
    1: ("Glacier Blue", "pale icy blue, almost silver-blue, very light"),
    2: ("Bosphorus Blue", "clear bright medium blue like the Bosphorus on a sunny day"),
    3: ("Sapphire", "a deep, rich sapphire blue: dark saturated royal-navy blue, clearly blue, not grey"),
    4: ("Silver Grey", "cool soft silver grey with a faint blue cast"),
    5: ("Aegean Green", "blue-green aqua, like shallow Aegean sea water"),
    6: ("Emerald", "emerald green with small amber flecks around the pupil"),
    7: ("Hazel", "hazel, green-brown with a golden amber centre"),
    8: ("Honey", "warm honey amber, light golden brown"),
}
# a different person behind each shade's daylight eye photo
SHADE_PEOPLE = {
    1: "a fair-skinned woman in her late 20s with light brown brows",
    2: "a woman in her 30s with light olive skin and dark brows",
    3: "a man in his 30s with fair skin and dark brows",
    4: "a man in his 40s with fair skin and ash-brown brows",
    5: "a woman in her 30s with tanned skin and dark brown brows",
    6: "a woman in her 20s with warm beige skin and auburn brows",
    7: "a woman in her 30s with medium olive skin and dark brows",
    8: "a woman in her 30s with light brown skin and black brows",
}

jobs = []


def add(name, model, prompt, ar, quality="2k", **kw):
    j = {"name": name, "model": model, "prompt": prompt, "aspect_ratio": ar}
    if model != LOC:
        j["quality"] = quality
    j.update(kw)
    jobs.append(j)


# ---------- Patient stories (portrait 3:4) + Istanbul moment (polaroid, 3:4 → 4:5) ----------
stories = {
    1: ("a woman in her early 30s from Dubai, warm olive skin, dark glossy hair loosely tied back, soft natural makeup, "
        "elegant cream linen blouse, standing on a sunlit stone terrace with softly blurred warm terracotta rooftops behind her", 7,
        "with long dark hair, walking along a cobbled Beyoğlu street at sunset with the round cylindrical medieval stone Galata Tower and its pointed conical grey roof rising behind her, warm golden light, candid travel photo, seen from three-quarter behind, wearing sunglasses pushed up in her hair"),
    2: ("a British woman in her late 20s from London, fair skin with light freckles, honey-blonde shoulder-length hair, "
        "minimal makeup, soft white knit top, sitting by a large window in an elegant hotel suite in Istanbul", 1,
        "with honey-blonde shoulder-length hair, standing in the courtyard in front of the Blue Mosque in Istanbul, wearing sunglasses and a light scarf over her shoulders, bright morning light, candid travel photo"),
    3: ("a Romanian man in his mid 30s from Bucharest, fair skin, short dark-brown hair, neatly trimmed stubble, "
        "navy crew-neck sweater over a white T-shirt, standing in a bright modern hotel lobby in Istanbul", 4,
        "stepping into the back seat of a black luxury Mercedes V-Class van held open by a chauffeur in a dark suit outside Istanbul Airport, candid travel photo, daylight"),
    4: ("a German woman in her early 30s from Berlin, light skin, straight chestnut-brown hair tucked behind her ears, "
        "light grey blazer over a white top, standing in a calm Istanbul hotel garden with soft green foliage behind her", 6,
        "relaxing on a sun lounger beside a luxury hotel infinity pool overlooking the Bosphorus, wearing sunglasses and a white robe, calm afternoon light, candid travel photo"),
    5: ("a Canadian woman in her mid 30s from Toronto, light skin, long wavy light-brown hair, natural makeup, "
        "camel trench coat over a black top, standing on a waterfront promenade with softly blurred calm blue water behind her", 2,
        "leaning on the railing of a waterfront terrace on the Bosphorus at dusk, warm city lights and a lit mosque dome softly blurred behind her, wearing sunglasses on her head, candid travel photo"),
}
for i, (who, shade, moment) in stories.items():
    sname, sdesc = SHADES[shade]
    add(f"story-{i}", SOUL,
        f"Head-and-shoulders editorial portrait photograph of {who}. She looks straight into the camera with a calm, quietly confident smile. "
        .replace("She looks", "He looks" if i == 3 else "She looks")
        + f"Her eyes are {sdesc}. ".replace("Her eyes", "His eyes" if i == 3 else "Her eyes")
        + EYES + " 85mm lens, shallow depth of field, face in the upper half of the frame. " + LOOK, "3:4")
    add(f"moment-{i}", SOUL,
        f"Candid holiday photo of " + who.split(",")[0] + f", {moment}. Natural, happy, relaxed travel moment in Istanbul, Turkey, the face is small in the frame. " + LOOK,
        "3:4")

# ---------- Review avatars (1:1 headshots) ----------
reviewers = [
    "a woman in her early 30s from Ireland with fair freckled skin, copper-red hair and pale icy blue eyes",
    "a woman in her late 20s from Kuwait wearing an elegant beige silk hijab, warm light-brown skin and soft light-brown eyes",
    "a British man in his mid 40s with fair skin, short greying hair, light stubble and cool silver-grey eyes",
    "a Romanian man in his early 30s with fair skin, short black hair and natural medium-blue eyes",
    "a French woman in her early 30s with light skin, a dark-brown bob haircut and blue-green aqua eyes",
    "an American man in his early 50s with tanned skin, salt-and-pepper hair, a warm smile and deep sapphire blue eyes",
    "an Italian woman in her late 20s with olive skin, long dark wavy hair and natural soft green eyes",
    "a woman in her 30s from Qatar wearing a black shayla headscarf, warm olive skin and hazel green-brown eyes",
    "a Dutch woman in her late 20s with fair skin, straight blonde hair and light amber-brown eyes",
]
for i, who in enumerate(reviewers, 1):
    add(f"review-{i}", SOUL,
        f"Friendly close-up headshot of {who}, smiling naturally at the camera, face centred and filling most of the square frame, "
        "plain softly blurred bright background, natural realistic eyes, both eyes the same colour. " + LOOK, "1:1")

# ---------- Team ----------
add("team-1", SOUL,
    "Professional headshot of a Turkish male ophthalmologist in his late 40s, short dark hair greying at the temples, clean-shaven, "
    "kind confident expression, crisp white doctor's coat over a navy shirt, inside a bright modern eye clinic, face centred in the upper half of the square frame. "
    + LOOK, "1:1")
add("team-2", SOUL,
    "Professional headshot of a Turkish woman in her early 30s working as an international patient coordinator, warm welcoming smile, "
    "dark hair in a neat low bun, tailored navy blazer over a white blouse, small earpiece, bright modern clinic lobby behind her, face centred in the frame. "
    + LOOK, "1:1")
add("team-3", SOUL,
    "Professional headshot of a Turkish woman in her late 20s who designs eye-colour shades, light lab coat over a soft grey top, "
    "dark wavy shoulder-length hair, thoughtful friendly smile, softly blurred colour swatches behind her, face centred in the frame. "
    + LOOK, "1:1")

# ---------- Why İrisya (2:3 portrait, eyes at ~1/3 height) ----------
add("why", SOUL,
    "Beauty editorial portrait of a woman in her late 20s with light olive skin, sleek dark hair pulled back, minimal makeup and small gold earrings, "
    "facing the camera with a serene expression. Her eyes are hazel, green-brown with a golden amber centre, positioned in the upper third of the frame. "
    + EYES + " Soft window light, clean pale ice-blue background, shoulders and a white silk top visible. " + LOOK, "2:3")

# ---------- Journey (16:9 → 2:1; chat bubbles sit on the left, keep the subject on the right) ----------
LEFT = " Composition: the main subject sits in the right half of the frame; the left half is calm, softly out of focus negative space."
add("journey-1", CINE,
    "Side view of a young woman with natural brown eyes standing next to a bright window in the right third of the frame, holding up her smartphone "
    "to take a daylight close-up photo of her own eye, calm and curious expression. The left half of the frame is a softly blurred bright white wall with soft daylight. "
    "Real photograph, no graphic panels, no text, no logos.", "16:9")
add("journey-2", SOUL,
    "A professional chauffeur in a dark tailored suit waiting in the bright modern arrivals hall of Istanbul Airport, holding a small blank white welcome card, "
    "polite smile, travellers softly blurred in the background, a black luxury car visible through the glass facade." + LEFT + " " + LOOK, "16:9")
add("journey-3", CINE,
    "An ophthalmologist in a white coat examining a female patient's eyes with a slit lamp microscope in a modern eye clinic, the patient rests her chin on the chin rest, "
    "calm and reassuring atmosphere. " + CLINIC + LEFT, "16:9")
add("journey-4", CINE,
    "A pristine modern ophthalmic procedure room with a femtosecond laser system and a white reclining patient bed under soft overhead light, nobody in the room, "
    "medical equipment arranged neatly, everything ready for a patient. " + CLINIC + LEFT, "16:9")
add("journey-5", SOUL,
    "A woman wearing large dark sunglasses and a light travel outfit at the panoramic window of a modern airport departure lounge at golden hour, "
    "a carry-on suitcase beside her, an airliner on the tarmac outside, she smiles calmly, happy to be going home." + LEFT + " " + LOOK, "16:9")

# ---------- Istanbul places ----------
add("riders", LOC,
    "Istanbul skyline at golden hour seen from a rooftop in Beyoğlu: the Galata Tower in the foreground, the Golden Horn and historic mosques with minarets behind, "
    "warm soft light, gentle haze, elegant travel photography, vertical composition, no text, no people.", "2:3")
add("vision-bg", LOC,
    "Wide panoramic view of the Bosphorus strait in Istanbul on a clear calm morning, historic wooden Ottoman waterfront mansions and green hills along the shore, soft pale blue sky, "
    "light airy atmosphere, travel photography, no text, no people.", "16:9")
add("footer", LOC,
    "Istanbul at blue hour seen from the water: the large illuminated Süleymaniye and New Mosque domes and minarets with the old town skyline fill the lower third of the frame, "
    "warm golden lights reflected in calm Bosphorus water, a deep navy blue-hour sky with soft gradient filling the upper half of the frame, elegant cinematic travel photography, no text, no people.", "21:9")
add("footer-portrait", LOC,
    "Vertical view of Istanbul at blue hour: the large illuminated Galata Tower and old town rooftops fill the lower half of the frame, warm city lights, "
    "a deep navy blue-hour sky filling the upper half, elegant cinematic travel photography, no text, no people.", "3:4")
add("clinic", LOC,
    "Reception area of a luxury eye clinic in Istanbul: a curved white reception desk with light oak details, deep navy lounge chairs, soft pendant lights, "
    "fresh white orchids, large windows with a softly blurred view of the Bosphorus, bright and calm, architectural interior photography, no text, no logos, no people.", "16:9")
add("package-hotel", LOC,
    "Elegant five-star hotel room in Istanbul with a king-size bed in crisp white linen, navy and cream accents, floor-to-ceiling windows overlooking the Bosphorus, "
    "soft morning light, luxury interior photography, no text, no people.", "16:9")
add("package-transfer", LOC,
    "A black luxury Mercedes V-Class van parked at the curb of a modern airport terminal in Istanbul, clean glass facade, soft daylight, "
    "premium chauffeur service photography, no text, no license plate text, no people.", "16:9")

# ---------- Procedure visuals ----------
add("package-procedure", CINE,
    "Macro photograph of a human eye with a clear bright blue iris, a faint ring of light around the iris suggesting precise laser treatment, "
    "clean clinical blue lighting, high-end medical photography. " + EYES + " No text.", "16:9")
add("bento-procedure", CINE,
    "A hand holding a fanned-out deck of round iris colour shade sample cards in icy blue, bright blue, grey, aqua, green, hazel and honey tones, "
    "clean pale ice-blue background, soft daylight, shallow depth of field, premium clinic aesthetic, no text, no numbers.", "16:9")
add("bento-aftercare", SOUL,
    "A woman at home on a sofa in soft daylight, wearing comfortable clothes, smiling as she takes a follow-up photo of her eyes with her smartphone to send to her clinic, "
    "a pair of sunglasses and eye drops on the coffee table, cosy calm mood, her face in the upper part of the frame. " + LOOK, "3:2")
add("tx-1", CINE,
    "An ophthalmic surgeon in navy scrubs, surgical cap and mask performing laser keratopigmentation at a femtosecond laser system, the patient lies calmly on the treatment bed, "
    "focused precise atmosphere, cool clinical light. " + CLINIC, "4:3")
add("tx-2", CINE,
    "Close-up of a patient seated at an ophthalmic laser with her chin on the chin rest while a doctor adjusts the device, soft cool blue clinical light, "
    "precise calm atmosphere, shallow depth of field. " + CLINIC, "4:3")
add("tx-3", CINE,
    "Elegant flat lay on a pale ice-blue surface: rows of small glass pigment vials and round iris-colour shade discs in icy blue, bright blue, sapphire, silver grey, "
    "aqua green, emerald, hazel and honey tones, a fine brush and a magnifier, premium laboratory aesthetic, soft daylight, no text, no labels.", "4:3")
add("tx-4", CINE,
    "Close-up photograph of a young woman's face cropped from the brows to the nose, both eyes open and looking at the camera, she has heterochromia: "
    "her left eye is dark brown and her right eye is light blue. Natural skin, soft daylight, clean neutral background. " + EYES + " No text.", "4:3")
add("tx-4-after", "gpt_image_2_6",
    "Edit this photo: change only the iris of the brown eye (on the left side of the image) to exactly the same light blue colour and texture as the other eye, "
    "so both eyes match in one natural light blue shade. Keep the face, skin, lashes, brows, lighting, framing and everything else identical. Photorealistic, no text.",
    "4:3", quality="medium", image="tx-4.png", extra={"resolution": "2k"})
add("tx-1-detail", CINE,
    f"Macro close-up of a single human eye with a {SHADES[2][1]} iris, eyelashes and part of the brow visible, soft daylight. " + EYES + " No text.", "3:4")
add("tx-2-detail", CINE,
    "Macro close-up of a single human eye with a natural dark brown iris, eyelashes and part of the brow visible, soft daylight. " + EYES + " No text.", "3:4")
add("tx-3-detail", CINE,
    "Close-up of gloved hands blending a hazel and honey coloured mineral pigment on a small glass palette with a fine spatula, soft daylight, laboratory precision, no text.", "3:4")
add("send-photos", CINE,
    "Wide daylight close-up photograph of a woman's single eye centred in the frame, natural medium-brown iris, soft window light, no flash, no contact lenses, "
    "natural skin and lashes, clean and sharp, like a reference photo sent to a clinic. " + EYES + " No text.", "21:9")

# ---------- Shade library: daylight eye photo + iris fibre macro per shade ----------
for i, (sname, sdesc) in SHADES.items():
    add(f"shade-{i}", CINE,
        f"Daylight close-up photograph of the eye area of {SHADE_PEOPLE[i]}, one eye and brow centred in the frame, the iris is {sdesc}. "
        "Soft window light, natural lashes and skin texture. " + EYES + " No text.", "16:9")
    add(f"shade-{i}-detail", CINE,
        f"Extreme macro photograph of a human iris filling the frame, the iris is {sdesc}, intricate radial fibres, crypts and texture in sharp detail, "
        "small dark pupil in the centre, a soft catchlight, natural photographic look, high-end macro photography. No text.", "16:9")

# ---------- Social share image ----------
add("og", CINE,
    "Cinematic close-up of a woman's eye with a clear bright blue iris on the right side of the frame, the left side of the frame fades into deep navy darkness, "
    "elegant premium beauty campaign image, soft rim light. " + EYES + " No text.", "16:9")

Path(__file__).with_name("jobs.json").write_text(json.dumps(jobs, indent=1, ensure_ascii=False), encoding="utf-8")
print(len(jobs), "jobs")
